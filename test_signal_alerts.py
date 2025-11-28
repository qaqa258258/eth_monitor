"""
Telegram交易信号推送测试脚本
模拟各种交易信号并发送到Telegram
"""
import json
import sys
from signal_detector import SignalDetector, SignalType

# 设置UTF-8编码
sys.stdout.reconfigure(encoding='utf-8')


def load_config():
    """加载配置"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 加载配置失败: {e}")
        sys.exit(1)


def test_signal_alerts():
    """测试各种交易信号推送"""
    print("=" * 80)
    print("📱 Telegram交易信号推送测试")
    print("=" * 80)
    print()
    
    # 加载配置
    config = load_config()
    
    # 初始化信号检测器
    detector = SignalDetector(
        rsi_overbought=config['rsi']['overbought'],
        rsi_oversold=config['rsi']['oversold'],
        telegram_token=config['telegram'].get('bot_token'),
        telegram_chat_id=config['telegram'].get('chat_id'),
        proxy_url=config.get('proxy')
    )
    
    print("将发送4种类型的测试信号到你的Telegram...\n")
    
    # 测试1: 做多信号
    print("1️⃣ 发送做多信号...")
    signal_long = {
        'timestamp': '2025-11-27 15:27:00',
        'signal_type': SignalType.LONG,
        'strength': 85.5,
        'reason': 'RSI超卖(25.8) + 触及下轨($3,020.50 <= $3,025.80)',
        'indicators': {
            'price': 3020.50,
            'rsi': 25.8,
            'boll_upper': 3150.20,
            'boll_middle': 3087.50,
            'boll_lower': 3025.80
        }
    }
    detector.send_alert('ETH/USDT', signal_long, via_telegram=True, via_console=False)
    print("✅ 做多信号已发送\n")
    
    input("按Enter键发送做空信号...")
    
    # 测试2: 做空信号
    print("\n2️⃣ 发送做空信号...")
    signal_short = {
        'timestamp': '2025-11-27 15:27:00',
        'signal_type': SignalType.SHORT,
        'strength': 92.3,
        'reason': 'RSI超买(78.5) + 触及上轨($3,150.80 >= $3,150.20)',
        'indicators': {
            'price': 3150.80,
            'rsi': 78.5,
            'boll_upper': 3150.20,
            'boll_middle': 3087.50,
            'boll_lower': 3025.80
        }
    }
    detector.send_alert('ETH/USDT', signal_short, via_telegram=True, via_console=False)
    print("✅ 做空信号已发送\n")
    
    input("按Enter键发送平多信号...")
    
    # 测试3: 平多信号
    print("\n3️⃣ 发送平多信号...")
    signal_exit_long = {
        'timestamp': '2025-11-27 15:27:00',
        'signal_type': SignalType.EXIT_LONG,
        'strength': 50.0,
        'reason': 'RSI回到中性区(52.3)',
        'indicators': {
            'price': 3087.50,
            'rsi': 52.3,
            'boll_upper': 3150.20,
            'boll_middle': 3087.50,
            'boll_lower': 3025.80
        }
    }
    detector.send_alert('ETH/USDT', signal_exit_long, via_telegram=True, via_console=False)
    print("✅ 平多信号已发送\n")
    
    input("按Enter键发送平空信号...")
    
    # 测试4: 平空信号
    print("\n4️⃣ 发送平空信号...")
    signal_exit_short = {
        'timestamp': '2025-11-27 15:27:00',
        'signal_type': SignalType.EXIT_SHORT,
        'strength': 50.0,
        'reason': 'RSI回到中性区(48.7)',
        'indicators': {
            'price': 3087.50,
            'rsi': 48.7,
            'boll_upper': 3150.20,
            'boll_middle': 3087.50,
            'boll_lower': 3025.80
        }
    }
    detector.send_alert('ETH/USDT', signal_exit_short, via_telegram=True, via_console=False)
    print("✅ 平空信号已发送\n")
    
    print("=" * 80)
    print("🎉 所有测试信号已发送完成！")
    print("📱 请查看你的Telegram，应该收到4条消息：")
    print("   1. 🟢 做多信号")
    print("   2. 🔴 做空信号")
    print("   3. ⬆️ 平多信号")
    print("   4. ⬇️ 平空信号")
    print("=" * 80)


if __name__ == '__main__':
    try:
        test_signal_alerts()
    except KeyboardInterrupt:
        print("\n\n👋 测试已取消")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
