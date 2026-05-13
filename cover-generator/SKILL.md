---
name: 文章封面生成器
description: 使用即梦AI的文生图功能，根据文章标题和描述生成文章封面图并保存到本地。
---

# 即梦封面生成器

本技能提供使用即梦AI的文生图API，根据文章标题和描述生成封面图并保存到本地文件系统的功能。

## 使用方法
首先使用 ${SKILL_DIR}作为当前技能的目录。

1. **准备输入**：
   - 文章标题：描述内容的简洁标题(不要有空格和特殊字符)
   - 文章描述：提供更多上下文的简短描述(不要有空格和特殊字符)
   - 输出路径：生成的图像将保存的本地目录

2. **生成封面图**：
   运行提供的Python脚本来生成并保存封面图。

## 脚本
使用即梦AI API生成封面图的主脚本。

**使用**：
```bash
python ${SKILL_DIR}/scripts/generate_cover.py --title '文章标题' --description '文章描述' --output '输出目录'
```

**参数**：
- `--title`：文章标题（必填）
- `--description`：文章描述（必填）
- `--output`：输出目录（默认为当前目录）

## 依赖要求

- Python 3.6+
- requests库
- python-dotenv

## 示例

**输入**：
```bash
python ${SKILL_DIR}/scripts/generate_cover.py --title '人工智能的未来' --description '探索人工智能和机器学习的最新发展' --output 'covers'
```

**输出**：
生成的封面图保存到 `covers/cover.png`