import requests
from PIL import Image
from io import BytesIO
import os

def download_and_resize_banner():
    # 使用一个适合的股市图表静态图片URL
    image_url = "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1000"
    
    try:
        # 下载图片
        image_response = requests.get(image_url)
        image = Image.open(BytesIO(image_response.content))
        
        # 调整尺寸为320x180
        resized_image = image.resize((320, 180), Image.Resampling.LANCZOS)
        
        # 确保目标目录存在
        output_dir = "../android/app/src/main/res/drawable"
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存图片
        output_path = os.path.join(output_dir, "tv_banner.png")
        resized_image.save(output_path, "PNG")
        
        print(f"Banner已保存到: {output_path}")
        
    except Exception as e:
        print(f"下载banner时出错: {str(e)}")

if __name__ == "__main__":
    download_and_resize_banner() 