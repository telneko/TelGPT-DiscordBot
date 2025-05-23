import os
from dataclasses import dataclass
from typing import Final

from .entities.claude_model import ClaudeModel  # 追加
from .entities.gemini_model import GeminiChatModel, GeminiImageModel
from .entities.openai_chat_model import OpenAIChatModel
from .entities.openai_image_model import OpenAIImageModel
from .entities.stable_diffusion_model import StableDiffusionModel  # 追加


@dataclass
class BotConfig:
    discord_assistant_name: str
    discord_token: str
    openai_api_key: str
    deepl_api_key: str
    gemini_api_key: str
    github_pat: str
    claude_api_key: str  # 追加
    stability_api_key: str  # 追加: Stability AI API キー
    status_channel_id: str  # 追加：ステータス通知チャンネルID

    openai_chat_model: OpenAIChatModel
    openai_image_model: OpenAIImageModel
    gemini_chat_model: GeminiChatModel
    gemini_image_model: GeminiImageModel
    claude_model: ClaudeModel  # 追加
    stable_diffusion_model: StableDiffusionModel  # 追加: Stable Diffusionモデル

    def __init__(self):
        self.discord_assistant_name = 'TelGPT'

        self.discord_token = os.getenv("TEL_GPT_DISCORD_TOKEN")
        self.openai_api_key = os.getenv("TEL_GPT_OPEN_AI_TOKEN")
        self.deepl_api_key = os.getenv("TEL_GPT_DEEPL_TOKEN")
        self.gemini_api_key = os.getenv("TEL_GPT_GEMINI_TOKEN")
        self.github_pat = os.getenv("GITHUB_ISSUE_PAT")
        self.claude_api_key = os.getenv("TEL_GPT_CLAUDE_TOKEN")  # 追加
        self.stability_api_key = os.getenv("TEL_GPT_STABILITY_TOKEN")  # 追加: Stability AI APIキー

        # ステータス通知チャンネルIDの設定（環境変数から取得、未設定の場合はNone）
        self.status_channel_id = os.getenv("TEL_GPT_STATUS_CHANNEL_ID")

        self.openai_chat_model = OpenAIChatModel.GPT_4_1
        self.openai_image_model = OpenAIImageModel.DALL_E_3
        self.gemini_chat_model = GeminiChatModel.GEMINI_2_5_FLASH
        self.gemini_image_model = GeminiImageModel.IMAGEN_3_0_GENERATE_001
        self.claude_model = ClaudeModel.CLAUDE_4_0_SONNET
        self.stable_diffusion_model = StableDiffusionModel.SDXL_1_0


# Bot の設定
botConfig: Final[BotConfig] = BotConfig()
