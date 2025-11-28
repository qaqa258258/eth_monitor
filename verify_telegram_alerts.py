"""
验证Telegram告警功能
测试各种信号是否能成功发送到Telegram
"""
import json
import sys
from signal_detector import SignalDetector, SignalType

sys.stdout.reconfigure(encoding='utf-8')


def load_config():
    """加载配置"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ 找不到config.json，请先配置!")
        sys.exit(1)


def verify_telegram_config(config):
    """验证Telegram配置"""
    print("=" * 80)
    print("🔍 检查Telegram配置")
    print("=" * 80)
    
    telegram_config = config.get('telegram', {})
    bot_token = telegram_config.get('bot_token', '')
    chat_id = telegram_config.get('chat_id', '')
    
    print(f"Bot Token: {bot_token[:20]}..." if len(bot_token) > 20 else f"Bot Token: {bot_token}")
    print(f"Chat ID: {chat_id}")
    
    if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
        print("\n❌ Bot Token 未配置!")
        return False
    
    if not chat_id or chat_id == "YOUR_CHAT_ID_HERE":
        print("\n❌ Chat ID 未配置!")
        return False
    
    print("\n✅ Telegram配置完整")
    return True


def test_signal_alert(detector, signal_type_name, signal_data):
    """测试单个信号的告警"""
    print(f"\n{'=' * 80}")
    print(f"📤 测试发送 {signal_type_name} 信号")
    print(f"{'=' * 80}")
    
    print(f"信号类型: {signal_data['signal_type'].value}")
    print(f"信号强度: {signal_data['strength']}")
    print(f"原因: {signal_data['reason']}")
    
    # 发送告警
    detector.send_alert(
        symbol='ETH/USDT',
        signal=signal_data,
        via_telegram=True,
        via_console=False  # 不在控制台重复打印
    )
    
    print("\n请检查您的Telegram是否收到消息!")
    input("按回车继续测试下一个信号...\n")


def main():
    """主函数"""
    print("=" * 80)
    print("🔔 Telegram 告警功能验证工具")
    print("=" * 80)
    print()
    
    # 加载配置
    config = load_config()
    
    # 验证配置
    if not verify_telegram_config(config):
        print("\n⚠️ 请先在 config.json 中配置正确的 Telegram bot_token 和 chat_id")
        print("\n如何获取:")
        print("1. Bot Token: 与 @BotFather 对话创建Bot获取")
        print("2. Chat ID: 与 @userinfobot 对话获取")
        return
    
    # 初始化检测器
    detector = SignalDetector(
        rsi_overbought=70,
        rsi_oversold=30,
        telegram_token=config['telegram']['bot_token'],
        telegram_chat_id=config['telegram']['chat_id'],
        proxy_url=config.get('proxy')
    )
    
    print("\n" + "=" * 80)
    print("🚀 开始测试各种信号")
    print("=" * 80)
    
    # 测试信号列表
    test_signals = [
        {
            'name': '🟢 做多信号',
            'data': {
                'timestamp': '2025-11-28 10:30:00',
                'signal_type': SignalType.LONG,
                'strength': 75.5,
                'reason': '触及下轨($2850.00 <= $2900.00) + RSI参考: 25.0',
                'indicators': {
                    'price': 2850,
                    'rsi': 25,
                    'boll_upper': 3200,
                    'boll_middle': 3050,
                    'boll_lower': 2900
                }
            }
        },
        {
            'name': '🔴 做空信号',
            'data': {
                'timestamp': '2025-11-28 10:31:00',
                'signal_type': SignalType.SHORT,
                'strength': 82.3,
                'reason': '触及上轨($3250.00 >= $3200.00) + RSI参考: 78.0',
                'indicators': {
                    'price': 3250,
                    'rsi': 78,
                    'boll_upper': 3200,
                    'boll_middle': 3050,
                    'boll_lower': 2900
                }
            }
        },
        {
            'name': '⬆️ 平多信号',
            'data': {
                'timestamp': '2025-11-28 10:32:00',
                'signal_type': SignalType.EXIT_LONG,
                'strength': 50,
                'reason': '价格回到中轨($3050.00 >= $3050.00) + RSI参考: 50.0',
                'indicators': {
                    'price': 3050,
                    'rsi': 50,
                    'boll_upper': 3200,
                    'boll_middle': 3050,
                    'boll_lower': 2900
                }
            }
        },
        {
            'name': '⬇️ 平空信号',
            'data': {
                'timestamp': '2025-11-28 10:33:00',
                'signal_type': SignalType.EXIT_SHORT,
                'strength': 50,
                'reason': '价格回到中轨($3050.00 <= $3050.00) + RSI参考: 50.0',
                'indicators': {
                    'price': 3050,
                    'rsi': 50,
                    'boll_upper': 3200,
                    'boll_middle': 3050,
                    'boll_lower': 2900
                }
            }
        }
    ]
    
    # 测试每个信号
    for signal in test_signals:
        test_signal_alert(detector, signal['name'], signal['data'])
    
    # 测试中性信号（不应该发送）
    print(f"\n{'=' * 80}")
    print("⚪ 测试中性信号 (不应该发送Telegram)")
    print("=" * 80)
    
    neutral_signal = {
        'timestamp': '2025-11-28 10:34:00',
        'signal_type': SignalType.NEUTRAL,
        'strength': 0,
        'reason': '无明显信号',
        'indicators': {
            'price': 3100,
            'rsi': 50,
            'boll_upper': 3200,
            'boll_middle': 3050,
            'boll_lower': 2900
        }
    }
    
    detector.send_alert(
        symbol='ETH/USDT',
        signal=neutral_signal,
        via_telegram=True,
        via_console=True
    )
    
    print("\n✅ 中性信号应该只在控制台显示，不发送Telegram")
    
    print("\n" + "=" * 80)
    print("🎉 测试完成！")
    print("=" * 80)
    print("\n请检查您的Telegram，应该收到4条消息:")
    print("  1. 🟢 做多信号")
    print("  2. 🔴 做空信号")
    print("  3. ⬆️ 平多信号")
    print("  4. ⬇️ 平空信号")
    print("\n中性信号不会发送到Telegram ✓")


if __name__ == '__main__':
    main()
