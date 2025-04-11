import pytest
from unittest.mock import patch, MagicMock, mock_open
import os
import json

from src.infrastructure.utils.common_utils import download_image, translate_text


@pytest.fixture
def mock_requests():
    with patch("src.infrastructure.utils.common_utils.requests") as mock_requests:
        yield mock_requests


def test_download_image_success(mock_requests):
    # 画像ダウンロード成功のテスト
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"image data"
    mock_requests.get.return_value = mock_response
    
    # open関数のモック
    with patch("builtins.open", mock_open()) as mock_file:
        download_image("https://example.com/image.png", "test_image.png")
        
        # 正しいURLからダウンロードされたかチェック
        mock_requests.get.assert_called_once_with("https://example.com/image.png")
        
        # 正しいファイル名で保存されたかチェック
        mock_file.assert_called_once_with("test_image.png", "wb")
        
        # 正しいデータが書き込まれたかチェック
        mock_file().write.assert_called_once_with(b"image data")


def test_download_image_failure(mock_requests):
    # 画像ダウンロード失敗のテスト
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_requests.get.return_value = mock_response
    
    with pytest.raises(Exception) as exc_info:
        download_image("https://example.com/not_found.png", "test_image.png")
    
    assert "Image download failed" in str(exc_info.value)


def test_translate_text_success(mock_requests):
    # 翻訳成功のテスト
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "translations": [{
            "text": "これはテストです"
        }]
    }
    mock_requests.post.return_value = mock_response
    
    result = translate_text("This is a test")
    
    # 結果を検証
    assert result == "これはテストです"
    
    # 正しいパラメータでAPIが呼び出されたかチェック
    mock_requests.post.assert_called_once()
    call_args = mock_requests.post.call_args
    assert call_args[0][0] == "https://api-free.deepl.com/v2/translate"
    
    # パラメータをチェック
    data = call_args[1]["data"]
    assert data["text"] == "This is a test"
    assert data["source_lang"] == "EN"
    assert data["target_lang"] == "JA"


def test_translate_text_custom_langs(mock_requests):
    # カスタム言語指定での翻訳テスト
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "translations": [{
            "text": "This is a test"
        }]
    }
    mock_requests.post.return_value = mock_response
    
    result = translate_text("これはテストです", source_lang="JA", target_lang="EN")
    
    # 結果を検証
    assert result == "This is a test"
    
    # 正しい言語パラメータが指定されたかチェック
    call_args = mock_requests.post.call_args
    data = call_args[1]["data"]
    assert data["source_lang"] == "JA"
    assert data["target_lang"] == "EN"


def test_translate_text_failure(mock_requests):
    # 翻訳失敗のテスト
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.text = "API key invalid"
    mock_requests.post.return_value = mock_response
    
    with pytest.raises(Exception) as exc_info:
        translate_text("This is a test")
    
    assert "Translation failed" in str(exc_info.value)
