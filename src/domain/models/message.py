from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Message:
    """AI モデルとの会話メッセージを表現するクラス"""
    role: str
    content: str


@dataclass
class CachedError:
    """エラーメッセージとその翻訳を保持するクラス"""
    message: str
    translated_message: str
