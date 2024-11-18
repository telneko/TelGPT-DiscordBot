from enum import Enum


class OpenAIChatModel(Enum):
    """
    OpenAI の対話モデルデータ
    """
    GPT_4_O = "gpt-4o"
    GPT_4_O_MINI = "gpt-4o-mini"
    GPT_O1_PREVIEW = "o1-preview"
