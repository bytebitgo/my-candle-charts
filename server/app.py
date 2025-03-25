from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import jwt
import json
from redis import Redis
import uvicorn
import configparser
import os
from typing import Union

# 配置
config = configparser.ConfigParser()
try:
    # 使用UTF-8编码读取配置文件
    with open('config.ini', 'r', encoding='utf-8') as f:
        config.read_file(f)
except Exception as e:
    print(f"读取配置文件失败: {str(e)}")
    # 使用默认配置
    config['server'] = {
        'host': '0.0.0.0',
        'port': '8000'
    }
    config['jwt'] = {
        'secret_key': '1234567890',
        'algorithm': 'HS256',
        'access_token_expire_days': '365'
    }

# FastAPI应用
app = FastAPI(title="Candlestick Data API")

# 安全认证
security = HTTPBearer()

# 数据存储类
class DataStore:
    def __init__(self, use_redis: bool = False, redis_config: dict = None):
        self.use_redis = use_redis
        if use_redis and redis_config:
            self.redis_client = Redis(
                host=redis_config['host'],
                port=int(redis_config['port']),
                password=redis_config.get('password', 'mycandle'),
                decode_responses=True
            )
        else:
            self.memory_store = {}
            self.symbols = set()

    def set(self, key: str, value: str, ex: int = None):
        """存储数据"""
        if self.use_redis:
            self.redis_client.set(key, value, ex=ex)
        else:
            self.memory_store[key] = value

    def get(self, key: str) -> Optional[str]:
        """获取数据"""
        if self.use_redis:
            return self.redis_client.get(key)
        else:
            return self.memory_store.get(key)

    def sadd(self, key: str, value: str):
        """添加到集合"""
        if self.use_redis:
            self.redis_client.sadd(key, value)
        else:
            self.symbols.add(value)

    def smembers(self, key: str) -> set:
        """获取集合成员"""
        if self.use_redis:
            return self.redis_client.smembers(key)
        else:
            return self.symbols

# 初始化数据存储
try:
    redis_config = config['redis'] if 'redis' in config else {
        'host': os.getenv('REDIS_HOST', 'redis'),
        'port': os.getenv('REDIS_PORT', '6379'),
        'password': os.getenv('REDIS_PASSWORD', 'mycandle')
    }
    use_redis = bool(redis_config and redis_config.get('host'))
    data_store = DataStore(use_redis=use_redis, redis_config=redis_config)
    print(f"使用{'Redis' if use_redis else '内存'}存储数据")
except Exception as e:
    print(f"Redis连接失败，使用内存存储: {str(e)}")
    data_store = DataStore(use_redis=False)

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class CandlestickData(BaseModel):
    symbol: str
    timeframe: str
    data: List[Dict]
    timestamp: str

class TokenData(BaseModel):
    client_id: str
    exp: datetime

def create_access_token(client_id: str) -> str:
    """创建JWT token，过期时间以天为单位"""
    expire = datetime.utcnow() + timedelta(days=int(config['jwt']['access_token_expire_days']))
    to_encode = {"client_id": client_id, "exp": expire}
    encoded_jwt = jwt.encode(
        to_encode,
        config['jwt']['secret_key'],
        algorithm=config['jwt']['algorithm']
    )
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> TokenData:
    """验证JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            config['jwt']['secret_key'],
            algorithms=[config['jwt']['algorithm']]
        )
        return TokenData(**payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token已过期"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="无效的认证凭据"
        )

@app.post("/api/v1/kline")
async def update_kline_data(
    data: CandlestickData,
    token: TokenData = Depends(verify_token)
):
    """更新K线数据"""
    try:
        key = f"kline:{data.symbol}:{data.timeframe}"
        data_store.set(key, json.dumps(data.dict()))
        data_store.sadd("available_symbols", data.symbol)
        return {"status": "success", "message": "数据更新成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/kline/{base}/{quote}/{timeframe}")
async def get_kline_data(
    base: str,
    quote: str,
    timeframe: str,
    token: TokenData = Depends(verify_token)
):
    """获取K线数据"""
    try:
        symbol = f"{base}/{quote}"
        print(f"Received request for symbol: {symbol}, timeframe: {timeframe}")
        key = f"kline:{symbol}:{timeframe}"
        print(f"Looking for key: {key}")
        data = data_store.get(key)
        print(f"Found data: {data}")
        if not data:
            raise HTTPException(status_code=404, detail="数据未找到")
        return json.loads(data)
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/symbols")
async def get_available_symbols(token: TokenData = Depends(verify_token)):
    """获取可用的交易品种"""
    try:
        symbols = data_store.smembers("available_symbols")
        return list(symbols) if symbols else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 添加生成token的接口
@app.post("/api/v1/token")
async def generate_token(client_id: str):
    """生成新的访问令牌"""
    try:
        token = create_access_token(client_id)
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": f"{config['jwt']['access_token_expire_days']}天"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=config['server']['host'],
        port=int(config['server']['port']),
        reload=True
    ) 