payoffs = {
    'A': {'H': 1_000_000, 'L': -400_000},
    'B': {'H': 600_000, 'L': 300_000},
    'C': {'H': 100_000, 'L': 400_000}
}

prior_prob = {'H': 0.41, 'L': 0.59}

strategy_desc = {
    'A': '大量生產 (10,000個)',
    'B': '中量生產 (6,000個)',
    'C': '小量生產 (3,000個)'
}

print("\n步驟1: 計算 EVwoPI (Expected Value without Perfect Information)")
print("這是不知道真實需求時的最佳期望值\n")

# 計算每個策略的期望值
expected_values = {}
for strategy in ['A', 'B', 'C']:
    ev = (payoffs[strategy]['H'] * prior_prob['H'] + 
          payoffs[strategy]['L'] * prior_prob['L'])
    expected_values[strategy] = ev
    print(f"Strategy {strategy}: EV = ${ev:,.2f}")

# 選擇最佳策略
best_strategy = max(expected_values, key=expected_values.get)
EVwoPI = expected_values[best_strategy]

print(f"\n最佳策略: Strategy {best_strategy} ({strategy_desc[best_strategy]})")
print(f"EVwoPI = ${EVwoPI:,.2f}")

print("步驟2: 計算 EVwPI (Expected Value with Perfect Information)")
print("假設能事先100%準確知道真實需求\n")

# 對每個需求狀態，找出最佳策略
best_payoffs = {}

print("情境1: 如果事先知道是高需求 (H)")
print("-"*70)
for strategy in ['A', 'B', 'C']:
    print(f"  Strategy {strategy}: ${payoffs[strategy]['H']:,}")

best_strategy_H = max(['A', 'B', 'C'], key=lambda s: payoffs[s]['H'])
best_payoffs['H'] = payoffs[best_strategy_H]['H']
print(f"  → 最佳選擇: Strategy {best_strategy_H}, 收益 ${best_payoffs['H']:,}")

print("\n情境2: 如果事先知道是低需求 (L)")
print("-"*70)
for strategy in ['A', 'B', 'C']:
    print(f"  Strategy {strategy}: ${payoffs[strategy]['L']:,}")

best_strategy_L = max(['A', 'B', 'C'], key=lambda s: payoffs[s]['L'])
best_payoffs['L'] = payoffs[best_strategy_L]['L']
print(f"  → 最佳選擇: Strategy {best_strategy_L}, 收益 ${best_payoffs['L']:,}")

# 計算期望值
EVwPI = (best_payoffs['H'] * prior_prob['H'] + 
         best_payoffs['L'] * prior_prob['L'])

print("有完美資訊的期望值:")
print(f"  EVwPI = ({best_payoffs['H']:,} × {prior_prob['H']}) + "
      f"({best_payoffs['L']:,} × {prior_prob['L']})")
print(f"  EVwPI = {best_payoffs['H'] * prior_prob['H']:,.2f} + "
      f"{best_payoffs['L'] * prior_prob['L']:,.2f}")
print(f"  EVwPI = ${EVwPI:,.2f}")

print("步驟3: 計算 EVPI")

EVPI = EVwPI - EVwoPI

print(f"\nEVPI = EVwPI - EVwoPI")
print(f"     = ${EVwPI:,.2f} - ${EVwoPI:,.2f}")
print(f"     = ${EVPI:,.2f}")

print("EVPI 的意義與解釋")
print(f"""
EVPI = ${EVPI:,.2f}

這個數字告訴我們：

1. **完美資訊的價值**
   如果有一個100%準確的預測系統（能完美預知需求），
   我們最多願意支付 ${EVPI:,.2f} 來獲得這個資訊。

2. **決策改善的上限**
   無論使用什麼方法（市場調查、數據分析等），
   期望收益的改善最多只能達到 ${EVPI:,.2f}。

3. **不確定性的代價**
   由於不知道真實需求，我們損失了 ${EVPI:,.2f} 的潛在收益。
   這就是「不確定性」的成本。

4. **資訊系統投資上限**
   任何資訊收集系統（如市場調查）的成本如果超過 ${EVPI:,.2f}，
   就不值得投資，因為即使完美預測也只值這個價格。
""")

print("完美資訊 vs 無資訊比較")

print(f"""
┌─────────────────────────────────────────────────────────┐
│                    決策情境比較                         │
├─────────────────────────────────────────────────────────┤
│ 無完美資訊 (現況):                                      │
│   最佳策略: Strategy {best_strategy} ({strategy_desc[best_strategy]})       
│   期望收益: ${EVwoPI:,}                              │
│                                                         │
│ 有完美資訊 (理想):                                      │
│   高需求時: Strategy {best_strategy_H} → ${best_payoffs['H']:,}            │
│   低需求時: Strategy {best_strategy_L} → ${best_payoffs['L']:,}              │
│   期望收益: ${EVwPI:,}                              │
│                                                         │
│ 差距 (EVPI): ${EVPI:,}                                │
│ 相對提升: {(EVPI/EVwoPI*100):.2f}%                                    │
└─────────────────────────────────────────────────────────┘
""")

print("EVPI 分析")
evpi_ratio = EVPI / EVwoPI * 100

print(f"\nEVPI 佔無資訊期望值的比例: {evpi_ratio:.2f}%")

if evpi_ratio < 5:
    assessment = "很小"
    recommendation = "不確定性影響不大，當前決策已經很好，不太需要額外資訊"
elif evpi_ratio < 15:
    assessment = "中等"
    recommendation = "有一定改進空間，可以考慮低成本的資訊收集方法"
else:
    assessment = "較大"
    recommendation = "不確定性影響顯著，強烈建議投資資訊收集系統"

print(f"評估: EVPI相對比例{assessment}")
print(f"建議: {recommendation}")

print("總結")


print(f"""
完美資訊的期望價值 (EVPI) = ${EVPI:,.2f}
""")

