from openai import OpenAI, BadRequestError
from typing import Dict, List, Any

from src.domain.config.bot_config import botConfig
from src.domain.interfaces.api_interfaces import OpenAIServiceInterface
from src.domain.models.ai_models import OpenAIChatModel, OpenAIImageModel
from src.domain.models.message import Message


# OpenAIのエラーハンドリング. エラーコードによってメッセージを変更
def handle_bad_request_error(e: BadRequestError) -> Dict[str, Any]:
    """
    OpenAI APIのエラーハンドリングを行う
    
    :param e: BadRequestErrorエラーオブジェクト
    :return: エラー情報を含む辞書
    """
    if e.code == "content_policy_violation":
        message = "コンテンツポリシー違反です. 他の質問をしてください."
    else:
        message = "エラーが発生しました. Error Code: " + e.code

    return {
        "error": {
            "code": e.code,
            "message": message
        }
    }


class OpenAIAPI(OpenAIServiceInterface):
    """
    OpenAI APIクライアントの実装
    """
    openAIClient: OpenAI

    def __init__(self):
        # OpenAI API の設定
        self.openAIClient = OpenAI(api_key=botConfig.openai_api_key)

    def question(self, model: OpenAIChatModel, prompt: str, system_setting: str) -> Dict[str, Any]:
        """
        OpenAIモデルに質問を送信し、回答を受け取る
        
        :param model: 使用するモデル
        :param prompt: 質問内容
        :param system_setting: システム設定
        :return: レスポンスまたはエラー情報を含む辞書
        """
        try:
            response = self.openAIClient.chat.completions.create(
                model=model.value,
                messages=[
                    {
                        "role": "system",
                        "content": "Your response should be in Japanese.",
                    },
                    {
                        "role": "system",
                        "content": system_setting,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
            return {
                "response": response.choices[0].message.content.strip()
            }
        except BadRequestError as e:
            return handle_bad_request_error(e)
        except Exception as e:
            return {
                "error": {
                    "code": 1,
                    "message": f"Unknown Error {e}"
                }
            }

    def conversation(self, model: OpenAIChatModel, prompts: List[Message]) -> Dict[str, Any]:
        """
        OpenAIモデルとの会話形式の対話を行う
        
        :param model: 使用するモデル
        :param prompts: 会話履歴
        :return: レスポンスまたはエラー情報を含む辞書
        """
        try:
            messages = []
            for message in prompts:
                messages.append(
                    {
                        "role": message.role,
                        "content": message.content,
                    }
                )
            # noinspection PyTypeChecker
            response = self.openAIClient.chat.completions.create(
                model=model.value,
                messages=messages,
            )
            return {
                "response": response.choices[0].message.content.strip()
            }
        except BadRequestError as e:
            return handle_bad_request_error(e)
        except Exception as e:
            return {
                "error": {
                    "code": 1,
                    "message": f"Unknown Error {e}"
                }
            }

    def create_image_variation(self, model: OpenAIImageModel, image_path: str) -> Dict[str, Any]:
        """
        既存の画像からバリエーションを生成する
        
        :param model: 使用する画像生成モデル
        :param image_path: 元の画像パス
        :return: 生成された画像のURLとプロンプトを含むレスポンスまたはエラー情報
        """
        try:
            response = self.openAIClient.images.create_variation(
                model=model.value,
                image=open(image_path, "rb"),
                n=1,
                size="1024x1024"
            )
            return {
                "response": {
                    "url": response.data[0].url,
                    "prompt": response.data[0].revised_prompt
                }
            }
        except BadRequestError as e:
            return handle_bad_request_error(e)
        except Exception as e:
            return {
                "error": {
                    "code": 1,
                    "message": f"Unknown Error {e}"
                }
            }

    def generate_image(self, model: OpenAIImageModel, prompt: str) -> Dict[str, Any]:
        """
        OpenAIを使用して画像を生成する
        
        :param model: 使用する画像生成モデル
        :param prompt: 画像生成用プロンプト
        :return: 生成された画像のURLとプロンプトを含むレスポンスまたはエラー情報
        """
        try:
            response = self.openAIClient.images.generate(
                model=model.value,
                prompt=prompt,
                response_format="url"
            )
            return {
                "response": {
                    "url": response.data[0].url,
                    "prompt": response.data[0].revised_prompt
                }
            }
        except BadRequestError as e:
            return handle_bad_request_error(e)
        except Exception as e:
            return {
                "error": {
                    "code": 1,
                    "message": f"Unknown Error {e}"
                }
            }
