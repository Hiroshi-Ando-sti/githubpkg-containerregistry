# GitHub Container Registry - Multi-Application Docker Build

このリポジトリには複数のアプリケーションが含まれており、それぞれ個別のDockerイメージとしてGitHub Container Registry (GHCR)に自動デプロイされます。

## アプリケーション構成

### 1. WebAPI (`webapi/`)
- Web APIアプリケーション
- イメージ名: `ghcr.io/{owner}/{repository}/webapi`

### 2. Container App Jobs (`container-app-jobs/`)
- バッチジョブアプリケーション（Azure Container Apps Jobs用）
- Application Insightsログ出力機能付き
- イメージ名: `ghcr.io/{owner}/{repository}/container-app-jobs`

## GitHub Actions ワークフロー

### 利用可能なワークフロー

1. **`docker-publish.yml`** - 個別ジョブ戦略
   - webapiとcontainer-app-jobsを個別のジョブで並列ビルド
   - より詳細な制御が可能

2. **`docker-publish-matrix.yml`** - マトリックス戦略
   - マトリックス戦略でより簡潔な設定
   - 新しいアプリケーション追加が容易

### 自動ビルドトリガー
- `main`ブランチへのプッシュ時に自動実行
- 各アプリケーションが個別のコンテナイメージとしてビルド・プッシュ

### 生成されるイメージタグ
- `latest` (mainブランチの最新)
- `main-{sha}` (コミットSHA付き)
- ブランチ名ベースのタグ

## イメージの使用方法

### WebAPIの実行
```bash
docker pull ghcr.io/{owner}/{repository}/webapi:latest
docker run -p 8000:8000 ghcr.io/{owner}/{repository}/webapi:latest
```

### Container App Jobsの実行
```bash
docker pull ghcr.io/{owner}/{repository}/container-app-jobs:latest
docker run -e APPLICATIONINSIGHTS_CONNECTION_STRING="your-connection-string" ghcr.io/{owner}/{repository}/container-app-jobs:latest
```

## ローカル開発

各アプリケーションのディレクトリでDockerイメージをビルドできます：

### WebAPI
```bash
cd webapi
docker build -t webapi .
docker run -p 8000:8000 webapi
```

### Container App Jobs
```bash
cd container-app-jobs
docker build -t container-app-jobs .
docker run container-app-jobs
```

## Azure での利用

### Container Apps
```bash
az containerapp create \
  --name my-webapi \
  --resource-group myResourceGroup \
  --environment myContainerAppsEnvironment \
  --image ghcr.io/{owner}/{repository}/webapi:latest \
  --target-port 8000 \
  --ingress external
```

### Container Apps Jobs
```bash
az containerapp job create \
  --name my-batch-job \
  --resource-group myResourceGroup \
  --environment myContainerAppsEnvironment \
  --trigger-type Manual \
  --image ghcr.io/{owner}/{repository}/container-app-jobs:latest \
  --env-vars APPLICATIONINSIGHTS_CONNECTION_STRING=secretref:appinsights-connection-string
```
