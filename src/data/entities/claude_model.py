from enum import Enum


class ClaudeModel(Enum):
    """
    Claude のモデルデータ
    """
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
