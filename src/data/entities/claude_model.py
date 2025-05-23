from enum import Enum


class ClaudeModel(Enum):
    """
    Claude のモデルデータ
    """
    CLAUDE_3_7_SONNET = "claude-3-7-sonnet-latest"
    CLAUDE_4_0_SONNET = "claude-sonnet-4-20250514"
    CLAUDE_4_0_OPUS = "claude-opus-4-20250514"
