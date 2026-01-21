#!/usr/bin/env python3
"""
ModelScope Image Generation Skill
使用 ModelScope API 生成图片
"""

import os
import json
import time
import base64
from typing import Dict, Any, Optional
from pathlib import Path

try:
    import requests
    from PIL import Image
    from io import BytesIO
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class ModelScopeImageSkill:
    """ModelScope 图片生成 Skill"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化 Skill

        Args:
            config: 配置信息，包含 API 密钥等
        """
        self.config = config or {}
        self.api_key = os.environ.get(
            self.config.get("api_key_env", "MODELSCOPE_API_KEY"),
            os.environ.get("MODELSCOPE_SDK_TOKEN")
        )

        if not self.api_key:
            raise ValueError("请设置 MODELSCOPE_API_KEY 环境变量")

        self.base_url = "https://api-inference.modelscope.cn/"
        self.common_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def generate_image(
        self,
        prompt: str,
        model: str = "Qwen/Qwen-Image-2512",
        size: str = "1024x1024",
        output_filename: str = "result_image.jpg",
        output_dir: str = "./outputs",
        max_wait_time: int = 300
    ) -> Dict[str, Any]:
        """
        生成图片

        Args:
            prompt: 图片描述提示词
            model: 使用的模型
            size: 图片尺寸
            output_filename: 输出文件名
            output_dir: 输出目录
            max_wait_time: 最大等待时间（秒）

        Returns:
            生成结果信息
        """
        if not HAS_REQUESTS:
            return {
                "success": False,
                "message": "请安装 requests: pip install requests"
            }

        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # 提交任务
            response = requests.post(
                f"{self.base_url}v1/images/generations",
                headers={**self.common_headers, "X-ModelScope-Async-Mode": "true"},
                data=json.dumps({
                    "model": model,
                    "prompt": prompt,
                }, ensure_ascii=False).encode('utf-8'),
                timeout=120.0
            )
            response.raise_for_status()
            task_id = response.json()["task_id"]

            # 轮询任务状态
            start_time = time.time()
            while time.time() - start_time < max_wait_time:
                result = requests.get(
                    f"{self.base_url}v1/tasks/{task_id}",
                    headers={**self.common_headers, "X-ModelScope-Task-Type": "image_generation"},
                    timeout=30.0
                )
                result.raise_for_status()
                data = result.json()

                if data["task_status"] == "SUCCEED":
                    output_images = data.get("output_images", [])
                    if output_images:
                        image_url = output_images[0]
                        image = Image.open(BytesIO(requests.get(image_url).content))
                        file_path = output_path / output_filename
                        image.save(file_path)

                        return {
                            "success": True,
                            "message": "图片生成成功！",
                            "prompt": prompt,
                            "model": model,
                            "size": size,
                            "file_path": str(file_path),
                            "image_url": image_url
                        }
                    else:
                        return {
                            "success": False,
                            "message": "任务成功但未返回图片"
                        }
                elif data["task_status"] == "FAILED":
                    return {
                        "success": False,
                        "message": "图片生成失败",
                        "task_id": task_id
                    }

                time.sleep(5)

            return {
                "success": False,
                "message": f"任务超时（超过 {max_wait_time} 秒）",
                "task_id": task_id
            }

        except requests.exceptions.HTTPError as e:
            return {
                "success": False,
                "message": f"API 请求失败: {e.response.status_code}",
                "details": e.response.text
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"图片生成失败: {str(e)}"
            }

    def list_models(self) -> Dict[str, Any]:
        """列出支持的模型"""
        return {
            "success": True,
            "models": [
                {
                    "id": "Qwen/Qwen-Image-2512",
                    "description": "通义千问图像生成模型"
                },
                {
                    "id": "Tongyi-MAI/Z-Image-Turbo",
                    "description": "通义万相 Turbo 模型"
                }
            ]
        }


def main():
    """主函数 - 用于命令行测试"""
    import argparse

    parser = argparse.ArgumentParser(description="ModelScope 图片生成工具")
    parser.add_argument("--prompt", required=True, help="图片描述")
    parser.add_argument("--model", default="Tongyi-MAI/Z-Image-Turbo", help="模型名称")
    parser.add_argument("--size", default="1024x1024", help="图片尺寸")
    parser.add_argument("--output", default="result_image.jpg", help="输出文件名")
    parser.add_argument("--dir", default="./outputs", help="输出目录")

    args = parser.parse_args()

    skill = ModelScopeImageSkill()
    result = skill.generate_image(
        prompt=args.prompt,
        model=args.model,
        size=args.size,
        output_filename=args.output,
        output_dir=args.dir
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()