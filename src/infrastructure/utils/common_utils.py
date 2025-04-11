import requests
from typing import Optional

from src.domain.config.bot_config import botConfig


def download_image(url: str, save_file_path: str) -> None:
    """
    URLから画像をダウンロードしてファイルに保存する
    
    :param url: ダウンロード元URL
    :param save_file_path: 保存先ファイルパス
    :return: None
    :raises: ダウンロードに失敗した場合は例外を発生させる
    """
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Image download failed: {response.status_code}")
        
    with open(save_file_path, 'wb') as file:
        file.write(response.content)


def translate_text(text: str, source_lang: str = "EN", target_lang: str = "JA") -> str:
    """
    DeepL APIを使用してテキストを翻訳する
    
    :param text: 翻訳元テキスト
    :param source_lang: ソース言語コード (デフォルト: EN)
    :param target_lang: ターゲット言語コード (デフォルト: JA)
    :return: 翻訳後のテキスト
    :raises: 翻訳に失敗した場合は例外を発生させる
    """
    url = "https://api-free.deepl.com/v2/translate"
    params = {
        "auth_key": botConfig.deepl_api_key,
        "text": text,
        "source_lang": source_lang,
        "target_lang": target_lang,
    }
    response = requests.post(url, data=params)
    if response.status_code != 200:
        raise Exception(f"Translation failed: {response.status_code}")
        
    result = response.json()
    return result['translations'][0]['text']
