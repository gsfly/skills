---
name: wechat-publisher
description: 一键发布 Markdown 到微信公众号草稿箱。基于 wenyan-cli，支持多主题、代码高亮、图片自动上传。
---

# wechat-publisher

**一键发布 Markdown 文章到微信公众号草稿箱**

基于 [wenyan-cli](https://github.com/caol64/wenyan-cli) 封装的 skill。

## 功能

- ✅ Markdown 自动转换为微信公众号格式
- ✅ 自动上传图片到微信图床
- ✅ 一键推送到草稿箱
- ✅ 多主题支持（代码高亮、Mac 风格代码块）
- ✅ 支持本地和网络图片

## 整体流程

### 1. 安装 wenyan-cli
**验证安装：**
```bash
wenyan --help
```
如果未安装则需要执行以下命令安装
```bash
npm install -g @wenyan-md/cli
```

### 2. 读取微信公众号凭证
从当前技能目录下的.env文件中读取

### 3. 准备 Markdown 文件

文件顶部**必须**包含完整的 frontmatter（wenyan 强制要求）：

```markdown
---
title: 文章标题（必填！）
cover: https://example.com/cover.jpg  # 封面图（必填！）
---

# 正文开始
你的内容...
```

**注意**：封面图如果没有，需调用'文章封面生成技能'生成到本地，然后markdown文件中使用相对路径
例如  cover: ./cover.png

### 4. 发布文章

**直接使用 wenyan-cli**
```bash
$env:WECHAT_APP_ID='your_wechat_app_id'; 
$env:WECHAT_APP_SECRET='your_wechat_app_secret';
wenyan publish -f article.md -t lapis -h solarized-light;
```

## 主题选项
wenyan-cli 支持多种主题：

**内置主题：**
- `default` - 默认主题
- `lapis` - 青金石（推荐）
- `phycat` - 物理猫
- 更多主题见：https://github.com/caol64/wenyan-core/tree/main/src/assets/themes

**代码高亮主题：**
- `atom-one-dark` / `atom-one-light`
- `dracula`
- `github-dark` / `github`
- `monokai`
- `solarized-dark` / `solarized-light` (推荐)
- `xcode`

**使用示例：**
```bash
# 使用 lapis 主题 + solarized-light 代码高亮
$env:WECHAT_APP_ID='your_wechat_app_id'; 
$env:WECHAT_APP_SECRET='your_wechat_app_secret';
wenyan publish -f article.md -t lapis -h solarized-light

# 使用 phycat 主题 + GitHub 代码高亮
$env:WECHAT_APP_ID='your_wechat_app_id'; 
$env:WECHAT_APP_SECRET='your_wechat_app_secret';
wenyan publish -f article.md -t phycat -h github

# 关闭 Mac 风格代码块
$env:WECHAT_APP_ID='your_wechat_app_id'; 
$env:WECHAT_APP_SECRET='your_wechat_app_secret';
wenyan publish -f article.md -t lapis --no-mac-style

# 关闭链接转脚注
$env:WECHAT_APP_ID='your_wechat_app_id'; 
$env:WECHAT_APP_SECRET='your_wechat_app_secret';
wenyan publish -f article.md -t lapis --no-footnote
```

## 自定义主题

### 临时使用自定义主题
```bash
$env:WECHAT_APP_ID='your_wechat_app_id'; 
$env:WECHAT_APP_SECRET='your_wechat_app_secret';
wenyan publish -f article.md -c /path/to/custom-theme.css
```

### 安装自定义主题（永久）
```bash
# 从本地文件安装
wenyan theme --add --name my-theme --path /path/to/theme.css

# 从网络安装
wenyan theme --add --name my-theme --path https://example.com/theme.css

# 使用已安装的主题
wenyan publish -f article.md -t my-theme

# 删除主题
wenyan theme --rm my-theme
```

### 列出所有主题
```bash
wenyan theme -l
```

### 图片支持
- ✅ 本地路径：`![](./images/photo.jpg)`
- ✅ 绝对路径：`![](/Users/bruce/photo.jpg)`
- ✅ 网络图片：`![](https://example.com/photo.jpg)`

所有图片会自动上传到微信图床！

会自动添加代码高亮和 Mac 风格装饰。


## 参考资料
- wenyan-cli GitHub: https://github.com/caol64/wenyan-cli
- wenyan 官网: https://wenyan.yuzhi.tech
- 微信公众号 API 文档: https://developers.weixin.qq.com/doc/offiaccount/
- IP 白名单配置: https://yuzhi.tech/docs/wenyan/upload

## License
Apache License 2.0 (继承自 wenyan-cli)