from enum import Enum


class GeminiChatModel(Enum):
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GEMINI_2_5_FLASH = "gemini-2.5-flash-preview-05-20"


class GeminiImageModel(Enum):
    IMAGEN_3_0_GENERATE_001 = "imagen-3.0-generate-001"
