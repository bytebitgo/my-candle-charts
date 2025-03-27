# MT5 数据采集器

这是一个用于从 MetaTrader 5 (MT5) 交易平台采集实时行情数据的工具。它能够自动采集指定交易品种的K线数据，并将数据发送到指定的服务器。

## 功能特点

- 支持多个交易品种的数据采集
- 支持多个时间周期（M1、M5、M15、M30、H1）
- 自动重连机制
- 健康状态监控
- 状态保存和恢复
- 完善的日志记录
- Docker 容器化部署支持
- Windows 可执行文件支持

## Windows 可执行文件使用方法（推荐）

### 快速开始

1. 从 [Releases](https://github.com/your-username/mt5-collector/releases) 页面下载最新版本的 `mt5_collector.zip`

2. 解压下载的文件到任意目录

3. 修改 `config.ini` 配置文件：
```ini
[server]
url = https://your-server-url/api/v1
api_key = your-api-key

[mt5]
symbols = ["EURUSD", "GBPUSD", "USDJPY"]
reconnect_delay = 60
health_check_interval = 30
```

4. 双击运行 `mt5_collector.exe`

### 注意事项
- 确保已安装并登录 MetaTrader 5 客户端
- 程序会在当前目录下创建 `logs` 文件夹存放日志文件
- 运行时请勿删除配置文件和程序所在目录的其他文件

## 使用 Docker

### 快速开始

1. 拉取最新的 Docker 镜像：
```bash
docker pull ghcr.io/your-username/mt5-collector:latest
```

2. 准备配置文件：
创建 `config.ini` 文件，内容如下：
```ini
[server]
url = https://your-server-url/api/v1
api_key = your-api-key

[mt5]
symbols = ["EURUSD", "GBPUSD", "USDJPY"]
reconnect_delay = 60
health_check_interval = 30
```

3. 运行容器：
```bash
docker run -d \
  --name mt5-collector \
  -v $(pwd)/config.ini:/app/config.ini \
  -v $(pwd)/logs:/app/logs \
  ghcr.io/your-username/mt5-collector:latest
```

### 查看日志
```bash
docker logs -f mt5-collector
```

### 停止容器
```bash
docker stop mt5-collector
```

### 重启容器
```bash
docker restart mt5-collector
```

## 手动安装（不推荐）

如果您不想使用 Docker，也可以按照以下步骤手动安装：

### 系统要求

- Python 3.8 或更高版本
- MetaTrader 5 客户端
- 稳定的网络连接

### 安装步骤

1. 安装 MetaTrader 5 客户端并登录您的账户

2. 安装所需的 Python 包：
```bash
pip install -r requirements.txt
```

## 配置说明

配置项说明：
- `url`: 数据接收服务器的 API 地址
- `api_key`: 访问服务器的 API 密钥
- `symbols`: 需要采集的交易品种列表
- `reconnect_delay`: MT5 断开连接后的重连等待时间（秒）
- `health_check_interval`: 健康检查的时间间隔（秒）

## 日志说明

程序运行日志保存在 `logs` 目录下的 `collector.log` 文件中。日志文件会自动按大小轮转，每个文件最大 10MB，保留最近 5 个备份。

## 状态保存

程序会自动保存运行状态到 `collector_state.json` 文件中，包括：
- 最后一次成功获取数据的时间
- 连接尝试次数
- 最后一次连接时间

## 自动构建

### Windows 可执行文件
本项目使用 GitHub Actions 自动构建 Windows 可执行文件。每次推送到 main 分支或创建新的标签时，都会自动构建并发布新版本。

发布包括：
- Windows 64位可执行文件 (mt5_collector.exe)
- 配置文件模板 (config.ini)
- 使用说明文档 (README.md)
- 更新日志 (CHANGELOG.md)

您可以在 [Releases](https://github.com/your-username/mt5-collector/releases) 页面下载最新版本。

### Docker 镜像

如果您想自己构建 Docker 镜像，可以按照以下步骤操作：

1. 克隆代码仓库：
```bash
git clone https://github.com/your-username/mt5-collector.git
cd mt5-collector
```

2. 构建镜像：
```bash
docker build -t mt5-collector .
```

3. 运行容器：
```bash
docker run -d \
  --name mt5-collector \
  -v $(pwd)/config.ini:/app/config.ini \
  -v $(pwd)/logs:/app/logs \
  mt5-collector
```

## GitHub Actions 自动构建

本项目使用 GitHub Actions 进行自动化构建和发布。每次推送到 main 分支或创建新的标签时，都会自动构建并发布 Docker 镜像到 GitHub Container Registry。

要使用自动构建的镜像，只需要：

1. 确保您有权限访问 GitHub Container Registry
2. 使用以下命令拉取镜像：
```bash
docker pull ghcr.io/your-username/mt5-collector:latest
```

您也可以使用特定版本的标签，例如：
```bash
docker pull ghcr.io/your-username/mt5-collector:v1.0.0
``` 