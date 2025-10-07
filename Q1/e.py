import gurobipy as gp
from gurobipy import GRB

TOTAL_LAND = 500
PLANT_COST = [150, 230, 260]
DEMAND = [200, 240]
SELL_PRICE = [170, 150, 36, 10]
BUY_PRICE = [238, 210]
AVG_YIELD = [2.5, 3, 20]

scenarios = [
    {'name': '低產量 (-20%)', 'multiplier': 0.8, 'probability': 1/3},
    {'name': '平均產量 (0%)', 'multiplier': 1.0, 'probability': 1/3},
    {'name': '高產量 (+20%)', 'multiplier': 1.2, 'probability': 1/3}
]

rp_model = gp.Model("RP")
rp_model.setParam('OutputFlag', 0)

x_rp = rp_model.addVars(3, name="acres", lb=0)
w_rp = {}
y_rp = {}

for s in range(3):
    w_rp[s] = rp_model.addVars(2, name=f"buy_s{s}", lb=0)
    y_rp[s] = rp_model.addVars(4, name=f"sell_s{s}", lb=0)

first_stage = sum(PLANT_COST[i]*x_rp[i] for i in range(3))
expected_second = 0

for s in range(3):
    prob = scenarios[s]['probability']
    second = (SELL_PRICE[0]*y_rp[s][0] + SELL_PRICE[1]*y_rp[s][1] + 
             SELL_PRICE[2]*y_rp[s][2] + SELL_PRICE[3]*y_rp[s][3] -
             BUY_PRICE[0]*w_rp[s][0] - BUY_PRICE[1]*w_rp[s][1])
    expected_second += prob * second

rp_model.setObjective(expected_second - first_stage, GRB.MAXIMIZE)

rp_model.addConstr(x_rp[0] + x_rp[1] + x_rp[2] <= TOTAL_LAND)

for s in range(3):
    mult = scenarios[s]['multiplier']
    yield_s = [AVG_YIELD[i] * mult for i in range(3)]
    
    rp_model.addConstr(yield_s[0]*x_rp[0] + w_rp[s][0] - y_rp[s][0] >= DEMAND[0])
    rp_model.addConstr(yield_s[1]*x_rp[1] + w_rp[s][1] - y_rp[s][1] >= DEMAND[1])
    rp_model.addConstr(yield_s[2]*x_rp[2] == y_rp[s][2] + y_rp[s][3])
    rp_model.addConstr(y_rp[s][2] <= 6000)

rp_model.optimize()
RP = rp_model.objVal

print(f"RP (隨機規劃解的期望利潤): ${RP:,.2f}")

ws_results = []  # Wait-and-See 結果

for s, scenario in enumerate(scenarios):
    mult = scenario['multiplier']
    prob = scenario['probability']
    
    print(f"情境 {s+1}: {scenario['name']} (機率 {prob:.2%})")
    
    # 建立WS模型：假設已知此情境會發生
    ws_model = gp.Model(f"WS_Scenario_{s}")
    ws_model.setParam('OutputFlag', 0)
    
    # 決策變數
    x_ws = ws_model.addVars(3, name="acres", lb=0)
    w_ws = ws_model.addVars(2, name="buy", lb=0)
    y_ws = ws_model.addVars(4, name="sell", lb=0)
    
    # 此情境下的產量
    yield_ws = [AVG_YIELD[i] * mult for i in range(3)]
    
    # 目標函數：最大化利潤
    profit_ws = (SELL_PRICE[0]*y_ws[0] + SELL_PRICE[1]*y_ws[1] + 
                SELL_PRICE[2]*y_ws[2] + SELL_PRICE[3]*y_ws[3] -
                BUY_PRICE[0]*w_ws[0] - BUY_PRICE[1]*w_ws[1] -
                PLANT_COST[0]*x_ws[0] - PLANT_COST[1]*x_ws[1] - PLANT_COST[2]*x_ws[2])
    
    ws_model.setObjective(profit_ws, GRB.MAXIMIZE)
    
    # 限制式
    ws_model.addConstr(x_ws[0] + x_ws[1] + x_ws[2] <= TOTAL_LAND)
    ws_model.addConstr(yield_ws[0]*x_ws[0] + w_ws[0] - y_ws[0] >= DEMAND[0])
    ws_model.addConstr(yield_ws[1]*x_ws[1] + w_ws[1] - y_ws[1] >= DEMAND[1])
    ws_model.addConstr(yield_ws[2]*x_ws[2] == y_ws[2] + y_ws[3])
    ws_model.addConstr(y_ws[2] <= 6000)
    
    ws_model.optimize()
    
    ws_profit = ws_model.objVal
    ws_results.append({
        'scenario': scenario['name'],
        'probability': prob,
        'profit': ws_profit,
        'acres': [x_ws[i].X for i in range(3)]
    })
    
    print(f"  最佳種植: 小麥={x_ws[0].X:.2f}, 玉米={x_ws[1].X:.2f}, 甜菜={x_ws[2].X:.2f}")
    print(f"  利潤: ${ws_profit:,.2f}")
    print()

# 計算 EEV
EEV = sum(r['profit'] * r['probability'] for r in ws_results)

print("="*70)
print(f"EEV (完美資訊下的期望利潤):")
for r in ws_results:
    print(f"  {r['scenario']:20s}: ${r['profit']:>12,.2f} × {r['probability']:.2%}")
print(f"\n  EEV = ${EEV:,.2f}")

# 先求EV解
ev_model = gp.Model("EV")
ev_model.setParam('OutputFlag', 0)

x_ev = ev_model.addVars(3, name="acres", lb=0)
w_ev = ev_model.addVars(2, name="buy", lb=0)
y_ev = ev_model.addVars(4, name="sell", lb=0)

profit_ev = (SELL_PRICE[0]*y_ev[0] + SELL_PRICE[1]*y_ev[1] + 
            SELL_PRICE[2]*y_ev[2] + SELL_PRICE[3]*y_ev[3] -
            BUY_PRICE[0]*w_ev[0] - BUY_PRICE[1]*w_ev[1] -
            PLANT_COST[0]*x_ev[0] - PLANT_COST[1]*x_ev[1] - PLANT_COST[2]*x_ev[2])

ev_model.setObjective(profit_ev, GRB.MAXIMIZE)

ev_model.addConstr(x_ev[0] + x_ev[1] + x_ev[2] <= TOTAL_LAND)
ev_model.addConstr(AVG_YIELD[0]*x_ev[0] + w_ev[0] - y_ev[0] >= DEMAND[0])
ev_model.addConstr(AVG_YIELD[1]*x_ev[1] + w_ev[1] - y_ev[1] >= DEMAND[1])
ev_model.addConstr(AVG_YIELD[2]*x_ev[2] == y_ev[2] + y_ev[3])
ev_model.addConstr(y_ev[2] <= 6000)

ev_model.optimize()

ev_acres = [x_ev[i].X for i in range(3)]

print(f"EV解的種植決策:")
print(f"  小麥={ev_acres[0]:.2f}, 玉米={ev_acres[1]:.2f}, 甜菜={ev_acres[2]:.2f}")

# 計算EV解在各情境下的表現
print(f"\nEV解在各情境下的利潤:")
ev_scenario_profits = []

for s, scenario in enumerate(scenarios):
    mult = scenario['multiplier']
    prob = scenario['probability']
    
    # 評估EV解在此情境下
    eval_model = gp.Model(f"Eval_s{s}")
    eval_model.setParam('OutputFlag', 0)
    
    w_eval = eval_model.addVars(2, name="buy", lb=0)
    y_eval = eval_model.addVars(4, name="sell", lb=0)
    
    yield_eval = [AVG_YIELD[i] * mult for i in range(3)]
    
    second_profit = (SELL_PRICE[0]*y_eval[0] + SELL_PRICE[1]*y_eval[1] + 
                    SELL_PRICE[2]*y_eval[2] + SELL_PRICE[3]*y_eval[3] -
                    BUY_PRICE[0]*w_eval[0] - BUY_PRICE[1]*w_eval[1])
    
    eval_model.setObjective(second_profit, GRB.MAXIMIZE)
    
    eval_model.addConstr(yield_eval[0]*ev_acres[0] + w_eval[0] - y_eval[0] >= DEMAND[0])
    eval_model.addConstr(yield_eval[1]*ev_acres[1] + w_eval[1] - y_eval[1] >= DEMAND[1])
    eval_model.addConstr(yield_eval[2]*ev_acres[2] == y_eval[2] + y_eval[3])
    eval_model.addConstr(y_eval[2] <= 6000)
    
    eval_model.optimize()
    
    first_cost = sum(PLANT_COST[i]*ev_acres[i] for i in range(3))
    total_profit = eval_model.objVal - first_cost
    ev_scenario_profits.append(total_profit)
    
    print(f"  {scenario['name']:20s}: ${total_profit:>12,.2f}")

EEV_EV = sum(ev_scenario_profits[s] * scenarios[s]['probability'] for s in range(3))

print(f"\n  EEV(EV解) = ${EEV_EV:,.2f}")
print(f"  （EV解在各情境下的期望利潤）")

EVPI = EEV - RP
VSS = RP - EEV_EV

print(f"\n【關鍵數值】")
print(f"  EEV  (完美資訊期望利潤):        ${EEV:>12,.2f}")
print(f"  RP   (隨機規劃期望利潤):        ${RP:>12,.2f}")
print(f"  EEV(EV解) (EV解期望利潤):       ${EEV_EV:>12,.2f}")

print(f"\n【EVPI - Expected Value of Perfect Information】")
print(f"  EVPI = EEV - RP = ${EEV:,.2f} - ${RP:,.2f} = ${EVPI:,.2f}")
print(f"\n  意義：")
print(f"  - 完美資訊的價值是 ${EVPI:,.2f}")
print(f"  - 如果能100%準確預測天氣，最多願意付 ${EVPI:,.2f} 購買此資訊")
print(f"  - 佔RP利潤的 {(EVPI/RP*100):.2f}%")

if EVPI < RP * 0.05:
    print(f"  - EVPI相對較小（<5%），說明RP已經很接近完美資訊的表現")
elif EVPI < RP * 0.15:
    print(f"  - EVPI中等（5-15%），完美資訊有一定價值但不是關鍵")
else:
    print(f"  - EVPI較大（>15%），完美資訊有顯著價值")

print(f"\n【VSS - Value of Stochastic Solution】")
print(f"  VSS = RP - EEV(EV解) = ${RP:,.2f} - ${EEV_EV:,.2f} = ${VSS:,.2f}")
print(f"\n  意義：")
print(f"  - 使用隨機規劃比只用平均值方法多賺 ${VSS:,.2f}")
print(f"  - 利潤提升 {(VSS/EEV_EV*100):.2f}%")

if VSS < EEV_EV * 0.02:
    print(f"  - VSS很小（<2%），簡單的EV方法就足夠了")
elif VSS < EEV_EV * 0.10:
    print(f"  - VSS中等（2-10%），隨機規劃有一定價值")
else:
    print(f"  - VSS很大（>10%），隨機規劃非常值得使用")

print("\n" + "="*70)
print("利潤層級圖")
print("="*70)
print(f"""
    EEV (完美資訊)      ${EEV:>12,.2f}  ◄─┐
         ↑                                    │
         │ EVPI = ${EVPI:>12,.2f}         │ 完美資訊的價值
         │                                    │
    RP (隨機規劃)       ${RP:>12,.2f}  ◄─┘
         ↑
         │ VSS = ${VSS:>12,.2f}
         │                                    ┌─ 隨機規劃的價值
    EEV(EV解)           ${EEV_EV:>12,.2f}  ◄─┘
""")

print(f"""
1. 如果能獲得完美天氣預報，期望利潤能從 ${RP:,.2f} 提升到 ${EEV:,.2f}
   → 完美資訊值 ${EVPI:,.2f}

2. 使用隨機規劃而不是簡單平均值法，期望利潤從 ${EEV_EV:,.2f} 提升到 ${RP:,.2f}
   → 隨機解的價值 ${VSS:,.2f}

3. RP解已經捕獲了 {((RP-EEV_EV)/(EEV-EEV_EV)*100):.1f}% 的潛在改進空間
   （VSS / (EVPI + VSS) = {(VSS/(EVPI+VSS)*100):.1f}%）
""")