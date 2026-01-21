# ModelScope Image Generation Skill 开发指南

本文档记录了创建 ModelScope 图片生成 Skill 的完整过程，可作为创建其他 Claude Skill 的参考。

## 目录

1. [项目规划](#项目规划)
2. [技术调研](#技术调研)
3. [开发过程](#开发过程)
4. [遇到的坑](#遇到的坑)
5. [项目结构](#项目结构)
6. [关键代码解析](#关键代码解析)
7. [部署流程](#部署流程)
8. [后续优化建议](#后续优化建议)

---

## 项目规划

### 需求分析

- **目标**: 创建一个使用 ModelScope API 生成图片的 Claude Skill
- **支持模型**: 
  - `Qwen/Qwen-Image-2512` - 通义千问图像生成模型
  - `Tongyi-MAI/Z-Image-Turbo` - 通义万相 Turbo 模型
  - (最初尝试了 `black-forest-labs/FLUX.2-klein-9B`，但 API 返回 40212 错误，不支持)
- **输出**: 图片保存到本地目录

### Claude Skill 规范要求

根据 Claude Skill 规范，需要以下文件：

| 文件 | 说明 | 必须 |
|------|------|------|
| `SKILL.md` | Skill 元数据（name + description） | ✅ 必须 |
| `skill.json` | Skill 配置入口 | ✅ 必须 |
| `skill.py` | 主逻辑代码 | ✅ 必须 |
| `requirements.txt` | 依赖列表 | 推荐 |
| `README.md` | 使用文档 | 推荐 |
| `tests/` | 测试文件 | 推荐 |

---

## 技术调研

### ModelScope API 调研

#### 1. REST API 端点

```python
# 基础 URL
base_url = "https://api-inference.modelscope.cn/"

# 提交任务
POST {base_url}v1/images/generations
Headers:
  - Authorization: Bearer {api_key}
  - Content-Type: application/json
  - X-ModelScope-Async-Mode: true

# 查询任务状态
GET {base_url}v1/tasks/{task_id}
Headers:
  - Authorization: Bearer {api_key}
  - X-ModelScope-Task-Type: image_generation
```

#### 2. API 调用流程

```python
# 步骤 1: 提交任务
response = requests.post(
    f"{base_url}v1/images/generations",
    headers={**headers, "X-ModelScope-Async-Mode": "true"},
    data=json.dumps({
        "model": "Tongyi-MAI/Z-Image-Turbo",
        "prompt": "A golden cat"
    })
)
task_id = response.json()["task_id"]

# 步骤 2: 轮询任务状态
while True:
    result = requests.get(
        f"{base_url}v1/tasks/{task_id}",
        headers={**headers, "X-ModelScope-Task-Type": "image_generation"}
    )
    if result["task_status"] == "SUCCEED":
        # 获取图片
        image_url = result["output_images"][0]
        break
    elif result["task_status"] == "FAILED":
        break
    time.sleep(5)
```

#### 3. 重要发现

- **必须使用异步模式**: 添加 `X-ModelScope-Async-Mode: true` header
- **查询必须指定任务类型**: 添加 `X-ModelScope-Task-Type: image_generation` header
- **返回格式**: 成功时 `output_images` 数组包含图片 URL

---

## 开发过程

### Stage 1: 项目初始化

1. 创建项目目录
2. 创建 `IMPLEMENTATION_PLAN.md` (开发计划)
3. 创建基础文件结构

### Stage 2: 核心代码开发

#### skill.py 开发

```python
# 核心类结构
class ModelScopeImageSkill:
    def __init__(self, config=None):
        # 初始化 API Key 和请求头
        
    def generate_image(self, prompt, model, size, output_filename, output_dir, max_wait_time):
        # 生成图片主逻辑
        
    def list_models(self):
        # 列出支持的模型
```

#### skill.json 配置

```json
{
  "name": "modelscope-image-generator",
  "main": "skill.py",
  "skills": [
    {
      "name": "generate_image",
      "parameters": { ... }
    }
  ]
}
```

#### SKILL.md 元数据

**重要**: 必须使用 YAML frontmatter 格式：

```yaml
---
name: modelscope-image-generator
description: 使用 ModelScope API 生成图片的 Skill...
---
```

### Stage 3: 测试和调试

1. 测试所有支持的模型
2. 验证错误处理
3. 清理测试文件

---

## 遇到的坑

### 坑 1: API 只支持异步模式

**问题**: 直接调用 `POST /v1/images/generations` 返回 400 错误
```
{"errors":{"message":"image-gen task currently does not support synchronous calls..."}}
```

**解决**: 添加 `X-ModelScope-Async-Mode: true` header

### 坑 2: 无法查询任务结果

**问题**: 提交任务返回 `task_id`，但查询时返回 "task not found"

**解决**: 查询时需要添加 `X-ModelScope-Task-Type: image_generation` header

### 坑 3: FLUX 模型不支持

**问题**: 使用 `black-forest-labs/FLUX.2-klein-9B` 返回 40212 错误

**解决**: 从支持的模型列表中移除

### 坑 4: SKILL.md 格式错误

**问题**: 安装时提示 "Skills require a SKILL.md with name and description"

**解决**: 使用 YAML frontmatter 格式：
```yaml
---
name: skill-name
description: Skill description
---
```

### 坑 5: requests vs httpx

**问题**: 使用 `requests.HTTPStatusError` 但模块没有这个属性

**解决**: 使用 `requests.exceptions.HTTPError`

---

## 项目结构

```
modelscope-image-skill/
├── SKILL.md              # Skill 元数据 (YAML frontmatter + 说明)
├── skill.json            # Skill 配置 (入口 + 函数定义)
├── skill.py              # 主逻辑代码
├── requirements.txt      # Python 依赖
├── README.md             # 使用文档 (中文)
├── tests/
│   ├── __init__.py
│   └── test_skill.py     # 测试文件
└── .git/                 # Git 仓库
```

---

## 关键代码解析

### 1. Skill 类初始化

```python
def __init__(self, config: Optional[Dict[str, Any]] = None):
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
```

**要点**:
- 从环境变量读取 API Key，不硬编码
- 使用 `Optional` 类型提示

### 2. 图片生成主逻辑

```python
def generate_image(self, prompt, model, size, output_filename, output_dir, max_wait_time):
    # 1. 提交任务
    response = requests.post(
        f"{self.base_url}v1/images/generations",
        headers={**self.common_headers, "X-ModelScope-Async-Mode": "true"},
        data=json.dumps({"model": model, "prompt": prompt}, ensure_ascii=False).encode('utf-8'),
        timeout=120.0
    )
    task_id = response.json()["task_id"]
    
    # 2. 轮询任务状态
    while time.time() - start_time < max_wait_time:
        result = requests.get(
            f"{self.base_url}v1/tasks/{task_id}",
            headers={**self.common_headers, "X-ModelScope-Task-Type": "image_generation"},
            timeout=30.0
        )
        
        if result["task_status"] == "SUCCEED":
            # 3. 下载并保存图片
            image = Image.open(BytesIO(requests.get(image_url).content))
            image.save(file_path)
            return {"success": True, "file_path": str(file_path)}
        
        time.sleep(5)
```

**要点**:
- 异步提交 + 轮询获取结果
- 使用 `ensure_ascii=False` 支持中文 prompt
- 超时和错误处理

### 3. 返回结果格式

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

---

## 部署流程

### 1. 本地开发

```bash
# 初始化 Git
cd modelscope-image-skill
git init
git add -A
git commit -m "Initial commit"

# 本地测试
pip install -r requirements.txt
python skill.py --prompt "一只猫"
```

### 2. 推送到 GitHub

```bash
# 添加远程仓库
git remote add origin https://github.com/username/repo-name.git

# 推送
git push -u origin master
```

### 3. 安装 Skill

```bash
npx skills add https://github.com/username/repo-name
```

### 4. 更新 Skill

```bash
# 修改代码后
git add .
git commit -m "描述更改"
git push

# 重新安装
npx skills remove skill-name
npx skills add https://github.com/username/repo-name
```

---

## 后续优化建议

### 1. 功能增强

- [ ] 支持批量生成图片 (`n` 参数)
- [ ] 支持自定义图片尺寸
- [ ] 支持 negative prompt
- [ ] 添加进度回调

### 2. 错误处理

- [ ] 更详细的错误分类
- [ ] 重试机制
- [ ] 日志记录

### 3. 测试覆盖

- [ ] 单元测试
- [ ] Mock API 测试
- [ ] 集成测试

### 4. 文档完善

- [ ] 英文版 README
- [ ] API 文档
- [ ] 示例代码

---

## 参考资源

- [ModelScope 开放平台](https://modelscope.cn/my/apis)
- [Claude Skill 规范](https://platform.anthropic.com/docs/en/agents-and-tools/agent-skills)
- [官方示例代码](https://modelscope.cn/docs/api/)

---

## 总结

创建 Claude Skill 的关键步骤：

1. ✅ 理解需求和技术栈
2. ✅ 调研目标 API
3. ✅ 创建项目结构和必要文件
4. ✅ 实现核心功能
5. ✅ 测试所有支持的模型
6. ✅ 部署到 GitHub
7. ✅ 规范检查 (SKILL.md 格式)
8. ✅ 安装测试

**成功标准**: 
- ✅ Skill 安装成功
- ✅ 能正常调用 API 生成图片
- ✅ 图片保存到本地目录
