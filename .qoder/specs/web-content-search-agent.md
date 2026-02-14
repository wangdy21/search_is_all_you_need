# search_is_all_you_need - 全网内容检索系统实施计划

## 技术栈

| 层级 | 技术选型 |
|------|---------|
| 后端 | Flask (Python) |
| 前端 | React 18 + Vite 5 + Ant Design 5 |
| LLM | 智谱AI (GLM-4) via zhipuai SDK |
| 搜索源 | DuckDuckGo + arXiv API + Google Scholar (scholarly) + 知乎(搜索引擎间接) |
| 数据库 | SQLite |
| 部署 | 单体部署 (Flask serve React 静态文件) |

## 项目目录结构

```
search_is_all_you_need/
├── .qoder/
│   ├── config.json                     # 限流参数、搜索默认值等非敏感配置
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── search_agent.py            # 搜索编排代理（多源并发搜索）
│   │   └── analysis_agent.py          # AI分析代理（智谱AI封装）
│   └── skills/
│       ├── __init__.py
│       ├── web_scraping_skill.py      # 网页抓取（知乎等内容提取）
│       └── pdf_download_skill.py      # PDF下载（arXiv论文）
├── backend/
│   ├── app.py                          # Flask入口，注册蓝图，serve静态文件
│   ├── config.py                       # 配置管理（读.env + config.json）
│   ├── requirements.txt
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py                 # SQLite连接、建表、迁移
│   │   └── schemas.py                  # 表结构定义
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── search.py                   # POST /api/search
│   │   ├── analysis.py                 # POST /api/analysis/*
│   │   ├── download.py                 # POST /api/download/arxiv, GET status
│   │   └── history.py                  # GET /api/history, DELETE clear
│   ├── services/
│   │   ├── __init__.py
│   │   ├── search_service.py           # 搜索聚合（调用search_agent + 缓存 + 分类）
│   │   ├── classification_service.py   # 基于URL规则的内容自动分类
│   │   ├── analysis_service.py         # AI分析（调用analysis_agent + 缓存）
│   │   ├── cache_service.py            # SQLite缓存读写
│   │   └── rate_limiter.py             # 令牌桶限流器
│   └── utils/
│       ├── __init__.py
│       └── logger.py                   # 统一日志
├── frontend/
│   ├── package.json
│   ├── vite.config.js                  # 开发代理到Flask后端
│   ├── index.html
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx                     # 主布局：搜索栏 + 筛选 + 结果 + 面板
│   │   ├── components/
│   │   │   ├── SearchBar.jsx           # 搜索框 + 多源选择
│   │   │   ├── FilterPanel.jsx         # 分类/日期/语言筛选
│   │   │   ├── ResultList.jsx          # 结果列表容器
│   │   │   ├── ResultItem.jsx          # 单条结果卡片
│   │   │   ├── AnalysisPanel.jsx       # AI分析侧滑抽屉
│   │   │   ├── DownloadManager.jsx     # 下载管理底部浮窗
│   │   │   └── HistoryPanel.jsx        # 搜索历史侧滑
│   │   ├── hooks/
│   │   │   ├── useSearch.js            # 搜索状态和API调用
│   │   │   ├── useAnalysis.js          # 分析状态和API调用
│   │   │   └── useDownload.js          # 下载任务管理
│   │   ├── services/
│   │   │   └── api.js                  # axios封装
│   │   └── styles/
│   │       └── global.css
├── data/                               # 运行时生成（SQLite数据库、下载PDF）
├── .env.example                        # 环境变量模板
├── .gitignore
└── run.sh                              # 一键启动脚本
```

## 数据库设计（SQLite）

**search_history** - 搜索历史
- id, query, filters(JSON), result_count, timestamp

**search_cache** - 搜索结果缓存（24h过期）
- id, query_hash(UNIQUE), results(JSON), timestamp, expire_at

**analysis_cache** - AI分析缓存（7天过期）
- id, content_hash(UNIQUE), analysis_type, result(JSON), timestamp

**download_records** - 下载记录
- id, title, url, pdf_path, status(pending/downloading/completed/failed), file_size, timestamp

## API设计

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/search | 多源搜索，参数: query, sources[], filters{} |
| POST | /api/analysis/summarize | 内容摘要 + 要点提取 |
| POST | /api/analysis/translate | 翻译为中文 |
| POST | /api/analysis/paper | 学术论文深度分析 |
| POST | /api/download/arxiv | 创建arXiv PDF下载任务 |
| GET  | /api/download/status/<id> | 查询下载状态 |
| GET  | /api/download/file/<id> | 获取已下载文件 |
| GET  | /api/history | 获取搜索历史 |
| DELETE | /api/history | 清空搜索历史 |

## 核心模块实现要点

### search_agent.py - 搜索编排代理
- `search_all_sources(query, sources, filters)`: 使用ThreadPoolExecutor并发调用各源，30s超时
- `search_arxiv(query)`: 使用`arxiv`库，提取title/authors/summary/pdf_url/published
- `search_duckduckgo(query)`: 使用`duckduckgo_search`的DDGS.text()
- `search_google_scholar(query)`: 使用`scholarly`库
- `search_zhihu(query)`: DuckDuckGo搜索`site:zhihu.com {query}`，再用web_scraping_skill提取

### analysis_agent.py - AI分析代理
- 初始化zhipuai客户端（GLM-4模型）
- `generate_summary(content)`: 生成摘要 + 3-5个关键点
- `translate_content(content, target_lang)`: 专业术语准确翻译
- `analyze_paper(paper_data)`: 提取研究方法/创新点/实验结果/结论

### rate_limiter.py - 令牌桶限流
- arXiv: 5令牌容量, 3秒/令牌恢复
- 知乎: 3令牌容量, 5秒/令牌恢复
- Scholar: 10令牌容量, 1秒/令牌恢复
- DuckDuckGo: 20令牌容量, 0.5秒/令牌恢复

### pdf_download_skill.py - PDF下载
- 流式下载 + 进度跟踪
- arXiv镜像源自动切换（arxiv.org → cn.arxiv.org）
- 后台线程下载，最大并发3个

## 实施步骤

### 步骤1: 项目基础搭建
1. 创建目录结构和所有`__init__.py`
2. `.gitignore` (.env, data/, node_modules/, __pycache__/, dist/)
3. `.env.example` (ZHIPU_API_KEY, SERPAPI_KEY, SECRET_KEY, DATABASE_PATH)
4. `.qoder/config.json` (限流参数、搜索默认值、下载配置)
5. `backend/config.py` (python-dotenv读取 + config.json合并)
6. `backend/requirements.txt`
7. `backend/models/database.py` + `schemas.py` (SQLite初始化)

### 步骤2: 后端工具层
1. `backend/utils/logger.py`
2. `backend/services/rate_limiter.py` (令牌桶算法)
3. `backend/services/cache_service.py`

### 步骤3: .qoder技能模块
1. `.qoder/skills/web_scraping_skill.py`:
   - fetch_page(url): requests + 随机UA + 超时10s
   - parse_zhihu_question(html): BeautifulSoup解析
   - extract_metadata(html): OpenGraph标签提取
2. `.qoder/skills/pdf_download_skill.py`:
   - download_arxiv_pdf(arxiv_id, save_dir): 流式下载 + 镜像切换
   - validate_pdf(path): 文件头校验
   - 后台线程池管理

### 步骤4: .qoder代理模块
1. `.qoder/agents/search_agent.py`: 五个搜索方法 + 并发编排
2. `.qoder/agents/analysis_agent.py`: zhipuai初始化 + 三个分析方法

### 步骤5: 后端业务服务
1. `backend/services/classification_service.py`: URL规则分类
2. `backend/services/search_service.py`: 缓存检查→搜索→分类→缓存写入
3. `backend/services/analysis_service.py`: 缓存检查→AI分析→缓存写入

### 步骤6: 后端API路由
1. `backend/routes/search.py`
2. `backend/routes/analysis.py`
3. `backend/routes/download.py`
4. `backend/routes/history.py`
5. `backend/app.py` (蓝图注册 + CORS + 静态文件 + 错误处理)

### 步骤7: 前端基础
1. `frontend/package.json` + `vite.config.js` (代理/api→Flask)
2. `frontend/src/services/api.js` (axios封装)
3. `frontend/src/styles/global.css`

### 步骤8: 前端Hooks
1. `useSearch.js` - 搜索状态管理
2. `useAnalysis.js` - 分析状态管理
3. `useDownload.js` - 下载任务管理

### 步骤9: 前端UI组件
1. SearchBar.jsx - 搜索框 + Checkbox多源选择
2. FilterPanel.jsx - 分类/日期/语言筛选
3. ResultList.jsx + ResultItem.jsx - 结果列表和卡片
4. AnalysisPanel.jsx - Drawer侧滑（摘要/论文分析/翻译Tab切换）
5. DownloadManager.jsx - Fixed底部浮窗进度条
6. HistoryPanel.jsx - Drawer侧滑历史列表
7. App.jsx - 主布局组合

### 步骤10: 集成部署
1. Vite build配置（输出到frontend/dist）
2. Flask serve frontend/dist静态文件
3. `run.sh`启动脚本（pip install → npm build → flask run）

## Python依赖 (requirements.txt)

```
Flask==3.0.0
Flask-CORS==4.0.0
zhipuai>=2.0.0
arxiv>=2.0.0
scholarly>=1.7.0
duckduckgo-search>=4.0.0
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=5.0.0
python-dotenv>=1.0.0
```

## 前端依赖 (package.json核心)

```
react ^18.2.0, react-dom ^18.2.0, axios ^1.6.0, antd ^5.12.0, dayjs ^1.11.0
@vitejs/plugin-react ^4.2.0, vite ^5.0.0
```

## 验证方案

1. **后端启动验证**: `cd backend && python app.py` 确认Flask启动无报错
2. **API接口验证**: 使用curl测试各API端点
   - `curl -X POST http://localhost:5000/api/search -H "Content-Type: application/json" -d '{"query":"machine learning","sources":["duckduckgo"]}'`
   - `curl http://localhost:5000/api/history`
3. **前端构建验证**: `cd frontend && npm run build` 确认无编译错误
4. **前端开发模式**: `cd frontend && npm run dev` 确认页面渲染正常
5. **端到端测试**: 通过前端界面执行搜索→查看结果→AI分析→下载PDF完整流程
6. **限流测试**: 连续快速发送请求，确认限流器正常工作
