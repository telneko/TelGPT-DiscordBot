from dataclasses import dataclass


@dataclass
class Message:
    role: str
    content: str


@dataclass
class CachedError:
    message: str
    translated_message: str
