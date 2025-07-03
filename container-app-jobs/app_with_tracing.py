import logging
import time
import os
from datetime import datetime
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

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

# OpenTelemetryトレーサーの取得
tracer = trace.get_tracer(__name__)

def main():
    """バッチ処理のメイン関数（OpenTelemetryトレース付き）"""
    with tracer.start_as_current_span("batch_job") as span:
        # スパンに属性を追加
        span.set_attribute("job.type", "batch_job")
        span.set_attribute("job.version", "1.0")
        
        # 開始時のログ出力
        span.set_attribute("job.phase", "start")
        logger.info("バッチ処理を開始します")
        start_time = datetime.now()
        logger.info(f"開始時刻: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 30秒待機
        span.set_attribute("job.phase", "processing")
        logger.info("30秒間待機します...")
        time.sleep(30)
        
        # 終了時のログ出力
        span.set_attribute("job.phase", "end")
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        span.set_attribute("job.duration_seconds", duration)
        
        logger.info("バッチ処理が完了しました")
        logger.info(f"終了時刻: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"実行時間: {duration:.2f}秒")

if __name__ == "__main__":
    main()
