import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import pytz
import requests
import json
import time
import logging
from typing import Optional, Dict, List
import configparser
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class MT5DataCollector:
    def __init__(self, config_path: str = 'config.ini'):
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

    def _load_config(self, config_path: str) -> configparser.ConfigParser:
        if not os.path.exists(config_path):
            self._create_default_config(config_path)
        
        config = configparser.ConfigParser()
        config.read(config_path)
        return config

    def _create_default_config(self, config_path: str):
        config = configparser.ConfigParser()
        config['server'] = {
            'url': 'http://your-server-url/api/v1',
            'api_key': 'your-api-key'
        }
        config['mt5'] = {
            'symbols': '["EURUSD", "GBPUSD", "USDJPY"]'
        }
        
        with open(config_path, 'w') as f:
            config.write(f)
        
        logging.info(f"Created default config file at {config_path}")

    def initialize_mt5(self) -> bool:
        """初始化MT5连接"""
        if not mt5.initialize():
            logging.error("MT5初始化失败")
            return False
        
        logging.info("MT5初始化成功")
        return True

    def get_candlestick_data(self, symbol: str, timeframe: str, count: int = 300) -> Optional[List[Dict]]:
        """获取K线数据"""
        if timeframe not in self.timeframes:
            logging.error(f"不支持的时间周期: {timeframe}")
            return None

        rates = mt5.copy_rates_from_pos(symbol, self.timeframes[timeframe], 0, count)
        if rates is None:
            logging.error(f"获取{symbol} {timeframe}数据失败")
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

        return data

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
                json=payload
            )
            response.raise_for_status()
            logging.info(f"成功发送{symbol} {timeframe}数据到服务器")
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"发送数据失败: {str(e)}")
            return False

    def run(self):
        """主运行循环"""
        if not self.initialize_mt5():
            return

        logging.info("开始数据采集...")
        
        try:
            while True:
                for symbol in self.symbols:
                    for timeframe in self.timeframes.keys():
                        data = self.get_candlestick_data(symbol, timeframe)
                        if data:
                            self.send_data_to_server(symbol, timeframe, data)
                
                # 等待下一次更新
                time.sleep(60)  # 每分钟更新一次
                
        except KeyboardInterrupt:
            logging.info("程序已停止")
        except Exception as e:
            logging.error(f"发生错误: {str(e)}")
        finally:
            mt5.shutdown()

if __name__ == "__main__":
    collector = MT5DataCollector()
    collector.run() 