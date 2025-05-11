from enum import Enum


class OpenAIChatModel(Enum):
    """
    OpenAI の対話モデルデータ
    """
    GPT_4_O = "gpt-4o"
    GPT_4_O_MINI = "gpt-4o-mini"
    GPT_4_1 = "gpt-4.1"
    GPT_O1_PREVIEW = "o1-preview"


class OpenAIImageModel(Enum):
    """
    OpenAI の画像生成モデルデータ
    """
    DALL_E_3 = "dall-e-3"


class GeminiChatModel(Enum):
    """
    Gemini の対話モデルデータ
    """
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    GEMINI_2_0_FLASH = "gemini-2.0-flash"


class GeminiImageModel(Enum):
    """
    Gemini の画像生成モデルデータ
    """
    IMAGEN_3_0_GENERATE_001 = "imagegeneration@003"
