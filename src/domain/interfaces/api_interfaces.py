from abc import ABC, abstractmethod
from typing import Dict, List, Any

from src.domain.models.ai_models import OpenAIChatModel, OpenAIImageModel, GeminiChatModel, GeminiImageModel
from src.domain.models.message import Message


class AIServiceInterface(ABC):
    """
    AIサービスの基本インターフェース
    """
    @abstractmethod
    def question(self, model: Any, prompt: str, system_setting: str) -> Dict[str, Any]:
        """
        AIモデルに質問を送信し、回答を受け取る
        
        :param model: 使用するモデル
        :param prompt: 質問内容
        :param system_setting: システム設定
        :return: レスポンスまたはエラー情報を含む辞書
        """
        pass


class OpenAIServiceInterface(AIServiceInterface):
    """
    OpenAI API用のインターフェース
    """
    @abstractmethod
    def question(self, model: OpenAIChatModel, prompt: str, system_setting: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def conversation(self, model: OpenAIChatModel, prompts: List[Message]) -> Dict[str, Any]:
        """
        OpenAIモデルとの会話形式の対話を行う
        
        :param model: 使用するモデル
        :param prompts: 会話履歴
        :return: レスポンスまたはエラー情報を含む辞書
        """
        pass
    
    @abstractmethod
    def generate_image(self, model: OpenAIImageModel, prompt: str) -> Dict[str, Any]:
        """
        OpenAIを使用して画像を生成する
        
        :param model: 使用する画像生成モデル
        :param prompt: 画像生成用プロンプト
        :return: 生成された画像のURLとプロンプトを含むレスポンスまたはエラー情報
        """
        pass
    
    @abstractmethod
    def create_image_variation(self, model: OpenAIImageModel, image_path: str) -> Dict[str, Any]:
        """
        既存の画像からバリエーションを生成する
        
        :param model: 使用する画像生成モデル
        :param image_path: 元の画像パス
        :return: 生成された画像のURLとプロンプトを含むレスポンスまたはエラー情報
        """
        pass


class GeminiServiceInterface(AIServiceInterface):
    """
    Gemini API用のインターフェース
    """
    @abstractmethod
    def question(self, model: GeminiChatModel, prompt: str, system_setting: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def generate_image(self, model: GeminiImageModel, prompt: str) -> Dict[str, Any]:
        """
        Geminiを使用して画像を生成する
        
        :param model: 使用する画像生成モデル
        :param prompt: 画像生成用プロンプト
        :return: 生成された画像のURLとプロンプトを含むレスポンスまたはエラー情報
        """
        pass


class GitHubServiceInterface(ABC):
    """
    GitHub API用のインターフェース
    """
    @abstractmethod
    def create_issue(self, author: str, title: str, message: str) -> Dict[str, Any]:
        """
        GitHubにIssueを作成する
        
        :param author: 作成者
        :param title: Issueタイトル
        :param message: Issue本文
        :return: 作成結果またはエラー情報を含む辞書
        """
        pass
