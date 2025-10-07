payoffs = {
    'A': {'H': 1_000_000, 'L': -400_000},
    'B': {'H': 600_000, 'L': 300_000},
    'C': {'H': 100_000, 'L': 400_000}
}

prior_prob = {'H': 0.41, 'L': 0.59}

# 後驗機率（從(g)小題）
posterior_prob = {
    'X1': {'H': 0.6495, 'L': 0.3505},  # 樂觀報告
    'X0': {'H': 0.1657, 'L': 0.8343}   # 悲觀報告
}

# 邊際機率（從(f)小題）
marginal_prob = {'X1': 0.505, 'X0': 0.495}

survey_cost = 50_000

print("\n步驟1: 不雇用市場調查的期望值")

expected_values_no_survey = {}
for strategy in ['A', 'B', 'C']:
    ev = (payoffs[strategy]['H'] * prior_prob['H'] + 
          payoffs[strategy]['L'] * prior_prob['L'])
    expected_values_no_survey[strategy] = ev
    print(f"Strategy {strategy}: ${ev:,.2f}")

best_no_survey = max(expected_values_no_survey, key=expected_values_no_survey.get)
EV_no_survey = expected_values_no_survey[best_no_survey]

print(f"\n最佳策略: Strategy {best_no_survey}")
print(f"期望收益: ${EV_no_survey:,.2f}")

print("步驟2: 雇用市場調查的最優期望值")
print("對每個調查結果，計算所有策略的期望值並選擇最佳\n")

# 樂觀報告 (X=1)
print("情況1: 收到樂觀報告 (X=1)")
print("-"*70)

ev_given_x1 = {}
for strategy in ['A', 'B', 'C']:
    ev = (payoffs[strategy]['H'] * posterior_prob['X1']['H'] + 
          payoffs[strategy]['L'] * posterior_prob['X1']['L'] - 
          survey_cost)
    ev_given_x1[strategy] = ev
    print(f"Strategy {strategy}: ${ev:,.2f}")

best_given_x1 = max(ev_given_x1, key=ev_given_x1.get)
print(f"\n最佳策略: Strategy {best_given_x1}")
print(f"期望收益: ${ev_given_x1[best_given_x1]:,.2f}")

# 悲觀報告 (X=0)
print("\n情況2: 收到悲觀報告 (X=0)")
print("-"*70)

ev_given_x0 = {}
for strategy in ['A', 'B', 'C']:
    ev = (payoffs[strategy]['H'] * posterior_prob['X0']['H'] + 
          payoffs[strategy]['L'] * posterior_prob['X0']['L'] - 
          survey_cost)
    ev_given_x0[strategy] = ev
    print(f"Strategy {strategy}: ${ev:,.2f}")

best_given_x0 = max(ev_given_x0, key=ev_given_x0.get)
print(f"\n最佳策略: Strategy {best_given_x0}")
print(f"期望收益: ${ev_given_x0[best_given_x0]:,.2f}")

# 計算雇用的總期望值
EV_with_survey = (ev_given_x1[best_given_x1] * marginal_prob['X1'] + 
                  ev_given_x0[best_given_x0] * marginal_prob['X0'])

print("\n" + "-"*70)
print("雇用市場調查的期望值:")
print(f"  = (${ev_given_x1[best_given_x1]:,.2f} × {marginal_prob['X1']:.4f}) + "
      f"(${ev_given_x0[best_given_x0]:,.2f} × {marginal_prob['X0']:.4f})")
print(f"  = ${EV_with_survey:,.2f}")

# ============================================================================
# 步驟3: 比較並做決策
# ============================================================================
print("步驟3: 雇用 vs 不雇用比較")

net_benefit = EV_with_survey - EV_no_survey

print(f"""
┌──────────────────────────────────────────────────────────┐
│                    決策比較                              │
├──────────────────────────────────────────────────────────┤
│ 選項1: 不雇用市場調查                                    │
│   最佳策略: Strategy {best_no_survey}                              │
│   期望收益: ${EV_no_survey:>12,.2f}                       │
│   調查成本: ${0:>12,.2f}                              │
│                                                          │
│ 選項2: 雇用市場調查                                      │
│   X=1 時最佳: Strategy {best_given_x1}                           │
│   X=0 時最佳: Strategy {best_given_x0}                           │
│   期望收益: ${EV_with_survey:>12,.2f}                       │
│   調查成本: ${survey_cost:>12,.2f} (已扣除)              │
│                                                          │
│ 淨效益 (選項2 - 選項1):                                  │
│   = ${EV_with_survey:,.2f} - ${EV_no_survey:,.2f}             │
│   = ${net_benefit:>12,.2f}                              │
└──────────────────────────────────────────────────────────┘
""")


print("最終建議")
if net_benefit > 0:
    decision = "建議雇用"
    symbol = ""
    explanation = f"雇用市場調查能增加期望收益 ${net_benefit:,.2f}"
else:
    decision = "不建議雇用"
    symbol = ""
    explanation = f"雇用市場調查會減少期望收益 ${abs(net_benefit):,.2f}"

print(f"\n{symbol} {decision}市場調查公司\n")
print(f"理由：{explanation}")

print("詳細分析")

print(f"""
1. **調查成本**: ${survey_cost:,}
   
2. **最優決策策略**（如果雇用）:
   • 收到樂觀報告 (機率 {marginal_prob['X1']:.1%}):
     → 選擇 Strategy {best_given_x1}
     → 期望收益 ${ev_given_x1[best_given_x1]:,.2f}
   
   • 收到悲觀報告 (機率 {marginal_prob['X0']:.1%}):
     → 選擇 Strategy {best_given_x0}
     → 期望收益 ${ev_given_x0[best_given_x0]:,.2f}

3. **價值分析**:
   • 樣本資訊價值 (EVSI) = ${net_benefit:,.2f}
   • 投資報酬率 = {(net_benefit/survey_cost*100):.2f}%
   • {'這個調查值得投資' if net_benefit > 0 else '調查成本太高，不值得投資'}

4. **風險考量**:
   • 不雇用：固定選 Strategy {best_no_survey}，面對需求不確定性
   • 雇用：根據調查結果調整策略，降低不確定性
""")

print("最優策略 vs 簡單策略 (第j小題)")
# 簡單策略: X=1→A, X=0→C
simple_strategy_x1 = ev_given_x1['A']
simple_strategy_x0 = ev_given_x0['C']
EVE_simple = (simple_strategy_x1 * marginal_prob['X1'] + 
              simple_strategy_x0 * marginal_prob['X0'])

improvement = EV_with_survey - EVE_simple

print(f"""
簡單策略 (X=1→A, X=0→C):
  期望收益: ${EVE_simple:,.2f}

最優策略 (X=1→{best_given_x1}, X=0→{best_given_x0}):
  期望收益: ${EV_with_survey:,.2f}

改進: ${improvement:,.2f}

{'最優策略' if improvement > 100 else '簡單策略'}表現{'顯著' if abs(improvement) > 5000 else '略'}{'更好' if improvement > 0 else '更差'}
""")

print("敏感度分析")
print("\n如果調查成本改變，決策如何變化？\n")

costs_to_test = [0, 25_000, 50_000, 75_000, 100_000]
print(f"{'成本':<15} {'淨效益':<15} {'決策'}")
print("-"*50)

for cost in costs_to_test:
    # 重新計算期望值（扣除新成本）
    ev_x1_new = (payoffs[best_given_x1]['H'] * posterior_prob['X1']['H'] + 
                 payoffs[best_given_x1]['L'] * posterior_prob['X1']['L'] - cost)
    ev_x0_new = (payoffs[best_given_x0]['H'] * posterior_prob['X0']['H'] + 
                 payoffs[best_given_x0]['L'] * posterior_prob['X0']['L'] - cost)
    ev_survey_new = ev_x1_new * marginal_prob['X1'] + ev_x0_new * marginal_prob['X0']
    
    net_new = ev_survey_new - EV_no_survey
    decision_new = "雇用 " if net_new > 0 else "不雇用 "
    
    marker = " ◄ 當前成本" if cost == survey_cost else ""
    print(f"${cost:<14,} ${net_new:<14,.2f} {decision_new}{marker}")

# 計算損益平衡點
breakeven_cost = net_benefit + survey_cost
print(f"\n損益平衡點: ${breakeven_cost:,.2f}")
print(f"如果調查成本 > ${breakeven_cost:,.2f}，則不應雇用")

print("執行建議")
if net_benefit > 0:
    print(f"""
{symbol} 建議雇用市場調查公司

執行步驟：
1. 支付 ${survey_cost:,} 進行市場調查
2. 根據調查結果執行以下決策：
   
   如果收到樂觀報告 (X=1):
     → 實施 Strategy {best_given_x1}
     → 預期收益: ${ev_given_x1[best_given_x1]:,.2f}
   
   如果收到悲觀報告 (X=0):
     → 實施 Strategy {best_given_x0}
     → 預期收益: ${ev_given_x0[best_given_x0]:,.2f}

預期效果：
• 相比不做調查，增加期望收益 ${net_benefit:,.2f}
• 投資報酬率 {(net_benefit/survey_cost*100):.2f}%
• 降低決策風險，提高決策品質
""")
else:
    print(f"""
{symbol} 不建議雇用市場調查公司

理由：
• 調查成本 ${survey_cost:,} 太高
• 調查帶來的資訊價值不足以彌補成本
• 淨損失: ${abs(net_benefit):,.2f}

建議：
• 直接選擇 Strategy {best_no_survey}（不做調查的最佳策略）
• 預期收益: ${EV_no_survey:,.2f}
• 或尋找成本更低的市場調查方案
• 損益平衡點: ${breakeven_cost:,.2f}
""")

print("總結")
print(f"""
【決策】: {decision}

【關鍵數據】:
• 不雇用期望值: ${EV_no_survey:,.2f}
• 雇用期望值: ${EV_with_survey:,.2f}
• 淨效益: ${net_benefit:,.2f}
• 調查成本: ${survey_cost:,.2f}

【最優策略】:
{f'• 樂觀報告  → Strategy {best_given_x1}' if net_benefit > 0 else f'• 直接選擇 Strategy {best_no_survey}'}
{f'• 悲觀報告  → Strategy {best_given_x0}' if net_benefit > 0 else ''}

""")