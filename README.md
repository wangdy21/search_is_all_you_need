# Search Is All You Need

全网内容检索与智能分析系统 - 一站式学术/网页内容搜索、AI 摘要生成与论文下载平台。

## 项目概述

本项目是一个全栈 Web 应用，提供多源内容检索和 AI 智能分析功能：

**核心功能：**
- **多源聚合搜索**：同时从 arXiv、Bing、Semantic Scholar、知乎等多个数据源检索内容
- **智能内容分类**：自动识别搜索结果类型（学术论文、博客、问答、论坛、网页）
- **AI 内容分析**：使用大语言模型生成摘要、提取关键点、翻译内容
- **学术论文解析**：深度分析论文的研究方法、创新点、实验结果
- **PDF 下载管理**：支持 arXiv 论文 PDF 下载，含国内镜像加速
- **搜索历史记录**：保存搜索记录，支持快速回溯

**架构特点：**
- 前后端分离，RESTful API 设计
- 多数据源并发搜索，线程池异步执行
- 令牌桶算法速率限制，防止 API 滥用
- 多级缓存策略，减少重复请求
- 支持多 LLM 提供商（智谱 AI / DeepSeek）

## 技术栈

### 后端
| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 运行环境 |
| Flask | 3.0 | Web 框架 |
| Flask-CORS | 4.0 | 跨域支持 |
| SQLite | - | 数据存储（WAL 模式） |
| zhipuai | 2.0+ | 智谱 AI SDK |
| openai | 1.x | DeepSeek API（兼容接口） |
| arxiv | 2.0+ | arXiv 论文检索 |
| requests | 2.31+ | HTTP 请求（Bing / Semantic Scholar） |
| BeautifulSoup4 | 4.12+ | HTML 解析（Bing 搜索结果解析） |

### 前端
| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18.2 | UI 框架 |
| Vite | 5.0 | 构建工具 |
| Ant Design | 5.12 | UI 组件库 |
| Axios | 1.6 | HTTP 客户端 |
| Day.js | 1.11 | 日期处理 |

## 环境配置

### 1. 环境变量配置

复制示例配置文件并编辑：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下变量：

```bash
# ========== LLM API 配置 (二选一) ==========

# 智谱AI API密钥 (使用智谱时必填)
# 获取地址: https://open.bigmodel.cn/
ZHIPU_API_KEY=your_zhipu_api_key_here

# DeepSeek API密钥 (使用DeepSeek时必填)
# 获取地址: https://platform.deepseek.com/api_keys
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# ========== Flask 配置 ==========

# 安全密钥 (生产环境务必修改)
SECRET_KEY=your_random_secret_key

# 运行模式: development / production
FLASK_ENV=development

# 服务端口
FLASK_PORT=5000

# ========== 存储路径 ==========

# SQLite 数据库路径
DATABASE_PATH=data/search.db

# PDF 下载保存目录
DOWNLOAD_DIR=data/downloads

# ========== 网络代理 (可选) ==========

# 用于访问外部服务（当前搜索引擎国内可直接访问，一般无需配置）
# HTTP_PROXY=http://127.0.0.1:7890
# HTTPS_PROXY=http://127.0.0.1:7890
```

### 2. LLM 提供商配置

编辑 `.qoder/config.json`，选择 LLM 提供商：

```json
{
    "analysis_settings": {
        "provider": "deepseek",      // 可选: "zhipu" 或 "deepseek"
        "zhipu_model": "glm-4-flash",
        "deepseek_model": "deepseek-chat",
        "max_content_length": 4000,
        "temperature": 0.7
    }
}
```

## 安装部署

### 方式一：一键启动（推荐）

```bash
# 克隆项目
git clone https://github.com/your-username/search_is_all_you_need.git
cd search_is_all_you_need

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API 密钥

# 一键启动
bash run.sh
```

### 方式二：手动安装

#### 后端安装

```bash
# 创建虚拟环境
python3.8 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r backend/requirements.txt

# DeepSeek 支持 (可选)
pip install "openai>=1.0.0,<1.60.0"
```

#### 前端安装

```bash
# 需要 Node.js >= 18
cd frontend
npm install
npm run build
cd ..
```

## 运行说明

### 开发模式

```bash
# 终端1: 启动后端
source venv/bin/activate
python backend/app.py

# 终端2: 启动前端开发服务器 (可选，支持热更新)
cd frontend
npm run dev
```

- 后端 API: http://localhost:5000
- 前端开发: http://localhost:5173 (Vite)

### 生产模式

```bash
# 构建前端
cd frontend && npm run build && cd ..

# 启动服务 (Flask 静态文件托管)
python backend/app.py
```

访问 http://localhost:5000

## 功能使用教程

### 1. 多源搜索

在顶部搜索框输入关键词，勾选数据源后按回车搜索：

- **DuckDuckGo**: 通用网页搜索（底层使用 Bing 搜索引擎）
- **arXiv**: 学术预印本论文（直接调用 arXiv API）
- **Google Scholar**: 学术文献（底层使用 Semantic Scholar API）
- **知乎**: 中文问答内容（通过 Bing 站内搜索）

搜索结果会自动分类并显示来源标签。

### 2. AI 内容分析

点击搜索结果卡片上的「分析」按钮，可使用以下功能：

- **智能摘要**: 生成内容摘要和关键要点
- **内容翻译**: 将英文内容翻译为中文
- **论文解析**: 深度分析学术论文（仅限学术类结果）

### 3. PDF 下载

对于 arXiv 论文，点击「下载 PDF」按钮：

- 支持后台下载，可继续浏览
- 自动使用国内镜像加速
- 下载进度实时显示
- 完成后可直接打开文件

### 4. 搜索历史

点击右上角「历史」按钮查看搜索记录：

- 显示搜索时间和结果数量
- 点击记录可快速重新搜索
- 支持清空历史记录

### 5. 结果筛选

使用左侧筛选面板按类型过滤：

- 全部 / 学术 / 博客 / 问答 / 论坛 / 网页

### 6. 时间范围筛选

在筛选面板中选择时间范围，限定搜索结果的时间区间：

- **不限**（默认）：返回所有时间的结果
- **近一周**：仅返回最近 7 天内的内容
- **近一月**：仅返回最近 30 天内的内容
- **近一年**：仅返回最近 365 天内的内容
- **近三年**：仅返回最近 3 年内的内容

选择时间范围后，点击搜索按钮即可生效。

**各数据源支持情况：**

| 数据源 | 时间过滤支持 | 说明 |
|--------|------------|------|
| arXiv | 原生支持 | 通过 `submittedDate` 查询语法精确过滤 |
| Google Scholar | 原生支持 | 通过 Semantic Scholar API 的 `year` 参数过滤 |
| DuckDuckGo | 不支持 | Bing 搜索结果缺少可靠的时间元数据，忽略时间参数 |
| 知乎 | 不支持 | 基于 Bing 站内搜索，忽略时间参数 |

## API 接口说明

### 搜索接口

```
POST /api/search
Content-Type: application/json

{
    "query": "搜索关键词",
    "sources": ["duckduckgo", "arxiv", "scholar", "zhihu"],
    "filters": {
        "time_range": "month"
    }
}
```

`filters.time_range` 可选值：`"week"` | `"month"` | `"year"` | `"3years"` | `null`（不限）。

```
Response: {
    "results": [...],
    "total": 15,
    "sources_status": {"arxiv": "success", "duckduckgo": "success"}
}
```

### 分析接口

```
POST /api/analysis/summarize    # 生成摘要
POST /api/analysis/translate    # 翻译内容
POST /api/analysis/paper        # 论文分析

Request Body: {"content": "...", "target_lang": "zh"}
```

### 下载接口

```
POST /api/download/arxiv        # 开始下载
GET  /api/download/status/<id>  # 查询状态
GET  /api/download/file/<id>    # 获取文件
GET  /api/download/history      # 下载历史
```

### 历史接口

```
GET    /api/history             # 获取搜索历史
DELETE /api/history             # 清空历史
```

## 前端组件介绍

| 组件 | 路径 | 功能 |
|------|------|------|
| `App.jsx` | `src/App.jsx` | 主布局，整合所有组件 |
| `SearchBar.jsx` | `src/components/` | 搜索输入框和数据源选择 |
| `FilterPanel.jsx` | `src/components/` | 结果类型筛选面板 |
| `ResultList.jsx` | `src/components/` | 搜索结果列表容器 |
| `ResultItem.jsx` | `src/components/` | 单个结果卡片 |
| `AnalysisPanel.jsx` | `src/components/` | AI 分析抽屉面板 |
| `DownloadManager.jsx` | `src/components/` | 下载任务管理器 |
| `HistoryPanel.jsx` | `src/components/` | 搜索历史抽屉 |

**自定义 Hooks:**

| Hook | 功能 |
|------|------|
| `useSearch` | 搜索状态和操作管理 |
| `useAnalysis` | AI 分析状态管理 |
| `useDownload` | 下载任务状态管理 |

## 配置选项

### 速率限制配置

编辑 `.qoder/config.json`：

```json
{
    "rate_limits": {
        "arxiv": {"capacity": 5, "refill_rate": 0.33},
        "duckduckgo": {"capacity": 20, "refill_rate": 2.0},
        "zhihu": {"capacity": 3, "refill_rate": 0.2},
        "scholar": {"capacity": 10, "refill_rate": 1.0}
    }
}
```

### 搜索默认配置

```json
{
    "search_defaults": {
        "max_results_per_source": 15,
        "timeout_seconds": 60,
        "cache_expire_hours": 24,
        "default_sources": ["duckduckgo", "arxiv"]
    }
}
```

### HTTP 代理配置

如果需要通过代理访问外部服务，在 `.env` 中配置：

```bash
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

支持 HTTP/HTTPS/SOCKS5 代理。当前搜索引擎（Bing、Semantic Scholar）在国内网络下可直接访问，一般无需配置代理。

## 注意事项

### API 密钥安全

- `.env` 文件包含敏感信息，**已在 `.gitignore` 中排除**
- 切勿将 API 密钥提交到版本控制
- 生产环境建议使用环境变量或密钥管理服务

### 数据源限制

| 数据源 | 实际后端 | 限制说明 |
|--------|----------|----------|
| DuckDuckGo | Bing (cn.bing.com) | 结果偏向中文内容 |
| arXiv | arXiv API | 主要为英文论文，中文关键词可能无结果 |
| Google Scholar | Semantic Scholar API | 免费 API，有速率限制（自动重试） |
| 知乎 | Bing 站内搜索 | 通过 `site:zhihu.com` 限定结果范围 |

### 性能建议

- 首次搜索可能较慢（建立连接），后续会使用缓存
- 建议不要同时勾选过多数据源
- AI 分析功能会消耗 LLM API 额度

### 常见问题

**Q: 搜索返回空结果？**
- arXiv 仅支持英文搜索
- Semantic Scholar API 有速率限制，短时间内多次搜索可能触发 429 错误（系统会自动重试）
- 查看后端日志了解具体错误

**Q: AI 分析功能不可用？**
- 确认已配置有效的 API 密钥
- 检查 `config.json` 中的 `provider` 设置

**Q: PDF 下载失败？**
- arXiv 服务器可能临时不可用
- 系统会自动尝试国内镜像

## 目录结构

```
search_is_all_you_need/
├── backend/
│   ├── app.py              # Flask 应用入口
│   ├── config.py           # 配置管理
│   ├── models/             # 数据库模型
│   ├── routes/             # API 路由
│   ├── services/           # 业务服务
│   └── utils/              # 工具函数
├── frontend/
│   ├── src/
│   │   ├── components/     # React 组件
│   │   ├── hooks/          # 自定义 Hooks
│   │   ├── services/       # API 服务
│   │   └── styles/         # 样式文件
│   ├── package.json
│   └── vite.config.js
├── .qoder/
│   ├── agents/             # AI 代理模块
│   ├── skills/             # 技能模块
│   └── config.json         # 运行时配置
├── data/                   # 数据目录 (git ignored)
├── .env.example            # 环境变量模板
├── .gitignore
├── run.sh                  # 一键启动脚本
└── README.md
```

## License

MIT License
