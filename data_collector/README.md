# MT5 数据采集器

这是一个用于从 MetaTrader 5 (MT5) 交易平台采集实时行情数据的工具。它能够自动采集指定交易品种的K线数据，并将数据发送到指定的服务器。

## 功能特点

- 支持多个交易品种的数据采集
- 支持多个时间周期（M1、M5、M15、M30、H1）
- 自动重连机制
- 健康状态监控
- 状态保存和恢复
- 完善的日志记录

## 系统要求

- Python 3.8 或更高版本
- MetaTrader 5 客户端
- 稳定的网络连接

## 安装步骤

1. 安装 MetaTrader 5 客户端并登录您的账户

2. 安装所需的 Python 包：
```bash
pip install -r requirements.txt
```

## 配置说明

在运行程序前，需要配置 `config.ini` 文件。配置文件包含以下内容：

```ini
[server]
url = https://your-server-url/api/v1
api_key = your-api-key

[mt5]
symbols = ["EURUSD", "GBPUSD", "USDJPY"]
reconnect_delay = 60
health_check_interval = 30
```

配置项说明：
- `url`: 数据接收服务器的 API 地址
- `api_key`: 访问服务器的 API 密钥
- `symbols`: 需要采集的交易品种列表
- `reconnect_delay`: MT5 断开连接后的重连等待时间（秒）
- `health_check_interval`: 健康检查的时间间隔（秒）

## 运行程序

```bash
python collector.py
```

程序启动后会自动：
1. 连接到 MT5 客户端
2. 开始采集配置的交易品种数据
3. 将数据发送到指定服务器
4. 在出现连接问题时自动重连

## 日志说明

程序运行日志保存在 `logs` 目录下的 `collector.log` 文件中。日志文件会自动按大小轮转，每个文件最大 10MB，保留最近 5 个备份。

## 状态保存

程序会自动保存运行状态到 `collector_state.json` 文件中，包括：
- 最后一次成功获取数据的时间
- 连接尝试次数
- 最后一次连接时间

## 注意事项

1. 确保 MT5 客户端已经登录并保持运行
2. 检查网络连接是否稳定
3. 确保服务器 API 密钥正确且未过期
4. 定期检查日志文件，及时发现并处理异常情况 