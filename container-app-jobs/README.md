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

### バッチ処理設定
```
SLEEP_SECONDS=30  # 待機時間（秒）
```

### Container Apps環境での推奨設定（オプション）
```
CONTAINER_NAME=my-batch-job  # コンテナ名
REPLICA_NAME=replica-1       # レプリカ名（自動生成も可能）
```

## レプリカ識別機能

このアプリケーションは以下の情報を使用してレプリカを識別します：

- **REPLICA_ID**: UUIDベースの一意識別子（自動生成）
- **HOSTNAME**: コンテナのホスト名
- **PROCESS_ID**: プロセスID
- **CONTAINER_NAME**: 環境変数から取得
- **REPLICA_NAME**: 環境変数から取得（未設定時は自動生成）

これらの情報は：
- ログメッセージのフォーマットに含まれる
- Application Insightsのカスタム属性として送信される
- OpenTelemetryトレースの属性として記録される

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

## Application Insightsでのレプリカ識別

Application Insightsポータルで以下のKQLクエリを使用してレプリカ別のログを確認できます：

### レプリカ別のログ確認
```kql
traces
| where message contains "バッチ処理"
| extend replica_name = customDimensions.replica_name
| extend replica_id = customDimensions.replica_id
| extend hostname = customDimensions.hostname
| order by timestamp desc
| project timestamp, message, replica_name, replica_id, hostname
```

### レプリカ別の実行時間確認
```kql
traces
| where message contains "実行時間"
| extend 
    replica_name = customDimensions.replica_name,
    duration_seconds = customDimensions.duration_seconds
| order by timestamp desc
| project timestamp, replica_name, duration_seconds
```

### Dependencies（トレース）でのレプリカ情報
```kql
dependencies
| where name == "batch_job"
| extend 
    replica_name = customDimensions.["replica.name"],
    replica_id = customDimensions.["replica.id"],
    hostname = customDimensions.["host.name"],
    container_name = customDimensions.["container.name"],
    duration_seconds = customDimensions.["job.duration_seconds"]
| order by timestamp desc
| project timestamp, replica_name, replica_id, hostname, container_name, duration_seconds
```

### レプリカ別のパフォーマンス分析
```kql
dependencies
| where name == "batch_job"
| extend 
    replica_name = customDimensions.["replica.name"],
    duration_seconds = todecimal(customDimensions.["job.duration_seconds"])
| summarize 
    avg_duration = avg(duration_seconds),
    max_duration = max(duration_seconds),
    min_duration = min(duration_seconds),
    count = count()
    by replica_name
| order by avg_duration desc
```
