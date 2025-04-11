import json
from typing import Dict, Any

import requests

from src.domain.config.bot_config import botConfig
from src.domain.interfaces.api_interfaces import GitHubServiceInterface
from src.domain.models.constants import Constants


class GithubAPI(GitHubServiceInterface):
    """
    GitHub APIクライアントの実装
    """
    def create_issue(self, author: str, title: str, message: str) -> Dict[str, Any]:
        """
        GitHubにIssueを作成する
        
        :param author: 作成者
        :param title: Issueタイトル
        :param message: Issue本文
        :return: 作成結果またはエラー情報を含む辞書
        """
        try:
            response = requests.post(
                Constants.create_issue_url,
                headers={
                    'Authorization': f'token {botConfig.github_pat}',
                    'Content-Type': 'application/json',
                },
                data=json.dumps({
                    "title": f"{title} by {author}",
                    "body": message
                })
            )
            
            if response.status_code != 201:
                return {
                    "error": {
                        "code": response.status_code,
                        "message": f"GitHub API error: {response.text}"
                    }
                }
                
            return {
                "response": response.json()['html_url']
            }
        except Exception as e:
            return {
                "error": {
                    "code": 1,
                    "message": f"Unknown Error {e}"
                }
            }
