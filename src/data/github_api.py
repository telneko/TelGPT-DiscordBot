import json

import requests

from ..data.configs import botConfig
from ..domain.constants import Constants


# noinspection PyMethodMayBeStatic
class GithubAPI:
    def __init__(self):
        pass

    def create_issue(self, author: str, title: str, message: str) -> dict:
        try:
            response = requests.post(
                Constants.create_issue_url,
                headers={
                    'Authorization': f'token {botConfig.github_pat} ',
                    'Content-Type': 'application/json',
                },
                data=json.dumps({
                    "title": f"{title} by {author}",
                    "body": message
                })
            )
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
