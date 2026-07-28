---
name: doubao-custom-web-search
description: 使用豆包搜索 Custom 版 API 执行网页或图片联网搜索，并将结果整理为带来源、时间和权威度说明的回答。用户要求搜索最新信息、查网页、查图片、验证事实、获取天气/赛事/交通/价格等实时数据，或明确提到豆包搜索、联网搜索、Custom 搜索 API 时使用。
---

# 豆包 Custom 联网搜索

使用豆包搜索 Custom API 获取实时网页或图片结果。将搜索结果视为外部证据，不把搜索摘要自动当作事实；回答时保留来源 URL、站点、发布时间和权威度，区分搜索结果与模型推断。

详细字段、响应结构和错误码见 [references/api-reference.md](references/api-reference.md)。需要调用 API 时先读该文件。

## 使用执行脚本

调用 API 时使用 [scripts/doubao_search.py](scripts/doubao_search.py)，不要在每次任务中重新手写 HTTP 客户端。脚本只依赖 Python 标准库，默认输出完整 JSON 响应，供后续回答提取来源和结果。

先设置凭据，再执行搜索：

```powershell
$env:DOUBAO_SEARCH_API_KEY = "<API_KEY>"
python scripts/doubao_search.py --query "北京最新天气" --type web --count 5 --need-content --need-url
python scripts/doubao_search.py --query "北京故宫" --type image --count 5 --image-shapes 横长方形
```

常用参数对应 API 字段：`--sites`、`--block-hosts`、`--auth-info-level`、`--time-range`、`--content-formats`、`--industry`、`--query-rewrite`，图片参数为 `--image-width-min`、`--image-height-min`、`--image-width-max`、`--image-height-max`、`--image-shapes`。脚本会校验 `Query`、`SearchType` 和 `Count`，缺少 `DOUBAO_SEARCH_API_KEY` 或 API 返回错误时以非零状态退出。

脚本默认使用 API Key URL。如确需测试代理或兼容端点，可传 `--endpoint`；不要把 Key 作为命令行参数传入，避免进入 shell 历史记录。

## 凭据与接入

优先使用 API Key 接入：

- URL：`https://open.feedcoopapi.com/search_api/web_search`
- Method：`POST`
- Header：`Authorization: Bearer <API_KEY>`、`Content-Type: application/json`
- 从环境变量或安全凭据存储读取 Key；绝不把 Key 写入代码、日志、回答或提交内容。

只有用户明确要求或已有火山 IAM AK/SK 配置时才使用 TOP 网关接入：

- URL：`https://mercury.volcengineapi.com?Action=WebSearch&Version=2025-01-01`
- Service：`volc_torchlight_api`
- Region：`cn-beijing`
- 使用火山 IAM 的标准签名流程；不要自行伪造签名。

## 执行流程

1. 判断意图：普通事实/实时信息使用 `SearchType: "web"`；用户明确要图片、图片链接或视觉素材时使用 `SearchType: "image"`。
2. 将查询压缩为单一、明确的搜索词。`Query` 必须为 1-100 个字符；文档说明不支持多词搜索。需要多个独立事实时分开查询，并遵守 QPS。
3. 根据任务选择过滤器：大模型阅读网页使用 `Filter.NeedContent: true`，优先 `Summary`；需要可点击来源使用 `Filter.NeedUrl: true`，但这会过滤火山如意结果；指定来源使用 `Sites`，排除来源使用 `BlockHosts`；追求权威性使用 `Filter.AuthInfoLevel: 1`；时间敏感问题使用 `TimeRange`；行业搜索使用 `Industry: finance`、`game` 或 `gov`。
4. `web` 的 `Count` 默认 10、最多 50；`image` 的 `Count` 最多 5。图片可用尺寸和形状过滤。仅在需要时启用 `QueryControl.QueryRewrite: true`，因为会增加耗时。
5. 检查 HTTP/响应错误。成功响应有 `Result`；失败时 `Result` 为 `null`。可恢复的内部错误有限重试并退避；不要对参数、鉴权、套餐或额度错误盲目重试。
6. 整理答案：先给结论，再列关键证据；每条关键事实尽量绑定来源。网页结果优先引用 `Summary`，不要只用 `Snippet` 生成复杂结论。对冲突来源说明差异，并以发布时间和权威度辅助判断。

## 回答约束

- 明确标注检索时间；涉及“最新”“今天”“当前”的内容必须实际搜索，不凭记忆回答。
- 不捏造没有返回的 URL、发布时间、作者、价格或结论。
- `RankScore` 只是相关性分数，不等于真实性；`AuthInfoLevel` 越低表示越权威，1 为“非常权威”。
- 图片回答返回图片标题、图片 URL、落地页 URL（如有）、站点和尺寸；不要把图片搜索结果当作网页正文证据。
- API Key、AK、SK、Bearer Token 和完整请求头属于敏感信息，输出示例时使用占位符。
- 默认用中文回答，除非用户使用其他语言。

## 常见错误处理

按 [references/api-reference.md](references/api-reference.md) 的错误表处理。`10400` 检查 JSON 和必填字段，`10401` 检查 TOP Token，`10402` 检查搜索类型，`10403` 检查账号权限；`10406`、`10409`、`10410`、`10412` 检查额度、套餐或 API Key 类型。`10500` 可退避重试，`700429` 应降低并发并退避。
