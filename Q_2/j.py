"""
第二題 (j): 計算 EVE (Expected Value with Experimentation)
使用簡單策略：X=1則選A，X=0則選C
"""

print("="*70)
print("第二題 (j): EVE - 直接使用調查結果的期望值")
print("="*70)

# ============================================================================
# 資料定義
# ============================================================================
payoffs = {
    'A': {'H': 1_000_000, 'L': -400_000},
    'B': {'H': 600_000, 'L': 300_000},
    'C': {'H': 100_000, 'L': 400_000}
}

prior_prob = {'H': 0.41, 'L': 0.59}

# 聯合機率（從(e)小題）
joint_prob = {
    (0, 0): 0.413,   # P(X=0, θ=0) - 悲觀且低需求
    (0, 1): 0.082,   # P(X=0, θ=1) - 悲觀且高需求
    (1, 0): 0.177,   # P(X=1, θ=0) - 樂觀且低需求
    (1, 1): 0.328    # P(X=1, θ=1) - 樂觀且高需求
}

# 邊際機率（從(f)小題）
marginal_prob = {
    0: 0.495,  # P(X=0)
    1: 0.505   # P(X=1)
}

survey_cost = 50_000

# ============================================================================
# 問題說明
# ============================================================================
print("\n【問題說明】")
print("-"*70)
print("""
題目要求計算「直接使用調查結果」的期望值：
  • 如果調查樂觀 (X=1) → 選擇 Strategy A (大量生產)
  • 如果調查悲觀 (X=0) → 選擇 Strategy C (小量生產)

這是一個簡單但不一定最優的決策規則。
""")

# ============================================================================
# 計算 EVE
# ============================================================================
print("\n" + "="*70)
print("計算 EVE")
print("="*70)

print("\n情境1: 調查顯示樂觀 (X=1)，選擇 Strategy A")
print("-"*70)

# 樂觀報告下的期望收益
# 有兩種可能：實際高需求或低需求
prob_H_given_X1 = joint_prob[(1, 1)] / marginal_prob[1]  # P(θ=1|X=1)
prob_L_given_X1 = joint_prob[(1, 0)] / marginal_prob[1]  # P(θ=0|X=1)

print(f"後驗機率:")
print(f"  P(H|X=1) = {prob_H_given_X1:.4f}")
print(f"  P(L|X=1) = {prob_L_given_X1:.4f}")

payoff_A_given_X1 = (payoffs['A']['H'] * prob_H_given_X1 + 
                     payoffs['A']['L'] * prob_L_given_X1 - 
                     survey_cost)

print(f"\nStrategy A 在 X=1 時的期望收益:")
print(f"  = ({payoffs['A']['H']:,} × {prob_H_given_X1:.4f}) + "
      f"({payoffs['A']['L']:,} × {prob_L_given_X1:.4f}) - {survey_cost:,}")
print(f"  = {payoffs['A']['H'] * prob_H_given_X1:,.2f} + "
      f"{payoffs['A']['L'] * prob_L_given_X1:,.2f} - {survey_cost:,}")
print(f"  = ${payoff_A_given_X1:,.2f}")

print("\n情境2: 調查顯示悲觀 (X=0)，選擇 Strategy C")
print("-"*70)

# 悲觀報告下的期望收益
prob_H_given_X0 = joint_prob[(0, 1)] / marginal_prob[0]  # P(θ=1|X=0)
prob_L_given_X0 = joint_prob[(0, 0)] / marginal_prob[0]  # P(θ=0|X=0)

print(f"後驗機率:")
print(f"  P(H|X=0) = {prob_H_given_X0:.4f}")
print(f"  P(L|X=0) = {prob_L_given_X0:.4f}")

payoff_C_given_X0 = (payoffs['C']['H'] * prob_H_given_X0 + 
                     payoffs['C']['L'] * prob_L_given_X0 - 
                     survey_cost)

print(f"\nStrategy C 在 X=0 時的期望收益:")
print(f"  = ({payoffs['C']['H']:,} × {prob_H_given_X0:.4f}) + "
      f"({payoffs['C']['L']:,} × {prob_L_given_X0:.4f}) - {survey_cost:,}")
print(f"  = {payoffs['C']['H'] * prob_H_given_X0:,.2f} + "
      f"{payoffs['C']['L'] * prob_L_given_X0:,.2f} - {survey_cost:,}")
print(f"  = ${payoff_C_given_X0:,.2f}")

# 計算 EVE
print("\n" + "-"*70)
print("計算 EVE (期望值)")
print("-"*70)

EVE = (payoff_A_given_X1 * marginal_prob[1] + 
       payoff_C_given_X0 * marginal_prob[0])

print(f"\nEVE = (收益|X=1) × P(X=1) + (收益|X=0) × P(X=0)")
print(f"    = (${payoff_A_given_X1:,.2f}) × {marginal_prob[1]:.4f} + "
      f"(${payoff_C_given_X0:,.2f}) × {marginal_prob[0]:.4f}")
print(f"    = ${payoff_A_given_X1 * marginal_prob[1]:,.2f} + "
      f"${payoff_C_given_X0 * marginal_prob[0]:,.2f}")
print(f"    = ${EVE:,.2f}")

# ============================================================================
# EVE 的意義
# ============================================================================
print("\n" + "="*70)
print("EVE 的意義")
print("="*70)

print(f"""
EVE = ${EVE:,.2f}

這是使用「簡單決策規則」的期望值：
  • 樂觀 → Strategy A
  • 悲觀 → Strategy C

注意：
  1. 這個規則簡單但不一定最優
  2. 最優策略應該對每個調查結果計算所有策略的期望值
  3. EVE 已經扣除調查成本 ${survey_cost:,}
""")

# ============================================================================
# 與其他值比較
# ============================================================================
print("\n" + "="*70)
print("與其他決策方法比較")
print("="*70)

# 計算 EVwoPI (從之前)
expected_values = {}
for strategy in ['A', 'B', 'C']:
    ev = (payoffs[strategy]['H'] * prior_prob['H'] + 
          payoffs[strategy]['L'] * prior_prob['L'])
    expected_values[strategy] = ev

best_strategy = max(expected_values, key=expected_values.get)
EVwoPI = expected_values[best_strategy]

# 計算 EVwPI (從之前)
best_payoffs = {
    'H': max(payoffs[s]['H'] for s in ['A', 'B', 'C']),
    'L': max(payoffs[s]['L'] for s in ['A', 'B', 'C'])
}
EVwPI = (best_payoffs['H'] * prior_prob['H'] + 
         best_payoffs['L'] * prior_prob['L'])

EVPI = EVwPI - EVwoPI

print(f"""
┌──────────────────────────────────────────────────────────┐
│                  決策方法比較                            │
├──────────────────────────────────────────────────────────┤
│ 1. 無資訊 (EVwoPI):                                      │
│    最佳策略: Strategy {best_strategy}                              │
│    期望收益: ${EVwoPI:>12,.2f}                         │
│                                                          │
│ 2. 簡單使用調查 (EVE):                                   │
│    決策規則: X=1→A, X=0→C                                │
│    期望收益: ${EVE:>12,.2f}                         │
│    調查價值: ${EVE - EVwoPI:>12,.2f} (扣除成本後)        │
│                                                          │
│ 3. 完美資訊 (EVwPI):                                     │
│    期望收益: ${EVwPI:>12,.2f}                         │
│    資訊價值: ${EVPI:>12,.2f} (EVPI)                    │
└──────────────────────────────────────────────────────────┘
""")

# ============================================================================
# 計算 EVSI (樣本資訊的期望價值)
# ============================================================================
print("\n" + "="*70)
print("EVSI - 樣本資訊的期望價值")
print("="*70)

EVSI = EVE - EVwoPI

print(f"\nEVSI = EVE - EVwoPI")
print(f"     = ${EVE:,.2f} - ${EVwoPI:,.2f}")
print(f"     = ${EVSI:,.2f}")

print(f"""
EVSI 的意義：
  • 使用這個簡單調查策略，比不做調查多賺 ${EVSI:,.2f}
  • 但這只是「簡單策略」的價值，不是最優策略的價值
  • 調查成本 ${survey_cost:,} 已經包含在計算中
""")

# 計算效率
efficiency = (EVSI / EVPI * 100) if EVPI > 0 else 0

print(f"\n調查效率 = EVSI / EVPI = {EVSI:,.2f} / {EVPI:,.2f} = {efficiency:.2f}%")
print(f"\n這表示簡單調查策略捕獲了完美資訊價值的 {efficiency:.2f}%")

# ============================================================================
# 是否值得雇用（預覽）
# ============================================================================
print("\n" + "="*70)
print("是否值得雇用市場調查？（預覽）")
print("="*70)

net_benefit = EVSI

print(f"\n使用簡單策略 (X=1→A, X=0→C):")
print(f"  調查帶來的額外期望收益: ${EVSI:,.2f}")

if net_benefit > 0:
    print(f"  ✅ 值得雇用！淨收益 = ${net_benefit:,.2f}")
else:
    print(f"  ❌ 不值得雇用！淨損失 = ${-net_benefit:,.2f}")

print(f"""
注意：
  • 這只是使用「簡單策略」的結果
  • 最優策略可能表現更好
  • 下一小題 (k) 會做完整分析
""")

# ============================================================================
# 情境模擬
# ============================================================================
print("\n" + "="*70)
print("情境模擬")
print("="*70)

print(f"\n假設進行1000次決策：")

# 計算各種情況的次數
num_x1 = marginal_prob[1] * 1000
num_x0 = marginal_prob[0] * 1000

num_x1_h = joint_prob[(1, 1)] * 1000
num_x1_l = joint_prob[(1, 0)] * 1000
num_x0_h = joint_prob[(0, 1)] * 1000
num_x0_l = joint_prob[(0, 0)] * 1000

print(f"\n調查樂觀 (X=1): 約 {num_x1:.0f} 次")
print(f"  → 選擇 Strategy A")
print(f"  → 實際高需求: {num_x1_h:.0f} 次，收益 ${payoffs['A']['H'] - survey_cost:,} 每次")
print(f"  → 實際低需求: {num_x1_l:.0f} 次，收益 ${payoffs['A']['L'] - survey_cost:,} 每次")

print(f"\n調查悲觀 (X=0): 約 {num_x0:.0f} 次")
print(f"  → 選擇 Strategy C")
print(f"  → 實際高需求: {num_x0_h:.0f} 次，收益 ${payoffs['C']['H'] - survey_cost:,} 每次")
print(f"  → 實際低需求: {num_x0_l:.0f} 次，收益 ${payoffs['C']['L'] - survey_cost:,} 每次")

total_profit = (num_x1_h * (payoffs['A']['H'] - survey_cost) +
                num_x1_l * (payoffs['A']['L'] - survey_cost) +
                num_x0_h * (payoffs['C']['H'] - survey_cost) +
                num_x0_l * (payoffs['C']['L'] - survey_cost))

avg_profit = total_profit / 1000

print(f"\n總利潤: ${total_profit:,.2f}")
print(f"平均利潤: ${avg_profit:,.2f} (應等於 EVE = ${EVE:,.2f})")

# ============================================================================
# 總結
# ============================================================================
print("\n" + "="*70)
print("總結")
print("="*70)

print(f"""
✅ EVE 計算完成

使用簡單策略 (X=1→A, X=0→C):
  期望值 (EVE) = ${EVE:,.2f}
  樣本資訊價值 (EVSI) = ${EVSI:,.2f}
  調查效率 = {efficiency:.2f}%

關鍵發現：
  1. 簡單調查策略{'確實' if EVSI > 0 else '不'}能增加期望收益
  2. 但這可能不是最優策略
""")
