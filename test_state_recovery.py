"""
测试信号历史恢复功能
验证load_history是否正确恢复last_signal状态
"""
import json
import sys
from signal_detector import SignalDetector, SignalType

# 设置UTF-8编码
sys.stdout.reconfigure(encoding='utf-8')


def test_state_recovery():
    """测试状态恢复功能"""
    print("=" * 80)
    print("🧪 信号状态恢复测试")
    print("=" * 80)
    print()
    
    # 1. 创建模拟历史文件（包含一个做多信号）
    print("1️⃣ 创建模拟历史文件...")
    test_history = [
        {
            'timestamp': '2025-11-27 10:00:00',
            'signal_type': '做多',
            'strength': 85.5,
            'reason': 'RSI超卖(25.8) + 触及下轨',
            'symbol': 'ETH/USDT',
            'indicators': {
                'price': 3020.50,
                'rsi': 25.8,
                'boll_upper': 3150.20,
                'boll_middle': 3087.50,
                'boll_lower': 3025.80
            }
        }
    ]
    
    with open('test_signals_history.json', 'w', encoding='utf-8') as f:
        json.dump(test_history, f, indent=2, ensure_ascii=False)
    
    print("✅ 已创建测试历史文件\n")
    
    # 2. 初始化检测器并加载历史
    print("2️⃣ 初始化检测器并加载历史...")
    detector = SignalDetector(
        rsi_overbought=70,
        rsi_oversold=30
    )
    
    print(f"   加载前 last_signal: {detector.last_signal}")
    
    detector.load_history('test_signals_history.json')
    
    print(f"   加载后 last_signal: {detector.last_signal}")
    print()
    
    # 3. 验证状态恢复
    print("3️⃣ 验证状态恢复...")
    if detector.last_signal is None:
        print("❌ 失败：last_signal 未恢复")
        return False
    
    if detector.last_signal['signal_type'] != SignalType.LONG:
        print(f"❌ 失败：信号类型错误，期望 SignalType.LONG，实际 {detector.last_signal['signal_type']}")
        return False
    
    print("✅ 成功：last_signal 已正确恢复为做多信号")
    print(f"   恢复的信号时间: {detector.last_signal['timestamp']}")
    print(f"   恢复的信号强度: {detector.last_signal['strength']}%")
    print()
    
    # 4. 测试平仓信号检测（基于恢复的状态）
    print("4️⃣ 测试基于恢复状态的平仓信号检测...")
    test_indicators = {
        'close': 3087.50,  # 价格回到中轨
        'rsi': 52.3,       # RSI > 50
        'boll_upper': 3150.20,
        'boll_middle': 3087.50,
        'boll_lower': 3025.80
    }
    
    signal = detector.detect_signal(test_indicators)
    
    print(f"   检测到信号类型: {signal['signal_type'].value}")
    print(f"   信号强度: {signal['strength']}%")
    print(f"   触发原因: {signal['reason']}")
    
    if signal['signal_type'] == SignalType.EXIT_LONG:
        print("\n✅ 成功：正确检测到平多信号！")
        print("   这证明状态恢复功能正常工作")
        return True
    else:
        print(f"\n❌ 失败：期望检测到平多信号，但得到 {signal['signal_type'].value}")
        return False


if __name__ == '__main__':
    print()
    success = test_state_recovery()
    print()
    print("=" * 80)
    if success:
        print("🎉 所有测试通过！状态恢复功能正常工作")
    else:
        print("❌ 测试失败")
    print("=" * 80)
    
    # 清理测试文件
    import os
    try:
        os.remove('test_signals_history.json')
        print("\n🧹 已清理测试文件")
    except:
        pass
