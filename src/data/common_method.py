import requests

from src.data.configs import botConfig


def download_image(url: str, save_file_path: str):
    response = requests.get(url)
    with open(save_file_path, 'wb') as file:
        file.write(response.content)


# 英語をDeepLで日本語に翻訳
def translate_text(text: str) -> str:
    url = "https://api-free.deepl.com/v2/translate"
    params = {
        "auth_key": botConfig.deepl_api_key,
        "text": text,
        "source_lang": "EN",
        "target_lang": "JA",
    }
    response = requests.post(url, data=params)
    result = response.json()
    return result['translations'][0]['text']
