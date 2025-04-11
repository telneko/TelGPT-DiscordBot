from typing import Final


class Constants:
    # AI が回答中のメッセージ
    answering_message: Final[str] = "回答中です..."

    # Github Issue 作成のエンドポイント
    create_issue_url: Final[str] = "https://api.github.com/repos/telneko/TelGPT-DiscordBot/issues"
    
    # ボットのステータス通知メッセージ
    bot_started_message: Final[str] = "🟢 TelGPT Bot が起動しました"
    bot_stopping_message: Final[str] = "🔴 TelGPT Bot を停止しています..."
    bot_reconnecting_message: Final[str] = "🟡 TelGPT Bot の接続が切断されました。再接続します..."
    bot_resumed_message: Final[str] = "🟢 TelGPT Bot の接続が復旧しました"
