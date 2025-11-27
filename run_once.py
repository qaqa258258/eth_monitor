"""
单次运行脚本 - 专为GitHub Actions设计
只运行一次检查，不进入循环
"""
import json
import sys
from datetime import datetime

from data_fetcher import DataFetcher
from indicator import calculate_all_indicators, get_latest_indicators
from signal_detector import SignalDetector

# 设置UTF-8编码
sys.stdout.reconfigure(encoding='utf-8')


def load_config(config_file: str = 'config.json') -> dict:
    """加载配置文件"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ 配置文件 {config_file} 不存在")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ 配置文件 {config_file} 格式错误")
        sys.exit(1)


def run_once():
    """运行一次检查"""
    print("=" * 80)
    print(f"🚀 ETH合约开单提醒系统 - GitHub Actions")
    print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 加载配置
    config = load_config()
    
    print(f"\n📊 交易对: {config['symbol']}")
    print(f"⏱️  时间周期: {config['timeframe']}")
    print(f"📈 BOLL参数: 周期={config['boll']['period']}, 标准差={config['boll']['std_dev']}")
    print(f"📉 RSI参数: 周期={config['rsi']['period']}, 超买={config['rsi']['overbought']}, 超卖={config['rsi']['oversold']}")
    print()
    
    # 初始化模块（GitHub Actions服务器在国外，不需要代理）
    data_fetcher = DataFetcher(proxy_url=None)  # 不使用代理
    signal_detector = SignalDetector(
        rsi_overbought=config['rsi']['overbought'],
        rsi_oversold=config['rsi']['oversold'],
        telegram_token=config['telegram'].get('bot_token'),
        telegram_chat_id=config['telegram'].get('chat_id'),
        proxy_url=None  # 不使用代理
    )
    
    # 加载历史信号
    signal_detector.load_history()
    
    print("🔌 正在连接交易所...")
    if not data_fetcher.test_connection():
        print("❌ 无法连接到交易所")
        sys.exit(1)
    
    print("✅ 连接成功\n")
    
    try:
        # 获取K线数据
        print(f"📡 正在获取 {config['symbol']} 的K线数据...")
        df = data_fetcher.fetch_kline_data(
            symbol=config['symbol'],
            timeframe=config['timeframe'],
            limit=100
        )
        
        if df is None:
            print("❌ 获取数据失败")
            sys.exit(1)
        
        print(f"✅ 获取到 {len(df)} 条K线数据")
        
        # 计算指标
        print("\n📊 计算技术指标...")
        df = calculate_all_indicators(
            df,
            boll_period=config['boll']['period'],
            boll_std=config['boll']['std_dev'],
            rsi_period=config['rsi']['period']
        )
        
        # 获取最新指标
        indicators = get_latest_indicators(df)
        
        print(f"💰 当前价格: ${indicators['close']:,.2f}")
        print(f"📈 RSI: {indicators['rsi']:.2f}")
        print(f"📊 BOLL位置: {indicators['boll_position']:.1f}%")
        
        # 检测信号
        signal = signal_detector.detect_signal(indicators)
        
        print(f"\n🎯 信号类型: {signal['signal_type'].value}")
        print(f"💪 信号强度: {signal['strength']:.1f}%")
        print(f"📝 原因: {signal['reason']}")
        
        # 发送告警
        signal_detector.send_alert(
            symbol=config['symbol'],
            signal=signal,
            via_telegram=True,
            via_console=True
        )
        
        # 保存信号历史
        signal_detector.save_history()
        
        print("\n✅ 检查完成！")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    run_once()
