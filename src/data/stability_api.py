import base64
import os
import io
from typing import Dict, Any, Optional

import requests
from PIL import Image

from .configs import botConfig
from .entities.stable_diffusion_model import StableDiffusionModel


class StabilityAPI:
    """
    Stability AI APIのクライアントクラス
    """
    API_HOST = "https://api.stability.ai"
    
    def __init__(self):
        """初期化"""
        self.api_key = botConfig.stability_api_key
        if not self.api_key:
            raise ValueError("Stability AI API key is not set")
    
    def generate_image(
        self,
        model: StableDiffusionModel,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        cfg_scale: float = 7.0,
        steps: int = 30,
        samples: int = 1
    ) -> Dict[str, Any]:
        """
        テキストプロンプトから画像を生成する
        
        Args:
            model: 使用するStable Diffusionモデル
            prompt: 画像生成のプロンプト
            negative_prompt: ネガティブプロンプト（生成に含めたくない要素）
            width: 生成画像の幅
            height: 生成画像の高さ
            cfg_scale: プロンプトの忠実度 (guidance scale)
            steps: 生成ステップ数
            samples: 生成する画像の数
            
        Returns:
            Dict: レスポンス情報を含む辞書
                成功時: {'response': {'url': 画像URL, 'prompt': 使用されたプロンプト, 'base64': Base64画像データ}}
                失敗時: {'error': {'message': エラーメッセージ}}
        """
        try:
            engine_id = model.value
            
            # リクエスト用のJSONデータを作成
            payload = {
                "text_prompts": [{"text": prompt}],
                "cfg_scale": cfg_scale,
                "height": height,
                "width": width,
                "samples": samples,
                "steps": steps,
            }
            
            # ネガティブプロンプトの追加（存在する場合）
            if negative_prompt:
                payload["text_prompts"].append({"text": negative_prompt, "weight": -1.0})
            
            # APIエンドポイントの設定
            url = f"{self.API_HOST}/v1/generation/{engine_id}/text-to-image"
            
            # APIリクエストを送信
            response = requests.post(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json=payload
            )
            
            # レスポンスのステータスコードが成功でない場合
            if response.status_code != 200:
                print(f"Stability API Error: {response.status_code} - {response.text}")
                return {
                    "error": {
                        "message": f"API error: {response.status_code} - {response.text}"
                    }
                }
            
            # レスポンスのJSONを解析
            data = response.json()
            
            # 画像データをデコード
            if "artifacts" in data and len(data["artifacts"]) > 0:
                artifact = data["artifacts"][0]
                
                # Base64画像データ
                image_base64 = artifact["base64"]
                
                # 一時的なURLをDiscordで使えるURLスキームに変換
                base64_url = f"data:image/png;base64,{image_base64}"
                
                # 一時ファイルを作成して、Discord用の添付ファイルとして使用
                # このアプローチでは、Discord側で表示可能な一時ファイルを提供
                temp_image_path = "temp_image.png"
                with open(temp_image_path, "wb") as f:
                    f.write(base64.b64decode(image_base64))
                
                return {
                    "response": {
                        "url": temp_image_path,  # 添付ファイル用のパス
                        "prompt": prompt,
                        "seed": artifact.get("seed", None),
                        "finish_reason": artifact.get("finish_reason", None),
                        "base64": image_base64  # 元のBase64データも保持
                    }
                }
            else:
                print("No image was generated from Stability API")
                return {
                    "error": {
                        "message": "No image was generated"
                    }
                }
                
        except Exception as e:
            print(f"Error in Stability API: {str(e)}")
            return {
                "error": {
                    "message": f"Error generating image: {str(e)}"
                }
            }
