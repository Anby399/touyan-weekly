# touyan

上市公司周报项目。采用 LangChain `create_agent`、PyMuPDF、Tavily、
PyMilvus、PyMySQL、FastAPI、FastMCP Streamable HTTP 和独立 Worker。
前端使用原生 HTML/CSS/JavaScript，不使用 React。

## 当前进度

已配置 uv 环境、依赖声明与应用配置。业务模块仍为空文件，尚不能启动 API、
Worker 或生成周报。Dockerfile 和 compose.yaml 仍为占位文件；本次未启动数据库。
未添加或运行测试，tests 目录保留原有空文件。

## 本地环境

在项目根目录执行：

```powershell
$env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'
uv sync --locked
# 仅首次配置时复制；不要覆盖已有 .env。
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Python 版本由 `.python-version` 指定为 3.11；`.venv` 保存虚拟环境，
`uv.lock` 固定依赖版本。无需手动激活环境，后续命令使用 `uv run`。
项目内 `.uv-cache` 用于 uv 缓存，不提交版本控制。
`.uv-python` 保存 uv 下载的 Python；上面的环境变量仅对当前终端有效。

## 配置说明

`app/config.py` 使用 pydantic-settings，读取项目根目录 `.env`，系统环境变量优先。
配置按需加载；密钥使用 SecretStr，配置加载不会连接外部服务。
当前允许密钥和模型名留空以准备环境，后续服务必须在实际使用前校验对应必填项。

| 配置组 | 用途 |
| --- | --- |
| APP / LOG | 监听地址、端口、时区和日志级别 |
| OPENAI / LLM | 聊天模型接口、密钥、模型名和调用参数 |
| EMBEDDING | 独立嵌入服务配置；维度需与模型和 Milvus 集合一致 |
| TAVILY / HTTP | 搜索密钥、搜索深度、结果数和网络超时 |
| MYSQL | 业务数据及后台任务队列的数据库连接 |
| MILVUS | 文档向量服务、数据库及集合 |
| CHUNK / RETRIEVAL | 分块大小、重叠及检索候选数量 |
| WORKER / JOB / STAGE | 任务轮询、并发、租约、重试和阶段超时 |
| AGENT / FACT_CHECK | Agent 迭代上限和核查修订次数 |
| MCP / SSE | MCP 入口、令牌和进度心跳 |
| DATA / PDF / EXPORT | 文件位置、上传大小、OCR 和导出配置 |

先填写 `.env` 中的模型名、聊天及嵌入密钥、Tavily 密钥、MySQL 密码，
并按实际服务修改 MySQL/Milvus 地址。模型名留空，不假设服务提供商支持某个模型。
更改 APP_PORT 后需同步调整 MCP_RESEARCH_URL。

MySQL 和 Milvus 是独立服务，uv 仅安装它们的 Python 客户端。
Word 转 PDF 另需 LibreOffice，Windows 可将 LIBREOFFICE_BINARY 设置为
`C:/Program Files/LibreOffice/program/soffice.exe`。
OCR 默认关闭；启用时另需 Tesseract 及中文、英文语言数据。
这些服务和系统程序不由 uv 安装。

配置项当前仅提供定义；对应业务模块完成后才会实际生效。
