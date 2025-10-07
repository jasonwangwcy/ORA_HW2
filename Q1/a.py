import gurobipy as gp
from gurobipy import GRB

TOTAL_LAND = 500  # 總土地（英畝）
PLANT_COST = [150, 230, 260]  # 種植成本：小麥、玉米、甜菜（$/英畝）
DEMAND = [200, 240]  # 需求：小麥、玉米（噸）
SELL_PRICE = [170, 150, 36, 10]  # 銷售價格：小麥、玉米、甜菜(<6000)、甜菜(>6000)（$/噸）
BUY_PRICE = [238, 210]  # 購買價格：小麥、玉米（$/噸）
AVG_YIELD = [2.5, 3, 20]  # 平均產量：小麥、玉米、甜菜（噸/英畝）

model = gp.Model("EV_Solution")
model.setParam('OutputFlag', 1)  

# 決策變數
# 第一階段：種植面積
x1 = model.addVar(name="wheat_acres", lb=0)  # 小麥種植面積
x2 = model.addVar(name="corn_acres", lb=0)   # 玉米種植面積
x3 = model.addVar(name="beet_acres", lb=0)   # 甜菜種植面積

# 第二階段：購買和銷售
w1 = model.addVar(name="buy_wheat", lb=0)    # 購買小麥
w2 = model.addVar(name="buy_corn", lb=0)     # 購買玉米
y1 = model.addVar(name="sell_wheat", lb=0)   # 銷售小麥
y2 = model.addVar(name="sell_corn", lb=0)    # 銷售玉米
y3 = model.addVar(name="sell_beet_low", lb=0)   # 銷售甜菜（≤6000噸）
y4 = model.addVar(name="sell_beet_high", lb=0)  # 銷售甜菜（>6000噸）

profit = (
    SELL_PRICE[0] * y1 +  # 小麥銷售收入
    SELL_PRICE[1] * y2 +  # 玉米銷售收入
    SELL_PRICE[2] * y3 +  # 甜菜銷售收入（低價）
    SELL_PRICE[3] * y4 -  # 甜菜銷售收入（高價）
    BUY_PRICE[0] * w1 -   # 小麥購買成本
    BUY_PRICE[1] * w2 -   # 玉米購買成本
    PLANT_COST[0] * x1 -  # 小麥種植成本
    PLANT_COST[1] * x2 -  # 玉米種植成本
    PLANT_COST[2] * x3    # 甜菜種植成本
)

model.setObjective(profit, GRB.MAXIMIZE)

# 1. 土地限制
model.addConstr(x1 + x2 + x3 <= TOTAL_LAND, "land_limit")

# 2. 小麥供需平衡：產量 + 購買 - 銷售 ≥ 需求
model.addConstr(AVG_YIELD[0]*x1 + w1 - y1 >= DEMAND[0], "wheat_demand")

# 3. 玉米供需平衡：產量 + 購買 - 銷售 ≥ 需求
model.addConstr(AVG_YIELD[1]*x2 + w2 - y2 >= DEMAND[1], "corn_demand")

# 4. 甜菜產量分配：總產量 = 低價銷售 + 高價銷售
model.addConstr(AVG_YIELD[2]*x3 == y3 + y4, "beet_production")

# 5. 甜菜價格門檻：低價部分不超過6000噸
model.addConstr(y3 <= 6000, "beet_price_threshold")
model.optimize()


if model.status == GRB.OPTIMAL:
    print("\n【最優解】")
    print(f"最大利潤: ${model.objVal:,.2f}")
    
    print("\n【第一階段決策：種植面積】")
    print(f"  小麥: {x1.X:>10.2f} 英畝")
    print(f"  玉米: {x2.X:>10.2f} 英畝")
    print(f"  甜菜: {x3.X:>10.2f} 英畝")
    print(f"  合計: {x1.X + x2.X + x3.X:>10.2f} 英畝（共500英畝）")
    
    print("\n【第二階段決策：交易量】")
    print(f"  購買小麥: {w1.X:>10.2f} 噸")
    print(f"  購買玉米: {w2.X:>10.2f} 噸")
    print(f"  銷售小麥: {y1.X:>10.2f} 噸")
    print(f"  銷售玉米: {y2.X:>10.2f} 噸")
    print(f"  銷售甜菜（$36/噸）: {y3.X:>10.2f} 噸")
    print(f"  銷售甜菜（$10/噸）: {y4.X:>10.2f} 噸")
    
    print("\n【產量計算】")
    wheat_prod = AVG_YIELD[0] * x1.X
    corn_prod = AVG_YIELD[1] * x2.X
    beet_prod = AVG_YIELD[2] * x3.X
    print(f"  小麥產量: {wheat_prod:>10.2f} 噸（需求200噸）")
    print(f"  玉米產量: {corn_prod:>10.2f} 噸（需求240噸）")
    print(f"  甜菜產量: {beet_prod:>10.2f} 噸")
    
    print("\n【成本與收入分析】")
    planting_cost = PLANT_COST[0]*x1.X + PLANT_COST[1]*x2.X + PLANT_COST[2]*x3.X
    buying_cost = BUY_PRICE[0]*w1.X + BUY_PRICE[1]*w2.X
    selling_revenue = (SELL_PRICE[0]*y1.X + SELL_PRICE[1]*y2.X + 
                      SELL_PRICE[2]*y3.X + SELL_PRICE[3]*y4.X)
    
    print(f"  種植成本: ${planting_cost:>12,.2f}")
    print(f"  購買成本: ${buying_cost:>12,.2f}")
    print(f"  銷售收入: ${selling_revenue:>12,.2f}")
    print(f"  淨利潤:   ${model.objVal:>12,.2f}")
    
    # 儲存結果供後續使用
    ev_solution = {
        'acres': [x1.X, x2.X, x3.X],
        'profit': model.objVal
    }
    
else:
    print("\n求解失敗！")
    print(f"狀態碼: {model.status}")