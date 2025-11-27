"""
数据获取模块 - 从交易所获取价格和K线数据
"""
import ccxt
import pandas as pd
from typing import Dict, List, Optional


class DataFetcher:
    """交易所数据获取器"""
    
    def __init__(self, proxy_url: str = None):
        """
        初始化数据获取器
        
        Args:
            proxy_url: 代理地址，如 'http://127.0.0.1:10808'
        """
        self.proxies = None
        if proxy_url:
            self.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
        
        # 初始化币安交易所
        self.exchange = ccxt.binance({
            'proxies': self.proxies,
            'timeout': 30000,
            'enableRateLimit': True
        })
    
    def fetch_realtime_price(self, symbol: str) -> Optional[float]:
        """
        获取实时价格
        
        Args:
            symbol: 交易对，如 'ETH/USDT'
            
        Returns:
            当前价格，失败返回None
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            print(f"❌ 获取实时价格失败: {e}")
            return None
    
    def fetch_kline_data(self, symbol: str, timeframe: str = '15m', limit: int = 100) -> Optional[pd.DataFrame]:
        """
        获取K线数据
        
        Args:
            symbol: 交易对，如 'ETH/USDT'
            timeframe: 时间周期，如 '1m', '5m', '15m', '1h', '4h', '1d'
            limit: 获取的K线数量
            
        Returns:
            包含OHLCV数据的DataFrame，失败返回None
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # 转换时间戳为datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            return df
        except Exception as e:
            print(f"❌ 获取K线数据失败: {e}")
            return None
    
    def test_connection(self) -> bool:
        """
        测试交易所连接
        
        Returns:
            连接成功返回True，否则返回False
        """
        try:
            self.exchange.load_markets()
            print("✅ 交易所连接成功")
            return True
        except Exception as e:
            print(f"❌ 交易所连接失败: {e}")
            return False


if __name__ == '__main__':
    # 测试代码
    fetcher = DataFetcher(proxy_url='http://127.0.0.1:10808')
    
    if fetcher.test_connection():
        print("\n📊 获取ETH/USDT实时价格...")
        price = fetcher.fetch_realtime_price('ETH/USDT')
        if price:
            print(f"当前价格: ${price:.2f}")
        
        print("\n📈 获取15分钟K线数据...")
        df = fetcher.fetch_kline_data('ETH/USDT', '15m', limit=30)
        if df is not None:
            print(f"获取到 {len(df)} 条K线数据")
            print(df.tail())
