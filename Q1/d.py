import gurobipy as gp
from gurobipy import GRB

TOTAL_LAND = 500
PLANT_COST = [150, 230, 260]
DEMAND = [200, 240]
SELL_PRICE = [170, 150, 36, 10]
BUY_PRICE = [238, 210]
AVG_YIELD = [2.5, 3, 20]

# 定義三種情境
scenarios = [
    {'name': '低產量 (-20%)', 'multiplier': 0.8, 'probability': 1/3},
    {'name': '平均產量 (0%)', 'multiplier': 1.0, 'probability': 1/3},
    {'name': '高產量 (+20%)', 'multiplier': 1.2, 'probability': 1/3}
]

num_scenarios = len(scenarios)

print("\n建立兩階段隨機規劃模型...")
print(f"  情境數量: {num_scenarios}")
print(f"  第一階段變數: 3個（種植面積）")
print(f"  第二階段變數: {6 * num_scenarios}個（每個情境6個交易變數）")
print()

model = gp.Model("Two_Stage_RP")
model.setParam('OutputFlag', 1)

x1 = model.addVar(name="wheat_acres", lb=0)
x2 = model.addVar(name="corn_acres", lb=0)
x3 = model.addVar(name="beet_acres", lb=0)

w = {}  # 購買變數
y = {}  # 銷售變數

for s in range(num_scenarios):
    # 每個情境的購買變數
    w[s, 0] = model.addVar(name=f"buy_wheat_s{s}", lb=0)
    w[s, 1] = model.addVar(name=f"buy_corn_s{s}", lb=0)
    
    # 每個情境的銷售變數
    y[s, 0] = model.addVar(name=f"sell_wheat_s{s}", lb=0)
    y[s, 1] = model.addVar(name=f"sell_corn_s{s}", lb=0)
    y[s, 2] = model.addVar(name=f"sell_beet_low_s{s}", lb=0)
    y[s, 3] = model.addVar(name=f"sell_beet_high_s{s}", lb=0)

# 第一階段成本（種植成本，確定的）
first_stage_cost = PLANT_COST[0]*x1 + PLANT_COST[1]*x2 + PLANT_COST[2]*x3

# 第二階段期望利潤（各情境的加權平均）
expected_second_stage_profit = 0

for s in range(num_scenarios):
    prob = scenarios[s]['probability']
    
    # 情境s的第二階段利潤
    second_stage_profit_s = (
        SELL_PRICE[0] * y[s,0] +  # 小麥銷售
        SELL_PRICE[1] * y[s,1] +  # 玉米銷售
        SELL_PRICE[2] * y[s,2] +  # 甜菜銷售（低價）
        SELL_PRICE[3] * y[s,3] -  # 甜菜銷售（高價）
        BUY_PRICE[0] * w[s,0] -   # 小麥購買
        BUY_PRICE[1] * w[s,1]     # 玉米購買
    )
    
    expected_second_stage_profit += prob * second_stage_profit_s

# 總期望利潤 = 期望第二階段利潤 - 第一階段成本
total_expected_profit = expected_second_stage_profit - first_stage_cost

model.setObjective(total_expected_profit, GRB.MAXIMIZE)

# 第一階段限制：土地限制（對所有情境共同）
model.addConstr(x1 + x2 + x3 <= TOTAL_LAND, "land_limit")

# 第二階段限制：每個情境分別
for s in range(num_scenarios):
    mult = scenarios[s]['multiplier']
    scenario_name = scenarios[s]['name']
    
    # 此情境下的實際產量
    wheat_yield = AVG_YIELD[0] * mult
    corn_yield = AVG_YIELD[1] * mult
    beet_yield = AVG_YIELD[2] * mult
    
    # 小麥供需平衡
    model.addConstr(
        wheat_yield*x1 + w[s,0] - y[s,0] >= DEMAND[0],
        f"wheat_balance_s{s}"
    )
    
    # 玉米供需平衡
    model.addConstr(
        corn_yield*x2 + w[s,1] - y[s,1] >= DEMAND[1],
        f"corn_balance_s{s}"
    )
    
    # 甜菜產量分配
    model.addConstr(
        beet_yield*x3 == y[s,2] + y[s,3],
        f"beet_production_s{s}"
    )
    
    # 甜菜價格門檻
    model.addConstr(
        y[s,2] <= 6000,
        f"beet_threshold_s{s}"
    )
model.optimize()

if model.status == GRB.OPTIMAL:
    print("\n【最優解】")
    print(f"期望總利潤: ${model.objVal:,.2f}")
    
    print("\n【第一階段決策：種植面積】")
    print(f"  小麥: {x1.X:>10.2f} 英畝")
    print(f"  玉米: {x2.X:>10.2f} 英畝")
    print(f"  甜菜: {x3.X:>10.2f} 英畝")
    print(f"  合計: {x1.X + x2.X + x3.X:>10.2f} 英畝")
    
    rp_acres = [x1.X, x2.X, x3.X]
    
    print("\n【第二階段決策：各情境下的應對策略】")
    print("="*70)
    
    for s in range(num_scenarios):
        mult = scenarios[s]['multiplier']
        prob = scenarios[s]['probability']
        
        print(f"\n情境 {s+1}: {scenarios[s]['name']} (機率 {prob:.2%})")
        print("-"*70)
        
        # 計算此情境下的實際產量
        wheat_prod = AVG_YIELD[0] * mult * x1.X
        corn_prod = AVG_YIELD[1] * mult * x2.X
        beet_prod = AVG_YIELD[2] * mult * x3.X
        
        print(f"實際產量:")
        print(f"  小麥: {wheat_prod:>10.2f} 噸（需求 200 噸）")
        print(f"  玉米: {corn_prod:>10.2f} 噸（需求 240 噸）")
        print(f"  甜菜: {beet_prod:>10.2f} 噸")
        
        print(f"\n應對決策:")
        print(f"  購買小麥: {w[s,0].X:>10.2f} 噸")
        print(f"  購買玉米: {w[s,1].X:>10.2f} 噸")
        print(f"  銷售小麥: {y[s,0].X:>10.2f} 噸")
        print(f"  銷售玉米: {y[s,1].X:>10.2f} 噸")
        print(f"  銷售甜菜($36): {y[s,2].X:>10.2f} 噸")
        print(f"  銷售甜菜($10): {y[s,3].X:>10.2f} 噸")
        
        # 計算此情境下的利潤
        second_stage = (SELL_PRICE[0]*y[s,0].X + SELL_PRICE[1]*y[s,1].X + 
                       SELL_PRICE[2]*y[s,2].X + SELL_PRICE[3]*y[s,3].X -
                       BUY_PRICE[0]*w[s,0].X - BUY_PRICE[1]*w[s,1].X)
        first_stage = sum(PLANT_COST[i]*rp_acres[i] for i in range(3))
        total = second_stage - first_stage
        
        print(f"\n利潤分析:")
        print(f"  種植成本: ${first_stage:>12,.2f}")
        print(f"  第二階段淨收益: ${second_stage:>12,.2f}")
        print(f"  總利潤: ${total:>12,.2f}")
    
    expected_profit_check = 0
    for s in range(num_scenarios):
        prob = scenarios[s]['probability']
        second_stage = (SELL_PRICE[0]*y[s,0].X + SELL_PRICE[1]*y[s,1].X + 
                       SELL_PRICE[2]*y[s,2].X + SELL_PRICE[3]*y[s,3].X -
                       BUY_PRICE[0]*w[s,0].X - BUY_PRICE[1]*w[s,1].X)
        first_stage = sum(PLANT_COST[i]*rp_acres[i] for i in range(3))
        total = second_stage - first_stage
        
        expected_profit_check += prob * total
        print(f"  {scenarios[s]['name']:20s}: ${total:>12,.2f} × {prob:.2%}")
    
    print(f"\n  期望總利潤: ${expected_profit_check:>12,.2f}")
    print(f"  （驗證：應等於目標值 ${model.objVal:,.2f}）")
    print("""
RP解考慮了所有可能情境，並為每個情境規劃最佳應對策略。
第一階段的種植決策是在「期望利潤最大化」的原則下做出的，
這比只考慮平均值的EV解更加穩健和實際。
    """)
    
    # 儲存結果供後續使用
    rp_solution = {
        'acres': rp_acres,
        'expected_profit': model.objVal
    }
    
else:
    print(f"\n求解失敗！狀態碼: {model.status}")