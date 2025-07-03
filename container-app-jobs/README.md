# Container Apps Jobs - バッチアプリケーション

このアプリケーションは、Azure Container Apps Jobsで実行されるバッチジョブです。開始時と終了時にログを出力し、Azure Monitor OpenTelemetryを使用してApplication Insightsにテレメトリを送信します。

## 使用ライブラリ

- **azure-monitor-opentelemetry**: Application Insightsへのログ・テレメトリ送信（OpenTelemetryベース）
- opencensusは非推奨のため、最新のAzure Monitor OpenTelemetryライブラリを使用

## ファイル構成

- `app.py`: 基本版（ログのみ）
- `app_with_tracing.py`: トレース機能付きバージョン（より詳細なテレメトリ）
- `requirements.txt`: 基本版用の依存関係
- `requirements_with_tracing.txt`: トレース機能付きバージョン用の依存関係

## 必要な環境変数

### Application Insights
```
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=your-instrumentation-key;IngestionEndpoint=https://your-region.in.applicationinsights.azure.com/;LiveEndpoint=https://your-region.livediagnostics.monitor.azure.com/
```

## Azure Container Apps Jobsでの設定例

### 1. Container Apps Environmentの作成
```bash
az containerapp env create \
  --name myenv \
  --resource-group myResourceGroup \
  --location eastus
```

### 2. Application Insightsリソースの作成
```bash
az monitor app-insights component create \
  --app myapp-insights \
  --location eastus \
  --resource-group myResourceGroup
```

### 3. Container Apps Jobの作成
```bash
az containerapp job create \
  --name mybatchjob \
  --resource-group myResourceGroup \
  --environment myenv \
  --trigger-type Manual \
  --replica-timeout 300 \
  --replica-retry-limit 1 \
  --replica-completion-count 1 \
  --parallelism 1 \
  --image myregistry.azurecr.io/mybatchjob:latest \
  --env-vars APPLICATIONINSIGHTS_CONNECTION_STRING=secretref:appinsights-connection-string
```

### 4. Secretの設定
```bash
az containerapp job secret set \
  --name mybatchjob \
  --resource-group myResourceGroup \
  --secrets appinsights-connection-string="YOUR_CONNECTION_STRING"
```

## Dockerコンテナの構築と実行

### ローカルでのテスト
```bash
# Dockerイメージの構築
docker build -t mybatchjob .

# ローカルでの実行（Application Insights無し）
docker run mybatchjob

# ローカルでの実行（Application Insights有り）
docker run -e APPLICATIONINSIGHTS_CONNECTION_STRING="your-connection-string" mybatchjob
```

## Application Insightsでのログ確認

Application Insightsポータルで以下のKQLクエリを使用してログを確認できます：

### ログの確認
```kql
traces
| where message contains "バッチ処理"
| order by timestamp desc
```

### トレース機能付きバージョンの場合（dependencies テーブル）
```kql
dependencies
| where name == "batch_job"
| extend duration_seconds = customDimensions.["job.duration_seconds"]
| order by timestamp desc
```

### カスタム属性での検索（トレース機能付きバージョン）
```kql
dependencies
| where customDimensions.["job.type"] == "batch_job"
| extend 
    phase = customDimensions.["job.phase"],
    duration = customDimensions.["job.duration_seconds"]
| order by timestamp desc
```
