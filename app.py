from flask import Flask, render_template, jsonify, request
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import pytz
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

TIMEFRAMES = {
    "M1": mt5.TIMEFRAME_M1,
    "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30,
    "H1": mt5.TIMEFRAME_H1
}

def initialize_mt5():
    if not mt5.initialize():
        logging.error("MT5初始化失败，请确保MetaTrader5已经启动并登录")
        return False
    
    # 检查是否成功连接
    if not mt5.terminal_info():
        logging.error("无法获取MT5终端信息")
        return False
    
    logging.info("MT5初始化成功")
    return True

def get_available_symbols():
    if not mt5.initialize():
        logging.error("MT5初始化失败")
        return []
    
    try:
        # 获取终端信息
        terminal_info = mt5.terminal_info()
        if terminal_info is None:
            logging.error("无法获取终端信息")
            return []
        logging.info(f"MT5终端连接状态: {terminal_info.connected}")
            
        # 获取所有可用的交易品种
        symbols = mt5.symbols_get()
        if symbols is None:
            logging.error("无法获取交易品种列表")
            return []
            
        # 获取所有已选择的交易品种（在市场报价中可见的）
        active_symbols = []
        for symbol in symbols:
            # 检查该品种是否在市场报价中可见
            if mt5.symbol_select(symbol.name, True):
                symbol_info = mt5.symbol_info(symbol.name)
                if symbol_info and symbol_info.visible:
                    active_symbols.append(symbol.name)
                    logging.info(f"找到活跃品种: {symbol.name}")
        
        if active_symbols:
            logging.info(f"找到以下活跃的交易品种: {active_symbols}")
            return sorted(active_symbols)  # 按字母顺序排序
        else:
            logging.warning("未找到活跃的交易品种，尝试获取所有可用的主要货币对")
            # 如果没有找到活跃的品种，获取所有可用的主要货币对
            major_symbols = []
            for symbol in symbols:
                if (('USD' in symbol.name or 'EUR' in symbol.name or 
                     'GBP' in symbol.name or 'JPY' in symbol.name) and
                    mt5.symbol_select(symbol.name, True)):
                    major_symbols.append(symbol.name)
            
            if major_symbols:
                logging.info(f"找到以下主要货币对: {major_symbols}")
                return sorted(major_symbols)
            return []
        
    except Exception as e:
        logging.error(f"获取交易品种信息时出错: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return []

def get_candlestick_data(symbol="EURUSD", timeframe=mt5.TIMEFRAME_M1, count=300):
    if not mt5.initialize():
        logging.error("MT5连接失败")
        return None
    
    # 检查交易品种是否可用
    symbols = mt5.symbols_get()
    if symbols is None:
        logging.error("无法获取交易品种列表")
        return None
    
    symbol_names = [sym.name for sym in symbols]
    if symbol not in symbol_names:
        logging.error(f"交易品种 {symbol} 不可用")
        return None
    
    # 获取UTC时间的数据
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
    if rates is None:
        logging.error(f"无法获取 {symbol} 的行情数据")
        return None
    
    logging.info(f"成功获取 {symbol} 的 {count} 根K线数据")
    
    # 转换为pandas DataFrame
    df = pd.DataFrame(rates)
    
    # 将时间戳转换为datetime，并设置为UTC时区
    df['time'] = pd.to_datetime(df['time'], unit='s', utc=True)
    
    # 转换为北京时间 (UTC+8)
    beijing_tz = pytz.timezone('Asia/Shanghai')
    df['time'] = df['time'].dt.tz_convert(beijing_tz)
    
    data = []
    for _, row in df.iterrows():
        data.append([
            row['time'].strftime('%Y-%m-%d %H:%M:%S'),
            float(row['open']),
            float(row['close']),
            float(row['low']),
            float(row['high']),
            float(row['tick_volume'])
        ])
    
    return data

@app.route('/')
def index():
    symbols = get_available_symbols()
    if not symbols:  # 如果没有找到打开的图表
        return "请先在MT5中打开至少一个图表", 400
    return render_template('index.html', symbols=symbols, timeframes=list(TIMEFRAMES.keys()))

@app.route('/get_data')
def get_data():
    symbol = request.args.get('symbol', '')
    if not symbol:
        return jsonify({'error': '请选择交易品种'})
    
    timeframe = request.args.get('timeframe', 'M1')
    if timeframe not in TIMEFRAMES:
        return jsonify({'error': '无效的时间周期'})
    
    data = get_candlestick_data(symbol=symbol, timeframe=TIMEFRAMES[timeframe])
    if data is None:
        return jsonify({'error': '获取数据失败，请检查MT5连接'})
    return jsonify({'data': data})

if __name__ == '__main__':
    if initialize_mt5():
        logging.info("服务器启动成功，请访问 http://localhost:5000")
        app.run(debug=True)
    else:
        logging.error("服务器启动失败，请检查MT5连接") 