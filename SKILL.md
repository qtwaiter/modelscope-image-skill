# ModelScope Image Generation Skill

**Name:** modelscope-image-generator

**Description:** 使用 ModelScope API 生成图片的 Skill，支持通义千问和通义万相模型。

## Features

- 支持多个图片生成模型
- 异步任务轮询，自动获取生成的图片
- 图片自动保存到本地目录
- 简洁的 API 接口

## Usage

```python
from skill import ModelScopeImageSkill

skill = ModelScopeImageSkill()
result = skill.generate_image(
    prompt="一只在草地上跑的橘猫",
    model="Tongyi-MAI/Z-Image-Turbo"
)
```

## Models

- `Qwen/Qwen-Image-2512` - 通义千问图像生成模型
- `Tongyi-MAI/Z-Image-Turbo` - 通义万相 Turbo 模型
