import google.generativeai as gemini_api

from .configs import botConfig
from .entities.gemini_model import GeminiChatModel, GeminiImageModel


# noinspection PyMethodMayBeStatic
class GeminiAPI:
    # Gemini API variable
    gemini_api: gemini_api

    def __init__(self):
        # Gemini API の設定
        gemini_api.configure(api_key=botConfig.gemini_api_key)
        self.gemini_api = gemini_api

    def question(self, model: GeminiChatModel, prompt: str, system_setting: str) -> dict:
        try:
            model = self.gemini_api.GenerativeModel(
                model_name=model.value,
                system_instruction=[
                    "Your response should be in Japanese.",
                    system_setting,
                ]
            )
            response = model.generate_content(prompt)
            return {"response": response.text}
        except Exception as e:
            return {"error": {"code": 1, "message": f"Gemini API Error: {e}"}}

    def generate_image(self, model: GeminiImageModel, prompt: str) -> dict:
        try:
            imagen = gemini_api.ImageGenerationModel(model.value)
            response = imagen.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="1:1",
            )
            image = response.images.pop(0)

            # image.png として保存
            image.save("image.png")

            return {
                "response": {
                }
            }
        except Exception as e:
            return {
                "error": {
                    "code": 1,
                    "message": f"Unknown Error {e}"
                }
            }
