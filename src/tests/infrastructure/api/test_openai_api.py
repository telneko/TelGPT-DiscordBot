import pytest
from unittest.mock import patch, MagicMock
import json

from src.domain.models.ai_models import OpenAIChatModel, OpenAIImageModel
from src.domain.models.message import Message
from src.infrastructure.api.openai_api import OpenAIAPI, handle_bad_request_error


@pytest.fixture
def mock_openai_client():
    with patch("src.infrastructure.api.openai_api.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        yield mock_client


def test_handle_bad_request_error_content_policy_violation():
    # コンテンツポリシー違反のエラーハンドリングをテスト
    error = MagicMock()
    error.code = "content_policy_violation"
    error.message = "Content policy violation"
    
    result = handle_bad_request_error(error)
    
    assert "error" in result
    assert result["error"]["code"] == "content_policy_violation"
    assert "コンテンツポリシー違反" in result["error"]["message"]


def test_handle_bad_request_error_other():
    # その他のエラーのハンドリングをテスト
    error = MagicMock()
    error.code = "other_error"
    error.message = "Other error"
    
    result = handle_bad_request_error(error)
    
    assert "error" in result
    assert result["error"]["code"] == "other_error"
    assert "Error Code:" in result["error"]["message"]


def test_question_success(mock_openai_client):
    # 成功時の質問処理をテスト
    # Mockの設定
    mock_response = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "This is a test response"
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    mock_completions = MagicMock()
    mock_completions.create.return_value = mock_response
    mock_openai_client.chat.completions = mock_completions
    
    # API呼び出し
    api = OpenAIAPI()
    result = api.question(
        model=OpenAIChatModel.GPT_4_O_MINI,
        prompt="Hello, world!",
        system_setting="You are a helpful assistant."
    )
    
    # 結果を検証
    assert "response" in result
    assert result["response"] == "This is a test response"
    
    # 正しい変数でAPIが呼び出されたかチェック
    mock_completions.create.assert_called_once()
    call_args = mock_completions.create.call_args[1]
    assert call_args["model"] == OpenAIChatModel.GPT_4_O_MINI.value
    assert len(call_args["messages"]) == 3
    assert call_args["messages"][2]["content"] == "Hello, world!"


def test_question_api_error(mock_openai_client):
    # APIエラー発生時のテスト
    from openai import BadRequestError
    from openai.types import ErrorObject

    # 新しいバージョンのOpenAI SDKに対応したモックエラー
    error = BadRequestError(
        message="Bad request",
        response=MagicMock(),
        body={"error": {"message": "Bad request", "type": "bad_request"}},
    )
    # エラーのコードを後付けで設定
    error.code = "bad_request"
    
    mock_openai_client.chat.completions.create.side_effect = error
    
    api = OpenAIAPI()
    result = api.question(
        model=OpenAIChatModel.GPT_4_O_MINI,
        prompt="Hello, world!",
        system_setting="You are a helpful assistant."
    )
    
    assert "error" in result
    assert result["error"]["code"] == "bad_request"


def test_conversation_success(mock_openai_client):
    # 成功時の会話処理をテスト
    # Mockの設定
    mock_response = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "Conversation response"
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    mock_completions = MagicMock()
    mock_completions.create.return_value = mock_response
    mock_openai_client.chat.completions = mock_completions
    
    # API呼び出し
    api = OpenAIAPI()
    result = api.conversation(
        model=OpenAIChatModel.GPT_4_O_MINI,
        prompts=[
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi there"),
            Message(role="user", content="How are you?")
        ]
    )
    
    # 結果を検証
    assert "response" in result
    assert result["response"] == "Conversation response"
    
    # 正しい変数でAPIが呼び出されたかチェック
    mock_completions.create.assert_called_once()
    call_args = mock_completions.create.call_args[1]
    assert call_args["model"] == OpenAIChatModel.GPT_4_O_MINI.value
    assert len(call_args["messages"]) == 3


def test_generate_image_success(mock_openai_client):
    # 成功時の画像生成処理をテスト
    # Mockの設定
    mock_data = MagicMock()
    mock_data.url = "https://example.com/image.png"
    mock_data.revised_prompt = "Revised prompt"
    mock_response = MagicMock()
    mock_response.data = [mock_data]
    
    mock_images = MagicMock()
    mock_images.generate.return_value = mock_response
    mock_openai_client.images = mock_images
    
    # API呼び出し
    api = OpenAIAPI()
    result = api.generate_image(
        model=OpenAIImageModel.DALL_E_3,
        prompt="Generate a cat image"
    )
    
    # 結果を検証
    assert "response" in result
    assert result["response"]["url"] == "https://example.com/image.png"
    assert result["response"]["prompt"] == "Revised prompt"
    
    # 正しい変数でAPIが呼び出されたかチェック
    mock_images.generate.assert_called_once_with(
        model=OpenAIImageModel.DALL_E_3.value,
        prompt="Generate a cat image",
        response_format="url"
    )