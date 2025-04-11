from enum import Enum


class StableDiffusionModel(Enum):
    """
    Stable Diffusionモデルの列挙型
    """
    # 標準的なStable Diffusionモデル
    SDXL_1_0 = "stable-diffusion-xl-1024-v1-0"
    
    # Stable Diffusion 3モデル
    SD3_MEDIUM = "sd3-medium"
    
    # デフォルトはSDXL 1.0を使用
    DEFAULT = SDXL_1_0
