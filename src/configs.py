import os
from dataclasses import dataclass
from typing import Final

from src.domain.gemini_chat_model import GeminiChatModel
from src.domain.openai_chat_model import OpenAIChatModel
from src.domain.openai_image_model import OpenAIImageModel


@dataclass
class BotConfig:
    discord_assistant_name: str
    discord_token: str
    openai_api_key: str
    deepl_api_key: str
    gemini_api_key: str
    github_pat: str
    openai_chat_model: OpenAIChatModel
    openai_image_model: OpenAIImageModel
    gemini_chat_model: GeminiChatModel

    def __init__(self):
        self.discord_assistant_name = 'TelGPT'
        self.discord_token = os.getenv("TEL_GPT_DISCORD_TOKEN")
        self.openai_api_key = os.getenv("TEL_GPT_OPEN_AI_TOKEN")
        self.deepl_api_key = os.getenv("TEL_GPT_DEEPL_TOKEN")
        self.gemini_api_key = os.getenv("TEL_GPT_GEMINI_TOKEN")
        self.github_pat = os.getenv("GITHUB_ISSUE_PAT")
        self.openai_chat_model = OpenAIChatModel.GPT_O1_PREVIEW
        self.openai_image_model = OpenAIImageModel.DALL_E_3
        self.gemini_chat_model = GeminiChatModel.GEMINI_1_5_FLASH


# Bot の設定
botConfig: Final[BotConfig] = BotConfig()
