# 豆包搜索 Custom API 参考

## 目录

- [接入](#接入)
- [请求](#请求)
- [响应](#响应)
- [错误码](#错误码)

## 接入

API Key（推荐）：

```http
POST https://open.feedcoopapi.com/search_api/web_search
Authorization: Bearer <API_KEY>
Content-Type: application/json
```

TOP 网关：

```http
POST https://mercury.volcengineapi.com?Action=WebSearch&Version=2025-01-01
Content-Type: application/json
```

TOP 网关使用火山 IAM AK/SK 签名，服务名为 `volc_torchlight_api`，区域为 `cn-beijing`。订阅套餐和按量后付费 API Key 独立计费；账号默认限流为 5 QPS，每个火山账号每月有 500 次免费额度，额度与 Global 版共用。

## 请求

公共字段：

| 字段 | 类型 | 必填 | 规则 |
|---|---|---:|---|
| `Query` | string | 是 | 1-100 字符，过长会截断；文档说明不支持多词搜索 |
| `SearchType` | string | 是 | `web` 或 `image` |
| `Count` | number | 否 | `web` 默认 10、最多 50；`image` 最多 5 |
| `QueryControl.QueryRewrite` | boolean | 否 | 默认 false；开启会增加耗时 |

`web` 请求示例：

```json
{
  "Query": "北京最新游玩攻略",
  "SearchType": "web",
  "Count": 10,
  "Filter": {
    "NeedContent": true,
    "NeedUrl": true,
    "Sites": "gov.cn|news.cn",
    "BlockHosts": "example.com",
    "AuthInfoLevel": 1
  },
  "TimeRange": "OneMonth",
  "QueryControl": { "QueryRewrite": false },
  "ContentFormats": "text",
  "Industry": "gov"
}
```

`web` 的 `Filter` 字段：

| 字段 | 类型 | 规则 |
|---|---|---|
| `NeedContent` | boolean | 仅返回有正文的结果，默认 false |
| `NeedUrl` | boolean | 仅返回有原文 URL；true 会过滤火山如意结果 |
| `Sites` | string | 指定站点，完整域名，最多 20 个，以 `|` 分隔 |
| `BlockHosts` | string | 屏蔽站点，完整域名，最多 5 个，以 `|` 分隔 |
| `AuthInfoLevel` | number | 0 不限制；1 仅非常权威，结果可能减少 |

其他 `web` 字段：`TimeRange` 可为 `OneDay`、`OneWeek`、`OneMonth`、`OneYear` 或 `YYYY-MM-DD..YYYY-MM-DD`；`ContentFormats` 可为 `text` 或 `markdown`；`Industry` 可为 `finance`、`game`、`gov`。行业搜索可能减少结果并过滤火山如意结果。

`image` 请求可传 `Query`、`SearchType: "image"`、`Count`，以及 `Filter.ImageWidthMin`、`ImageHeightMin`、`ImageWidthMax`、`ImageHeightMax`、`ImageShapes`。形状枚举为 `横长方形`、`竖长方形`、`方形`。

## 响应

```json
{
  "ResponseMetadata": {
    "RequestId": "...",
    "Action": "WebSearch",
    "Version": "2025-01-01",
    "Service": "volc_torchlight_api",
    "Region": "cn-beijing"
  },
  "Result": {
    "ResultCount": 0,
    "WebResults": [],
    "ImageResults": [],
    "SearchContext": { "OriginQuery": "...", "SearchType": "web" },
    "TimeCost": 0,
    "LogId": "...",
    "CardResults": []
  }
}
```

成功时读取 `Result`。`web` 读取 `WebResults`，优先 `Summary`（约 500-1000 字，适合大模型）而非 `Snippet`（约 200 字，仅适合列表展示）；需要正文时读取 `Content`。保留 `Title`、`SiteName`、`Url`、`PublishTime`、`AuthInfoDes`、`AuthInfoLevel` 和 `RankScore` 作为引用元数据。

`image` 读取 `ImageResults`，每项包含 `Title`、`SiteName`、`Url`、`PublishTime` 和 `Image`；`Image` 包含 `Url`、`Width`、`Height`、`Shape`，以及可能存在的 `BlurDes`、`Category`。

`CardResults` 是 `web` 结果中火山如意结构化结果的子集，可能包含天气、汇率、火车、航班、赛事、税率、宏观经济等卡片。只有在类型和字段明确时使用；不要臆测未返回的卡片字段。

## 错误码

| Code | 含义 | 处理 |
|---:|---|---|
| 10400 | ParamError | 检查 JSON、字段类型和必填字段 |
| 10401 | InvalidTopToken | 检查 TOP 网关 Token |
| 10402 | InvalidSearchType | 检查 `SearchType` 和服务开通状态 |
| 10403 | InvalidAccountId | 检查账号是否开通对应搜索服务 |
| 10406 | FreeQuotaExhausted | 检查控制台是否开通付费调用 |
| 10409 | SearchPackageModeUnsupported | 检查 API Key 是否适用于 Custom 版和当前搜索类型 |
| 10410 | SearchPackageUnavailable | 检查套餐是否开通或过期 |
| 10412 | SearchPackageQuotaExhausted | 升配套餐或切换按量后付费 API Key |
| 10500 | InnerError | 可退避后重试 |
| 700429 | FreeRateLimitExceeded | 降低并发、退避；默认 QPS 5 |

错误响应中 `ResponseMetadata.Error` 包含 `Code` 和 `Message`，且 `Result` 为 `null`。不要向用户暴露凭据或完整认证头。
