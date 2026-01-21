# ModelScope 图片生成 Skill

使用 ModelScope API 生成图片的 Skill，支持通义千问和通义万相模型。

## 功能特性

- 支持多个图片生成模型
- 异步任务轮询，自动获取生成的图片
- 图片自动保存到本地目录
- 简洁的 API 接口

## 安装

```bash
git clone https://github.com/qtwaiter/modelscope-image-skill.git
cd modelscope-image-skill
pip install -r requirements.txt
```

## 配置

设置环境变量 `MODELSCOPE_API_KEY`：

```bash
export MODELSCOPE_API_KEY="your_api_key_here"
```

或者在代码中直接设置：

```python
import os
os.environ["MODELSCOPE_API_KEY"] = "your_api_key_here"
```

## 使用方法

### Python 代码

```python
from skill import ModelScopeImageSkill

# 初始化
skill = ModelScopeImageSkill()

# 生成图片
result = skill.generate_image(
    prompt="一只在草地上跑的橘猫",
    model="Tongyi-MAI/Z-Image-Turbo",  # 或 Qwen/Qwen-Image-2512
    size="1024x1024",
    output_filename="cat.jpg",
    output_dir="./images"
)

if result["success"]:
    print(f"图片已保存到: {result['file_path']}")
else:
    print(f"生成失败: {result['message']}")
```

### 命令行

```bash
python skill.py --prompt "一只在草地上跑的橘猫" --model "Tongyi-MAI/Z-Image-Turbo"
```

## 支持的模型

| 模型 ID | 描述 |
|---------|------|
| `Qwen/Qwen-Image-2512` | 通义千问图像生成模型 |
| `Tongyi-MAI/Z-Image-Turbo` | 通义万相 Turbo 模型 |

## API 参数

### generate_image()

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `prompt` | str | 必填 | 图片描述文本 |
| `model` | str | Tongyi-MAI/Z-Image-Turbo | 使用的模型 |
| `size` | str | 1024x1024 | 图片尺寸 |
| `output_filename` | str | result_image.jpg | 输出文件名 |
| `output_dir` | str | ./outputs | 输出目录 |
| `max_wait_time` | int | 300 | 最大等待时间（秒） |

## 返回结果

```python
{
    "success": True,
    "message": "图片生成成功！",
    "prompt": "一只在草地上跑的橘猫",
    "model": "Tongyi-MAI/Z-Image-Turbo",
    "size": "1024x1024",
    "file_path": "images/cat.jpg",
    "image_url": "https://muse-ai.oss-cn-hangzhou.aliyuncs.com/img/xxx.png"
}
```

## 获取 API Key

1. 访问 [ModelScope 开放平台](https://modelscope.cn/my/apis)
2. 登录账号
3. 创建 API Key

## 项目结构

```
modelscope-image-skill/
├── skill.py          # 主逻辑代码
├── skill.json        # Skill 配置
├── requirements.txt  # 依赖列表
├── tests/
│   ├── __init__.py
│   └── test_skill.py # 测试文件
└── README.md         # 英文说明
```

## 许可证

MIT
