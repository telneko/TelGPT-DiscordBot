from openai import OpenAI, BadRequestError

from .configs import botConfig
from .entities.entity import Message
from .entities.openai_chat_model import OpenAIChatModel
from .entities.openai_image_model import OpenAIImageModel


# OpenAIのエラーハンドリング. エラーコードによってメッセージを変更
def handle_bad_request_error(e: BadRequestError):
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


class OpenAIAPI:
    openAIClient: OpenAI

    def __init__(self):
        # OpenAI API の設定
        self.openAIClient = OpenAI(api_key=botConfig.openai_api_key)

    def question(self, model: OpenAIChatModel, prompt: str, system_setting: str) -> dict:
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

    def conversation(self, model: OpenAIChatModel, prompts: list[Message]) -> dict:
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

    def create_image_variation(self, model: OpenAIImageModel, image_path: str) -> dict:
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

    def generate_image(self, model: OpenAIImageModel, prompt: str) -> dict:
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
