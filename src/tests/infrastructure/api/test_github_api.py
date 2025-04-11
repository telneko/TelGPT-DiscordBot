import pytest
from unittest.mock import patch, MagicMock
import json
import requests

from src.domain.models.constants import Constants
from src.infrastructure.api.github_api import GithubAPI


@pytest.fixture
def mock_requests():
    with patch("src.infrastructure.api.github_api.requests") as mock_requests:
        yield mock_requests


def test_create_issue_success(mock_requests):
    # 成功時のIssue作成をテスト
    # Mockの設定
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "html_url": "https://github.com/test/repo/issues/1"
    }
    mock_requests.post.return_value = mock_response
    
    # API呼び出し
    github_api = GithubAPI()
    result = github_api.create_issue(
        author="test_user",
        title="Test Issue",
        message="This is a test issue"
    )
    
    # 結果を検証
    assert "response" in result
    assert result["response"] == "https://github.com/test/repo/issues/1"
    
    # 正しい引数でAPIが呼び出されたかチェック
    mock_requests.post.assert_called_once()
    call_args = mock_requests.post.call_args
    assert call_args[0][0] == Constants.create_issue_url
    
    # JSONデータをチェック
    json_data = json.loads(call_args[1]["data"])
    assert json_data["title"] == "Test Issue by test_user"
    assert json_data["body"] == "This is a test issue"


def test_create_issue_api_error(mock_requests):
    # APIエラー発生時のテスト
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    mock_requests.post.return_value = mock_response
    
    github_api = GithubAPI()
    result = github_api.create_issue(
        author="test_user",
        title="Test Issue",
        message="This is a test issue"
    )
    
    assert "error" in result
    assert result["error"]["code"] == 401
    assert "GitHub API error" in result["error"]["message"]


def test_create_issue_exception(mock_requests):
    # 例外発生時のテスト
    mock_requests.post.side_effect = Exception("Network error")
    
    github_api = GithubAPI()
    result = github_api.create_issue(
        author="test_user",
        title="Test Issue",
        message="This is a test issue"
    )
    
    assert "error" in result
    assert result["error"]["code"] == 1
    assert "Unknown Error" in result["error"]["message"]
