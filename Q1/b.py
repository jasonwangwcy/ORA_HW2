import gurobipy as gp
from gurobipy import GRB

TOTAL_LAND = 500
PLANT_COST = [150, 230, 260]
DEMAND = [200, 240]
SELL_PRICE = [170, 150, 36, 10]
BUY_PRICE = [238, 210]
AVG_YIELD = [2.5, 3, 20]

# 重新求解EV問題
ev_model = gp.Model("EV_Solution")
ev_model.setParam('OutputFlag', 0)

x = ev_model.addVars(3, name="acres", lb=0)
w = ev_model.addVars(2, name="buy", lb=0)
y = ev_model.addVars(4, name="sell", lb=0)

profit = (SELL_PRICE[0]*y[0] + SELL_PRICE[1]*y[1] + 
          SELL_PRICE[2]*y[2] + SELL_PRICE[3]*y[3] -
          BUY_PRICE[0]*w[0] - BUY_PRICE[1]*w[1] -
          PLANT_COST[0]*x[0] - PLANT_COST[1]*x[1] - PLANT_COST[2]*x[2])

ev_model.setObjective(profit, GRB.MAXIMIZE)

ev_model.addConstr(x[0] + x[1] + x[2] <= TOTAL_LAND)
ev_model.addConstr(AVG_YIELD[0]*x[0] + w[0] - y[0] >= DEMAND[0])
ev_model.addConstr(AVG_YIELD[1]*x[1] + w[1] - y[1] >= DEMAND[1])
ev_model.addConstr(AVG_YIELD[2]*x[2] == y[2] + y[3])
ev_model.addConstr(y[2] <= 6000)

ev_model.optimize()

# 儲存EV解的種植決策
ev_acres = [x[i].X for i in range(3)]
ev_profit_in_avg = ev_model.objVal

print(f"EV解的種植決策:")
print(f"  小麥: {ev_acres[0]:.2f} 英畝")
print(f"  玉米: {ev_acres[1]:.2f} 英畝")
print(f"  甜菜: {ev_acres[2]:.2f} 英畝")
print(f"  在平均產量下的利潤: ${ev_profit_in_avg:,.2f}")

print("\n步驟2：情境分析")
print("將EV解的種植決策應用到三種產量情境")
print()

# 定義三種情境
scenarios = [
    {'name': '低產量 (-20%)', 'multiplier': 0.8, 'probability': 1/3},
    {'name': '平均產量 (0%)', 'multiplier': 1.0, 'probability': 1/3},
    {'name': '高產量 (+20%)', 'multiplier': 1.2, 'probability': 1/3}
]

scenario_results = []

for idx, scenario in enumerate(scenarios):
    print(f"情境 {idx+1}: {scenario['name']}")
    print(f"  產量倍數: {scenario['multiplier']}")
    
    # 在此情境下的實際產量
    yield_in_scenario = [AVG_YIELD[i] * scenario['multiplier'] for i in range(3)]
    
    # 建立模型：固定種植決策，優化第二階段決策
    sc_model = gp.Model(f"Scenario_{idx}")
    sc_model.setParam('OutputFlag', 0)
    
    # 只有第二階段變數（購買和銷售）
    w_sc = sc_model.addVars(2, name="buy", lb=0)
    y_sc = sc_model.addVars(4, name="sell", lb=0)
    
    # 目標：最大化第二階段利潤（不含種植成本，因為已經種下去了）
    second_stage_profit = (SELL_PRICE[0]*y_sc[0] + SELL_PRICE[1]*y_sc[1] + 
                          SELL_PRICE[2]*y_sc[2] + SELL_PRICE[3]*y_sc[3] -
                          BUY_PRICE[0]*w_sc[0] - BUY_PRICE[1]*w_sc[1])
    
    sc_model.setObjective(second_stage_profit, GRB.MAXIMIZE)
    
    # 限制式（使用EV的種植決策和此情境的產量）
    sc_model.addConstr(
        yield_in_scenario[0]*ev_acres[0] + w_sc[0] - y_sc[0] >= DEMAND[0],
        "wheat"
    )
    sc_model.addConstr(
        yield_in_scenario[1]*ev_acres[1] + w_sc[1] - y_sc[1] >= DEMAND[1],
        "corn"
    )
    sc_model.addConstr(
        yield_in_scenario[2]*ev_acres[2] == y_sc[2] + y_sc[3],
        "beet"
    )
    sc_model.addConstr(y_sc[2] <= 6000, "beet_threshold")
    
    sc_model.optimize()
    
    # 計算總利潤 = 第二階段利潤 - 第一階段種植成本
    planting_cost = sum(PLANT_COST[i] * ev_acres[i] for i in range(3))
    total_profit = sc_model.objVal - planting_cost
    
    # 儲存結果
    result = {
        'scenario': scenario['name'],
        'probability': scenario['probability'],
        'second_stage_profit': sc_model.objVal,
        'planting_cost': planting_cost,
        'total_profit': total_profit,
        'buy_wheat': w_sc[0].X,
        'buy_corn': w_sc[1].X,
        'sell_wheat': y_sc[0].X,
        'sell_corn': y_sc[1].X,
        'sell_beet_low': y_sc[2].X,
        'sell_beet_high': y_sc[3].X,
        'wheat_production': yield_in_scenario[0] * ev_acres[0],
        'corn_production': yield_in_scenario[1] * ev_acres[1],
        'beet_production': yield_in_scenario[2] * ev_acres[2]
    }
    scenario_results.append(result)
    
    # 顯示詳細結果
    print(f"  實際產量:")
    print(f"    小麥: {result['wheat_production']:.2f} 噸（需求 200 噸）")
    print(f"    玉米: {result['corn_production']:.2f} 噸（需求 240 噸）")
    print(f"    甜菜: {result['beet_production']:.2f} 噸")
    
    print(f"  第二階段決策:")
    print(f"    購買小麥: {result['buy_wheat']:.2f} 噸")
    print(f"    購買玉米: {result['buy_corn']:.2f} 噸")
    print(f"    銷售小麥: {result['sell_wheat']:.2f} 噸")
    print(f"    銷售玉米: {result['sell_corn']:.2f} 噸")
    print(f"    銷售甜菜(低價): {result['sell_beet_low']:.2f} 噸")
    print(f"    銷售甜菜(高價): {result['sell_beet_high']:.2f} 噸")
    
    print(f"  財務分析:")
    print(f"    種植成本: ${result['planting_cost']:,.2f}")
    print(f"    第二階段淨收益: ${result['second_stage_profit']:,.2f}")
    print(f"    總利潤: ${result['total_profit']:,.2f}")
    print()

expected_profit = sum(r['total_profit'] * r['probability'] for r in scenario_results)

print(f"\nEV解在各情境下的利潤:")
for r in scenario_results:
    print(f"  {r['scenario']:20s}: ${r['total_profit']:>12,.2f} (機率 {r['probability']:.2%})")

print(f"\n期望總利潤: ${expected_profit:,.2f}")
print(f"  = ({scenario_results[0]['total_profit']:.2f} × 1/3) + "
      f"({scenario_results[1]['total_profit']:.2f} × 1/3) + "
      f"({scenario_results[2]['total_profit']:.2f} × 1/3)")

print("結論")
print(f"""
雖然EV解在「平均產量」情境下表現最佳（${scenario_results[1]['total_profit']:,.2f}），
但考慮所有情境的期望利潤為 ${expected_profit:,.2f}。

這個期望利潤將用於與RP解（隨機規劃解）比較，
以計算VSS（隨機解的價值）。
""")

ev_expected_profit = expected_profit