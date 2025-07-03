import logging
import time
import os
from datetime import datetime
from azure.monitor.opentelemetry import configure_azure_monitor

# Application Insights接続文字列を環境変数から取得
APPLICATIONINSIGHTS_CONNECTION_STRING = os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING')

# Azure Monitor OpenTelemetryの設定（接続文字列が設定されている場合のみ）
if APPLICATIONINSIGHTS_CONNECTION_STRING:
    configure_azure_monitor(connection_string=APPLICATIONINSIGHTS_CONNECTION_STRING)
    print("Azure Monitor OpenTelemetryが設定されました")
else:
    print("APPLICATIONINSIGHTS_CONNECTION_STRING環境変数が設定されていません。Application Insightsへのログ送信は無効です。")

# ログの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # コンソール出力
    ]
)

logger = logging.getLogger(__name__)

def main():
    """バッチ処理のメイン関数"""
    # 開始時のログ出力
    logger.info("バッチ処理を開始します")
    logger.info(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 30秒待機
    logger.info("30秒間待機します...")
    time.sleep(30)
    
    # 終了時のログ出力
    logger.info("バッチ処理が完了しました")
    logger.info(f"終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()