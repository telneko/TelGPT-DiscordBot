from unittest.mock import Mock
from src.domain.models.ai_models import OpenAIChatModel, OpenAIImageModel, GeminiChatModel, GeminiImageModel


# テスト用のモックConfig
def create_mock_config():
    mock_config = Mock()
    mock_config.discord_assistant_name = 'TestBot'
    mock_config.discord_token = 'test_discord_token'
    mock_config.openai_api_key = 'test_openai_key'
    mock_config.deepl_api_key = 'test_deepl_key'
    mock_config.gemini_api_key = 'test_gemini_key'
    mock_config.github_pat = 'test_github_pat'
    mock_config.openai_chat_model = OpenAIChatModel.GPT_4_O_MINI
    mock_config.openai_image_model = OpenAIImageModel.DALL_E_3
    mock_config.gemini_chat_model = GeminiChatModel.GEMINI_1_5_FLASH
    mock_config.gemini_image_model = GeminiImageModel.IMAGEN_3_0_GENERATE_001
    return mock_config
