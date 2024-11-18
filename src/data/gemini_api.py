import google.generativeai as gemini_api

from src.configs import botConfig
from src.domain.gemini_chat_model import GeminiChatModel


class GeminiAPI:
    # Gemini API variable
    gemini_api: gemini_api

    def __init__(self):
        # Gemini API の設定
        gemini_api.configure(api_key=botConfig.gemini_api_key)
        self.gemini_api = gemini_api

    def question(self, model: GeminiChatModel, prompt: str) -> dict:
        try:
            model = self.gemini_api.GenerativeModel(model_name=model.value)
            response = model.generate_content(prompt)
            return {"response": response.text}
        except Exception as e:
            return {"error": {"code": 1, "message": f"Gemini API Error: {e}"}}
