import google.generativeai as gemini_api
from typing import Dict, Any

from src.domain.config.bot_config import botConfig
from src.domain.interfaces.api_interfaces import GeminiServiceInterface
from src.domain.models.ai_models import GeminiChatModel, GeminiImageModel


class GeminiAPI(GeminiServiceInterface):
    """
    Gemini APIクライアントの実装
    """
    gemini_api: gemini_api

    def __init__(self):
        # Gemini API の設定
        gemini_api.configure(api_key=botConfig.gemini_api_key)
        self.gemini_api = gemini_api

    def question(self, model: GeminiChatModel, prompt: str, system_setting: str) -> Dict[str, Any]:
        """
        Geminiモデルに質問を送信し、回答を受け取る
        
        :param model: 使用するモデル
        :param prompt: 質問内容
        :param system_setting: システム設定
        :return: レスポンスまたはエラー情報を含む辞書
        """
        try:
            model_instance = self.gemini_api.GenerativeModel(
                model_name=model.value,
                system_instruction=[
                    "Your response should be in Japanese.",
                    system_setting,
                ]
            )
            response = model_instance.generate_content(prompt)
            return {"response": response.text}
        except Exception as e:
            return {"error": {"code": 1, "message": f"Gemini API Error: {e}"}}

    def generate_image(self, model: GeminiImageModel, prompt: str) -> Dict[str, Any]:
        """
        Geminiを使用して画像を生成する
        
        :param model: 使用する画像生成モデル
        :param prompt: 画像生成用プロンプト
        :return: 生成された画像のURLとプロンプトを含むレスポンスまたはエラー情報
        """
        try:
            imagen = self.gemini_api.ImageGenerationModel(model.value)
            response = imagen.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="1:1",
            )
            image = response.images.pop(0)

            # image.pngとして保存
            image_path = "image.png"
            image.save(image_path)

            # レスポンスを返す
            # 注意: Gemini APIは現在URLを返さないので、保存した画像パスを返す
            return {
                "response": {
                    "path": image_path,
                    "prompt": prompt  # Geminiは修正されたプロンプトを返さないので、元のプロンプトを使用
                }
            }
        except Exception as e:
            return {
                "error": {
                    "code": 1,
                    "message": f"Gemini Image Generation Error: {e}"
                }
            }
