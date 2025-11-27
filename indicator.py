"""
技术指标计算模块 - 计算BOLL和RSI指标
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple


def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
    """
    计算布林带指标
    
    Args:
        df: 包含close列的DataFrame
        period: 移动平均周期，默认20
        std_dev: 标准差倍数，默认2.0
        
    Returns:
        添加了boll_upper, boll_middle, boll_lower列的DataFrame
    """
    df = df.copy()
    
    # 计算中轨（移动平均线）
    df['boll_middle'] = df['close'].rolling(window=period).mean()
    
    # 计算标准差
    rolling_std = df['close'].rolling(window=period).std()
    
    # 计算上轨和下轨
    df['boll_upper'] = df['boll_middle'] + (std_dev * rolling_std)
    df['boll_lower'] = df['boll_middle'] - (std_dev * rolling_std)
    
    return df


def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    计算RSI指标（相对强弱指数）
    
    Args:
        df: 包含close列的DataFrame
        period: RSI周期，默认14
        
    Returns:
        添加了rsi列的DataFrame
    """
    df = df.copy()
    
    # 计算价格变化
    delta = df['close'].diff()
    
    # 分离涨跌
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # 计算平均涨跌幅
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    # 计算RS和RSI
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    return df


def calculate_all_indicators(df: pd.DataFrame, boll_period: int = 20, boll_std: float = 2.0, 
                            rsi_period: int = 14) -> pd.DataFrame:
    """
    计算所有指标
    
    Args:
        df: 包含OHLCV数据的DataFrame
        boll_period: 布林带周期
        boll_std: 布林带标准差倍数
        rsi_period: RSI周期
        
    Returns:
        包含所有指标的DataFrame
    """
    df = calculate_bollinger_bands(df, period=boll_period, std_dev=boll_std)
    df = calculate_rsi(df, period=rsi_period)
    
    return df


def get_latest_indicators(df: pd.DataFrame) -> Dict:
    """
    获取最新的指标值
    
    Args:
        df: 包含指标的DataFrame
        
    Returns:
        包含最新指标值的字典
    """
    if df is None or len(df) == 0:
        return {}
    
    latest = df.iloc[-1]
    
    return {
        'timestamp': latest.get('timestamp'),
        'close': latest['close'],
        'boll_upper': latest.get('boll_upper'),
        'boll_middle': latest.get('boll_middle'),
        'boll_lower': latest.get('boll_lower'),
        'rsi': latest.get('rsi'),
        # 计算价格相对于布林带的位置百分比
        'boll_position': ((latest['close'] - latest.get('boll_lower', 0)) / 
                         (latest.get('boll_upper', 1) - latest.get('boll_lower', 0)) * 100) 
                         if latest.get('boll_upper') and latest.get('boll_lower') else None
    }


if __name__ == '__main__':
    # 测试代码
    from data_fetcher import DataFetcher
    
    print("📊 测试指标计算模块...")
    
    fetcher = DataFetcher(proxy_url='http://127.0.0.1:10808')
    df = fetcher.fetch_kline_data('ETH/USDT', '15m', limit=100)
    
    if df is not None:
        # 计算所有指标
        df = calculate_all_indicators(df, boll_period=20, boll_std=2.0, rsi_period=14)
        
        # 显示最新指标
        indicators = get_latest_indicators(df)
        
        print("\n📈 最新指标值:")
        print(f"时间: {indicators['timestamp']}")
        print(f"价格: ${indicators['close']:.2f}")
        print(f"\nBOLL指标:")
        print(f"  上轨: ${indicators['boll_upper']:.2f}")
        print(f"  中轨: ${indicators['boll_middle']:.2f}")
        print(f"  下轨: ${indicators['boll_lower']:.2f}")
        print(f"  位置: {indicators['boll_position']:.1f}%")
        print(f"\nRSI: {indicators['rsi']:.2f}")
        
        # 显示最近5条数据
        print("\n最近5条完整数据:")
        print(df[['timestamp', 'close', 'boll_upper', 'boll_middle', 'boll_lower', 'rsi']].tail())
