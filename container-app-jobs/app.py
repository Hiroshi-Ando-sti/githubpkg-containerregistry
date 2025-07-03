import logging
import time
import os
import uuid
import socket
from datetime import datetime
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.trace import set_span_in_context

# Application Insights接続文字列を環境変数から取得
APPLICATIONINSIGHTS_CONNECTION_STRING = os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING')

# レプリカ識別用の情報を生成
REPLICA_ID = str(uuid.uuid4())[:8]  # 短いUUID
HOSTNAME = socket.gethostname()
PROCESS_ID = os.getpid()
CONTAINER_NAME = os.getenv('CONTAINER_NAME', 'unknown')
REPLICA_NAME = os.getenv('REPLICA_NAME', f'replica-{REPLICA_ID}')

# Azure Monitor OpenTelemetryの設定（接続文字列が設定されている場合のみ）
if APPLICATIONINSIGHTS_CONNECTION_STRING:
    configure_azure_monitor(
        connection_string=APPLICATIONINSIGHTS_CONNECTION_STRING,
        enable_live_metrics=True,
        resource_attributes={
            'service.name': 'container-app-jobs',
            'service.version': '1.0.0',
            'service.instance.id': REPLICA_ID,
            'host.name': HOSTNAME,
            'container.name': CONTAINER_NAME,
            'replica.name': REPLICA_NAME,
            'process.pid': str(PROCESS_ID)
        }
    )
    print(f"Azure Monitor OpenTelemetryが設定されました (Replica: {REPLICA_NAME})")
else:
    print("APPLICATIONINSIGHTS_CONNECTION_STRING環境変数が設定されていません。Application Insightsへのログ送信は無効です。")

# ログの設定（レプリカ情報を含む）
logging.basicConfig(
    level=logging.INFO,
    format=f'%(asctime)s - %(levelname)s - [Replica:{REPLICA_NAME}] - %(message)s',
    handlers=[
        logging.StreamHandler(),  # コンソール出力
    ]
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# OpenTelemetryトレーサーの取得
tracer = trace.get_tracer(__name__)

def main():
    """バッチ処理のメイン関数"""
    with tracer.start_as_current_span("batch_job") as span:
        # スパンに属性を追加
        span.set_attribute("job.type", "batch_job")
        span.set_attribute("job.version", "1.0")
        span.set_attribute("replica.id", REPLICA_ID)
        span.set_attribute("replica.name", REPLICA_NAME)
        span.set_attribute("host.name", HOSTNAME)
        span.set_attribute("container.name", CONTAINER_NAME)
        span.set_attribute("process.pid", PROCESS_ID)
        
        # 開始時のログ出力
        span.set_attribute("job.phase", "start")
        logger.info("バッチ処理を開始します", extra={
            'replica_id': REPLICA_ID,
            'replica_name': REPLICA_NAME,
            'hostname': HOSTNAME,
            'container_name': CONTAINER_NAME,
            'process_id': PROCESS_ID
        })
        start_time = datetime.now()
        logger.info(f"開始時刻: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # SLEEP_SECONDS 秒 待機
        SLEEP_SECONDS_STR = os.getenv('SLEEP_SECONDS', '30')  # デフォルト値30秒
        try:
            SLEEP_SECONDS = int(SLEEP_SECONDS_STR)
        except ValueError:
            logger.warning(f"SLEEP_SECONDS環境変数の値が無効です: {SLEEP_SECONDS_STR}. デフォルト値30秒を使用します。")
            SLEEP_SECONDS = 30
        
        span.set_attribute("job.phase", "processing")
        span.set_attribute("job.sleep_seconds", SLEEP_SECONDS)
        logger.info(f"{SLEEP_SECONDS}秒間待機します...")
        time.sleep(SLEEP_SECONDS)
        
        # 終了時のログ出力
        span.set_attribute("job.phase", "end")
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        span.set_attribute("job.duration_seconds", duration)
        
        logger.info("バッチ処理が完了しました", extra={
            'replica_id': REPLICA_ID,
            'replica_name': REPLICA_NAME,
            'duration_seconds': duration
        })
        logger.info(f"終了時刻: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"実行時間: {duration:.2f}秒")

if __name__ == "__main__":
    main()