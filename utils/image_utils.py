from PIL import Image
import io
from typing import Optional, Tuple, Union
from pathlib import Path

class ImageUtils:
    """图像处理工具类"""
    
    @staticmethod
    def resize_image(image_path: Union[str, Path], size: Tuple[int, int]) -> Optional[Path]:
        """调整图像大小
        
        Args:
            image_path: 图像路径
            size: 目标大小 (width, height)
            
        Returns:
            Optional[Path]: 调整后的图像路径，如果处理失败则返回None
        """
        try:
            with Image.open(image_path) as img:
                resized_img = img.resize(size, Image.Resampling.LANCZOS)
                output_path = Path(image_path).with_stem(f"{Path(image_path).stem}_resized")
                resized_img.save(output_path)
                return output_path
        except Exception:
            return None
    
    @staticmethod
    def compress_image(image_path: Union[str, Path], quality: int = 85) -> Optional[Path]:
        """压缩图像
        
        Args:
            image_path: 图像路径
            quality: 压缩质量 (1-100)
            
        Returns:
            Optional[Path]: 压缩后的图像路径，如果处理失败则返回None
        """
        try:
            with Image.open(image_path) as img:
                output_path = Path(image_path).with_stem(f"{Path(image_path).stem}_compressed")
                img.save(output_path, quality=quality, optimize=True)
                return output_path
        except Exception:
            return None
    
    @staticmethod
    def convert_format(image_path: Union[str, Path], format: str) -> Optional[Path]:
        """转换图像格式
        
        Args:
            image_path: 图像路径
            format: 目标格式 (如 'JPEG', 'PNG')
            
        Returns:
            Optional[Path]: 转换后的图像路径，如果处理失败则返回None
        """
        try:
            with Image.open(image_path) as img:
                output_path = Path(image_path).with_suffix(f".{format.lower()}")
                img.save(output_path, format=format)
                return output_path
        except Exception:
            return None
    
    @staticmethod
    def image_to_bytes(image_path: Union[str, Path]) -> Optional[bytes]:
        """将图像转换为字节数据
        
        Args:
            image_path: 图像路径
            
        Returns:
            Optional[bytes]: 图像字节数据，如果转换失败则返回None
        """
        try:
            with Image.open(image_path) as img:
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format=img.format)
                return img_byte_arr.getvalue()
        except Exception:
            return None
    
    @staticmethod
    def bytes_to_image(image_bytes: bytes, output_path: Union[str, Path]) -> bool:
        """将字节数据保存为图像
        
        Args:
            image_bytes: 图像字节数据
            output_path: 输出路径
            
        Returns:
            bool: 是否成功
        """
        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                img.save(output_path)
                return True
        except Exception:
            return False 