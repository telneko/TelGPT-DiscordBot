import asyncio
import atexit
import signal
import sys

from data.configs import botConfig
from data.discord_command import discordClient, status_channel
from data.entities.constants import Constants

# シャットダウン時の処理
def send_shutdown_notification():
    """ボットのシャットダウン時に通知を送信"""
    if status_channel:
        # 非同期関数を同期的に実行するための処理
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # ループが実行中の場合はタスクとして登録
            loop.create_task(status_channel.send(Constants.bot_stopping_message))
            # 少し待ってメッセージが送信されるのを待つ
            loop.run_until_complete(asyncio.sleep(1))
        else:
            # ループが実行されていない場合は新しく作成して実行
            asyncio.run(status_channel.send(Constants.bot_stopping_message))

# シグナルハンドラの設定
def signal_handler(sig, frame):
    """シグナル受信時のハンドラ"""
    print(f"Signal {sig} received, shutting down...")
    send_shutdown_notification()
    # クライアントをクローズ
    if not discordClient.is_closed():
        loop = asyncio.get_event_loop()
        loop.run_until_complete(discordClient.close())
    sys.exit(0)

# 終了時とシグナル受信時のハンドラを登録
atexit.register(send_shutdown_notification)
signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # termination

# メインエントリーポイント
if __name__ == "__main__":
    discordClient.run(token=botConfig.discord_token)
