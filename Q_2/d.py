
payoffs = {
    'A': {'H': 1_000_000, 'L': -400_000},  # Strategy A: 10,000個
    'B': {'H': 600_000, 'L': 300_000},     # Strategy B: 6,000個
    'C': {'H': 100_000, 'L': 400_000}      # Strategy C: 3,000個
}

# 先驗機率 (Prior Probability)
prob = {
    'H': 0.41,  # 高需求機率
    'L': 0.59   # 低需求機率
}

# 策略描述
strategy_desc = {
    'A': '大量生產 (10,000個/年)',
    'B': '中量生產 (6,000個/年)',
    'C': '小量生產 (3,000個/年)'
}

print("\n【問題資料】")
print("-"*70)
print("\n收益矩陣 (單位：NTD):")
print(f"{'策略':<12} {'高需求(H)':<20} {'低需求(L)':<20}")
print("-"*70)
for strategy, desc in strategy_desc.items():
    print(f"Strategy {strategy:1}  ${payoffs[strategy]['H']:>12,}        ${payoffs[strategy]['L']:>12,}")

print(f"\n先驗機率:")
print(f"  P(高需求) = {prob['H']:.2f}")
print(f"  P(低需求) = {prob['L']:.2f}")

print("\n" + "="*70)
print("期望值計算")
print("="*70)
print("\n期望值公式: EV = Σ [收益 × 機率]")

expected_values = {}

for strategy in ['A', 'B', 'C']:
    ev = (payoffs[strategy]['H'] * prob['H'] + 
          payoffs[strategy]['L'] * prob['L'])
    expected_values[strategy] = ev
    
    print(f"\nStrategy {strategy} ({strategy_desc[strategy]}):")
    print(f"  EV = ({payoffs[strategy]['H']:,} × {prob['H']}) + "
          f"({payoffs[strategy]['L']:,} × {prob['L']})")
    print(f"  EV = {payoffs[strategy]['H'] * prob['H']:,.2f} + "
          f"{payoffs[strategy]['L'] * prob['L']:,.2f}")
    print(f"  EV = ${ev:,.2f}")

# 找出最佳策略
print("決策分析結果")

best_strategy = max(expected_values, key=expected_values.get)
best_ev = expected_values[best_strategy]

print("\n各策略期望值排序:")
sorted_strategies = sorted(expected_values.items(), key=lambda x: x[1], reverse=True)

for rank, (strategy, ev) in enumerate(sorted_strategies, 1):
    marker = " ⭐ 最佳" if strategy == best_strategy else ""
    print(f"  {rank}. Strategy {strategy}: ${ev:>12,.2f}{marker}")

print("\n" + "="*70)
print(f"✅ 最佳策略: Strategy {best_strategy}")
print("="*70)
print(f"\n策略描述: {strategy_desc[best_strategy]}")
print(f"期望收益: ${best_ev:,.2f}")


print("風險分析")
print(f"\n選擇 Strategy {best_strategy} 的情境分析:")
print(f"  如果高需求發生 (機率 {prob['H']:.0%}):")
print(f"    → 收益 ${payoffs[best_strategy]['H']:,}")
print(f"  如果低需求發生 (機率 {prob['L']:.0%}):")
print(f"    → 收益 ${payoffs[best_strategy]['L']:,}")

# 計算標準差（風險指標）
print("\n各策略的風險評估（標準差）:")
for strategy in ['A', 'B', 'C']:
    ev = expected_values[strategy]
    variance = (prob['H'] * (payoffs[strategy]['H'] - ev)**2 + 
                prob['L'] * (payoffs[strategy]['L'] - ev)**2)
    std_dev = variance ** 0.5
    
    print(f"  Strategy {strategy}: 標準差 = ${std_dev:,.2f}")


print("其他決策準則")
# Maximin準則（悲觀準則）
print("\n1. Maximin準則（最保守，選擇最壞情況最好的）:")
maximin = {}
for strategy in ['A', 'B', 'C']:
    worst = min(payoffs[strategy]['H'], payoffs[strategy]['L'])
    maximin[strategy] = worst
    print(f"   Strategy {strategy}: 最壞情況收益 = ${worst:,}")

best_maximin = max(maximin, key=maximin.get)
print(f"   → Maximin最佳策略: Strategy {best_maximin} (${maximin[best_maximin]:,})")

# Maximax準則（樂觀準則）
print("\n2. Maximax準則（最樂觀，選擇最好情況最好的）:")
maximax = {}
for strategy in ['A', 'B', 'C']:
    best = max(payoffs[strategy]['H'], payoffs[strategy]['L'])
    maximax[strategy] = best
    print(f"   Strategy {strategy}: 最好情況收益 = ${best:,}")

best_maximax = max(maximax, key=maximax.get)
print(f"   → Maximax最佳策略: Strategy {best_maximax} (${maximax[best_maximax]:,})")

print("決策建議總結")
print(f"""
基於期望值準則（Expected Value Criterion）:

建議採用 Strategy {best_strategy} - {strategy_desc[best_strategy]}

理由：
  1. 期望收益最高: ${best_ev:,.2f}
  2. 在給定的機率分佈下，這是最優決策
  3. 考慮了所有可能情境及其發生機率

注意事項：
  • 此決策基於先驗機率 P(H)={prob['H']}, P(L)={prob['L']}
  • 如果機率估計不準確，最佳策略可能改變
  • 如果對風險有特殊偏好，可能選擇其他策略
  • 接下來的小題將探討市場調查是否能改善決策

無市場調查的期望收益: ${best_ev:,.2f}
（此值將用於後續計算EVPI和EVSI）
""")

# 儲存結果供後續使用
results = {
    'best_strategy': best_strategy,
    'expected_value_without_info': best_ev,
    'all_expected_values': expected_values
}
