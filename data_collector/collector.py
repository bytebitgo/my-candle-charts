import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import pytz
import requests
import json
import time
import logging
from typing import Optional, Dict, List
import configparser
import os
import sys
from logging.handlers import RotatingFileHandler
import threading
import signal

# 配置日志
def setup_logger(log_path: str = 'logs'):
    if not os.path.exists(log_path):
        os.makedirs(log_path)
        
    log_file = os.path.join(log_path, 'collector.log')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # 文件处理器，限制单个文件大小为10MB，保留5个备份
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

class MT5DataCollector:
    def __init__(self, config_path: str = 'config.ini'):
        self.logger = setup_logger()
        self.config = self._load_config(config_path)
        self.server_url = self.config['server']['url']
        self.api_key = self.config['server']['api_key']
        self.symbols = json.loads(self.config['mt5']['symbols'])
        self.timeframes = {
            'M1': mt5.TIMEFRAME_M1,
            'M5': mt5.TIMEFRAME_M5,
            'M15': mt5.TIMEFRAME_M15,
            'M30': mt5.TIMEFRAME_M30,
            'H1': mt5.TIMEFRAME_H1
        }
        self.last_connection_time = None
        self.connection_attempts = 0
        self.max_connection_attempts = 5
        self.running = False
        self.health_check_interval = 30  # 30秒检查一次健康状态
        self.reconnect_delay = 60  # 重连等待时间（秒）
        self.last_data_time = {}  # 记录每个品种最后一次成功获取数据的时间
        
        # 注册信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """处理进程信号"""
        self.logger.info(f"收到信号 {signum}，准备安全退出...")
        self.running = False

    def _load_config(self, config_path: str) -> configparser.ConfigParser:
        if not os.path.exists(config_path):
            self._create_default_config(config_path)
        
        config = configparser.ConfigParser()
        config.read(config_path, encoding='utf-8')
        return config

    def _create_default_config(self, config_path: str):
        config = configparser.ConfigParser()
        config['server'] = {
            'url': 'https://localhost:8443/api/v1',
            'api_key': 'your-api-key'
        }
        config['mt5'] = {
            'symbols': '["EURUSD", "GBPUSD", "USDJPY"]',
            'reconnect_delay': '60',
            'health_check_interval': '30'
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            config.write(f)
        
        self.logger.info(f"创建默认配置文件：{config_path}")

    def _save_state(self):
        """保存当前状态"""
        state = {
            'last_data_time': self.last_data_time,
            'connection_attempts': self.connection_attempts,
            'last_connection_time': self.last_connection_time.isoformat() if self.last_connection_time else None
        }
        
        try:
            with open('collector_state.json', 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存状态失败: {str(e)}")

    def _load_state(self):
        """加载上次的状态"""
        try:
            if os.path.exists('collector_state.json'):
                with open('collector_state.json', 'r', encoding='utf-8') as f:
                    state = json.load(f)
                self.last_data_time = state.get('last_data_time', {})
                self.connection_attempts = state.get('connection_attempts', 0)
                last_connection_time = state.get('last_connection_time')
                if last_connection_time:
                    self.last_connection_time = datetime.fromisoformat(last_connection_time)
        except Exception as e:
            self.logger.error(f"加载状态失败: {str(e)}")

    def initialize_mt5(self) -> bool:
        """初始化MT5连接"""
        try:
            if not mt5.initialize():
                self.logger.error(f"MT5初始化失败: {mt5.last_error()}")
                return False
            
            self.last_connection_time = datetime.now()
            self.connection_attempts = 0
            self.logger.info("MT5初始化成功")
            return True
        except Exception as e:
            self.logger.error(f"MT5初始化异常: {str(e)}")
            return False

    def check_connection(self) -> bool:
        """检查MT5连接状态"""
        try:
            if not mt5.terminal_info():
                self.logger.error("MT5连接已断开")
                return False
            return True
        except Exception as e:
            self.logger.error(f"检查MT5连接状态失败: {str(e)}")
            return False

    def reconnect(self) -> bool:
        """重新连接MT5"""
        if self.connection_attempts >= self.max_connection_attempts:
            self.logger.error("达到最大重试次数，程序退出")
            self.running = False
            return False

        self.connection_attempts += 1
        self.logger.info(f"尝试重新连接MT5 (第{self.connection_attempts}次)")
        
        try:
            mt5.shutdown()
            time.sleep(self.reconnect_delay)
            return self.initialize_mt5()
        except Exception as e:
            self.logger.error(f"重新连接失败: {str(e)}")
            return False

    def get_candlestick_data(self, symbol: str, timeframe: str, count: int = 300) -> Optional[List[Dict]]:
        """获取K线数据"""
        if timeframe not in self.timeframes:
            self.logger.error(f"不支持的时间周期: {timeframe}")
            return None

        try:
            rates = mt5.copy_rates_from_pos(symbol, self.timeframes[timeframe], 0, count)
            if rates is None:
                self.logger.error(f"获取{symbol} {timeframe}数据失败: {mt5.last_error()}")
                return None

            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s', utc=True)
            
            # 转换为北京时间
            beijing_tz = pytz.timezone('Asia/Shanghai')
            df['time'] = df['time'].dt.tz_convert(beijing_tz)

            # 转换为列表格式
            data = []
            for _, row in df.iterrows():
                data.append({
                    'time': row['time'].strftime('%Y-%m-%d %H:%M:%S'),
                    'open': float(row['open']),
                    'close': float(row['close']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'volume': float(row['tick_volume'])
                })

            # 更新最后获取数据的时间
            key = f"{symbol}_{timeframe}"
            self.last_data_time[key] = datetime.now().isoformat()
            return data
            
        except Exception as e:
            self.logger.error(f"获取{symbol} {timeframe}数据异常: {str(e)}")
            return None

    def send_data_to_server(self, symbol: str, timeframe: str, data: List[Dict]) -> bool:
        """发送数据到服务器"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'symbol': symbol,
            'timeframe': timeframe,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }

        try:
            response = requests.post(
                f"{self.server_url}/kline",
                headers=headers,
                json=payload,
                verify=True  # 使用系统的证书验证
            )
            response.raise_for_status()
            self.logger.info(f"成功发送{symbol} {timeframe}数据到服务器")
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"发送数据失败: {str(e)}")
            return False

    def health_check(self):
        """健康检查线程"""
        while self.running:
            try:
                if not self.check_connection():
                    self.logger.warning("健康检查：MT5连接异常")
                    if not self.reconnect():
                        break
                time.sleep(self.health_check_interval)
            except Exception as e:
                self.logger.error(f"健康检查异常: {str(e)}")
                time.sleep(self.health_check_interval)

    def run(self):
        """主运行循环"""
        self._load_state()
        
        if not self.initialize_mt5():
            return

        self.running = True
        self.logger.info("开始数据采集...")
        
        # 启动健康检查线程
        health_check_thread = threading.Thread(target=self.health_check)
        health_check_thread.daemon = True
        health_check_thread.start()
        
        try:
            while self.running:
                if not self.check_connection():
                    if not self.reconnect():
                        break
                    continue

                for symbol in self.symbols:
                    for timeframe in self.timeframes.keys():
                        if not self.running:
                            break
                        
                        data = self.get_candlestick_data(symbol, timeframe)
                        if data:
                            self.send_data_to_server(symbol, timeframe, data)
                
                # 保存当前状态
                self._save_state()
                
                # 等待下一次更新
                time.sleep(60)  # 每分钟更新一次
                
        except KeyboardInterrupt:
            self.logger.info("收到键盘中断信号")
        except Exception as e:
            self.logger.error(f"主循环发生错误: {str(e)}")
        finally:
            self.running = False
            self._save_state()
            health_check_thread.join(timeout=5)
            mt5.shutdown()
            self.logger.info("程序已安全退出")

if __name__ == "__main__":
    collector = MT5DataCollector()
    collector.run() 