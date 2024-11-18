from typing import Final


class Constants:
    # AI が回答中のメッセージ
    answering_message: Final[str] = "回答中です..."

    # Github Issue 作成のエンドポイント
    create_issue_url: Final[str] = "https://api.github.com/repos/telneko/TelGPT-DiscordBot/issues"
