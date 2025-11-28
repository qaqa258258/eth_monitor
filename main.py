"""
ETH合约开单提醒系统 - 命令行监控版本
基于BOLL + RSI策略的交易信号监控
"""
import json
import time
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


def print_header(config: dict):
    """打印启动信息"""
    print("=" * 80)
    print("🚀 ETH合约开单提醒系统 - 命令行监控")
    print("=" * 80)
    print(f"📊 交易对: {config['symbol']}")
    print(f"⏱️  时间周期: {config['timeframe']}")
    print(f"🔄 检查间隔: {config['check_interval']}秒")
    print(f"📈 BOLL参数: 周期={config['boll']['period']}, 标准差={config['boll']['std_dev']}")
    print(f"📉 RSI参数: 周期={config['rsi']['period']}, 超买={config['rsi']['overbought']}, 超卖={config['rsi']['oversold']}")
    print(f"🌐 代理: {config['proxy']}")
    print("=" * 80)
    print("\n🔍 策略说明:")
    print("  🟢 做多信号: 价格触及或跌破下轨 (RSI仅供参考)")
    print("  🔴 做空信号: 价格触及或突破上轨 (RSI仅供参考)")
    print("  ⬆️ 平多信号: 持有多单且价格回到中轨以上")
    print("  ⬇️ 平空信号: 持有空单且价格回到中轨以下")
    print("=" * 80)
    print()


def print_status(symbol: str, indicators: dict, signal: dict):
    """打印当前状态"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 获取指标值
    price = indicators.get('close', 0)
    rsi = indicators.get('rsi', 0)
    boll_upper = indicators.get('boll_upper', 0)
    boll_middle = indicators.get('boll_middle', 0)
    boll_lower = indicators.get('boll_lower', 0)
    boll_position = indicators.get('boll_position', 0)
    
    # 信号类型和强度
    signal_type = signal['signal_type'].value
    strength = signal['strength']
    reason = signal['reason']
    
    # 选择emoji
    if strength > 0:
        emoji_map = {
            '做多': '🟢',
            '做空': '🔴',
            '平多': '⬆️',
            '平空': '⬇️'
        }
        emoji = emoji_map.get(signal_type, '⚪')
    else:
        emoji = '⚪'
    
    # 打印状态
    print(f"[{now}] {symbol}")
    print(f"  💰 价格: ${price:,.2f}")
    print(f"  📊 BOLL: 上轨=${boll_upper:,.2f} | 中轨=${boll_middle:,.2f} | 下轨=${boll_lower:,.2f} | 位置={boll_position:.1f}%")
    print(f"  📈 RSI: {rsi:.2f}")
    print(f"  {emoji} 信号: {signal_type} (强度: {strength:.1f}%) - {reason}")
    print("-" * 80)


def run_monitor():
    """运行监控主循环"""
    # 加载配置
    config = load_config()
    
    # 打印启动信息
    print_header(config)
    
    # 初始化模块
    data_fetcher = DataFetcher(proxy_url=config['proxy'])
    signal_detector = SignalDetector(
        rsi_overbought=config['rsi']['overbought'],
        rsi_oversold=config['rsi']['oversold'],
        telegram_token=config['telegram'].get('bot_token'),
        telegram_chat_id=config['telegram'].get('chat_id'),
        proxy_url=config['proxy']
    )
    
    # 加载历史信号(恢复持仓状态)
    signal_detector.load_history()
    
    # 测试连接
    print("🔌 正在连接交易所...")
    if not data_fetcher.test_connection():
        print("❌ 无法连接到交易所,请检查网络和代理设置")
        sys.exit(1)
    
    print("✅ 连接成功,开始监控...\n")
    
    # 主循环
    loop_count = 0
    try:
        while True:
            loop_count += 1
            
            try:
                # 获取K线数据
                df = data_fetcher.fetch_kline_data(
                    symbol=config['symbol'],
                    timeframe=config['timeframe'],
                    limit=100  # 获取足够的数据来计算指标
                )
                
                if df is None:
                    print("⚠️ 获取数据失败,等待下次刷新...")
                    time.sleep(config['check_interval'])
                    continue
                
                # 计算指标
                df = calculate_all_indicators(
                    df,
                    boll_period=config['boll']['period'],
                    boll_std=config['boll']['std_dev'],
                    rsi_period=config['rsi']['period']
                )
                
                # 获取最新指标
                indicators = get_latest_indicators(df)
                
                # 检测信号
                signal = signal_detector.detect_signal(indicators)
                
                # 打印状态
                print_status(config['symbol'], indicators, signal)
                
                # 发送告警(仅在有信号时)
                signal_detector.send_alert(
                    symbol=config['symbol'],
                    signal=signal,
                    via_telegram=True,
                    via_console=False  # 已经在上面打印了
                )
                
                # 记录信号到历史(包括中性信号)
                signal_detector.record_signal(
                    symbol=config['symbol'],
                    signal=signal
                )
                
                # 每10次循环保存一次历史
                if loop_count % 10 == 0:
                    signal_detector.save_history()
                
            except Exception as e:
                print(f"❌ 发生错误: {e}")
                print("👉 请检查网络连接和代理设置")
            
            # 等待下次检查
            time.sleep(config['check_interval'])
            
    except KeyboardInterrupt:
        print("\n\n👋 监控已停止")
        # 保存信号历史
        signal_detector.save_history()
        print("💾 信号历史已保存到 signals_history.json")


if __name__ == '__main__':
    run_monitor()