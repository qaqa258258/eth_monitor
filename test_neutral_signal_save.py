"""
测试信号历史保存功能
验证中性信号也会被正确保存
"""
import json
import sys
from signal_detector import SignalDetector, SignalType

# 设置UTF-8编码
sys.stdout.reconfigure(encoding='utf-8')


def test_neutral_signal_saving():
    """测试中性信号保存"""
    print("=" * 80)
    print("🧪 测试信号历史保存功能（包括中性信号）")
    print("=" * 80)
    print()
    
    # 1. 初始化检测器
    print("1️⃣ 初始化检测器...")
    detector = SignalDetector(
        rsi_overbought=70,
        rsi_oversold=30
    )
    print("✅ 初始化完成\n")
    
    # 2. 测试不同类型的信号
    test_signals = [
        {
            'name': '做多信号',
            'indicators': {
                'close': 3000,
                'rsi': 25,
                'boll_upper': 3200,
                'boll_middle': 3100,
                'boll_lower': 3000
            }
        },
        {
            'name': '中性信号1',
            'indicators': {
                'close': 3100,
                'rsi': 50,
                'boll_upper': 3200,
                'boll_middle': 3100,
                'boll_lower': 3000
            }
        },
        {
            'name': '中性信号2',
            'indicators': {
                'close': 3110,
                'rsi': 55,
                'boll_upper': 3200,
                'boll_middle': 3100,
                'boll_lower': 3000
            }
        }
    ]
    
    print("2️⃣ 检测并记录信号...")
    for test in test_signals:
        print(f"\n  测试: {test['name']}")
        signal = detector.detect_signal(test['indicators'])
        print(f"    信号类型: {signal['signal_type'].value}")
        print(f"    信号强度: {signal['strength']}%")
        
        # 发送告警（不会推送中性信号）
        detector.send_alert('ETH/USDT', signal, via_telegram=False, via_console=False)
        
        # 记录信号（包括中性信号）
        detector.record_signal('ETH/USDT', signal)
        print(f"    ✅ 已记录")
    
    print(f"\n✅ 所有信号已记录，历史记录数量: {len(detector.signals_history)}\n")
    
    # 3. 保存历史文件
    print("3️⃣ 保存历史文件...")
    detector.save_history('test_signals_history_neutral.json')
    print("✅ 已保存到 test_signals_history_neutral.json\n")
    
    # 4. 验证文件内容
    print("4️⃣ 验证文件内容...")
    with open('test_signals_history_neutral.json', 'r', encoding='utf-8') as f:
        saved_history = json.load(f)
    
    print(f"  文件中记录数量: {len(saved_history)}")
    
    for i, record in enumerate(saved_history, 1):
        print(f"  [{i}] {record['signal_type']} - {record['reason']}")
    
    if len(saved_history) == 3:
        print("\n✅ 成功：所有信号（包括中性信号）都已保存！")
        return True
    else:
        print(f"\n❌ 失败：期望3条记录，实际{len(saved_history)}条")
        return False


if __name__ == '__main__':
    print()
    success = test_neutral_signal_saving()
    print()
    print("=" * 80)
    if success:
        print("🎉 测试通过！修复成功")
    else:
        print("❌ 测试失败")
    print("=" * 80)
    
    # 清理测试文件
    import os
    try:
        os.remove('test_signals_history_neutral.json')
        print("\n🧹 已清理测试文件")
    except:
        pass
