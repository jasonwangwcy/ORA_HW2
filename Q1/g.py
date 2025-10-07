import gurobipy as gp
from gurobipy import GRB
import numpy as np
from scipy import stats

TOTAL_LAND = 500
PLANT_COST = [150, 230, 260]
DEMAND = [200, 240]
SELL_PRICE = [170, 150, 36, 10]
BUY_PRICE = [238, 210]
AVG_YIELD = [2.5, 3, 20]

# Monte Carlo 參數
N = 30  # 每批樣本數
M = 15  # 訓練批次數
N_bar = 30  # 驗證每批樣本數
T = 15  # 驗證批次數

# 常態分佈參數
MU = 1.0    # 平均值
SIGMA = 0.1  # 標準差

# np.random.seed(34) 

saa_solutions = []  # 儲存所有SAA解
saa_objectives = []  # 儲存所有目標值

for m in range(M):
    
    # 步驟1：從 N(1, 0.1) 產生 N 個產量率樣本
    yield_multipliers = np.random.normal(MU, SIGMA, N)
    
    print(f"產生 {N} 個產量率樣本:")
    print(f"  平均值: {np.mean(yield_multipliers):.4f}")
    print(f"  標準差: {np.std(yield_multipliers):.4f}")
    print(f"  範圍: [{np.min(yield_multipliers):.4f}, {np.max(yield_multipliers):.4f}]")
    
    # 步驟2：建立 SAA 模型
    saa_model = gp.Model(f"SAA_batch_{m+1}")
    saa_model.setParam('OutputFlag', 0)  # 不顯示求解過程
    
    # 第一階段變數：種植面積（對所有樣本相同）
    x_saa = saa_model.addVars(3, name="acres", lb=0)
    
    # 第二階段變數：每個樣本情境的購買和銷售決策
    w_saa = {}
    y_saa = {}
    
    for n in range(N):
        w_saa[n] = saa_model.addVars(2, name=f"buy_n{n}", lb=0)
        y_saa[n] = saa_model.addVars(4, name=f"sell_n{n}", lb=0)
    
    # 目標函數：最大化期望利潤
    first_stage_cost = sum(PLANT_COST[i] * x_saa[i] for i in range(3))
    
    expected_second_stage = 0
    for n in range(N):
        prob_n = 1/N  # 每個樣本的機率
        
        second_stage_profit_n = (
            SELL_PRICE[0] * y_saa[n][0] +
            SELL_PRICE[1] * y_saa[n][1] +
            SELL_PRICE[2] * y_saa[n][2] +
            SELL_PRICE[3] * y_saa[n][3] -
            BUY_PRICE[0] * w_saa[n][0] -
            BUY_PRICE[1] * w_saa[n][1]
        )
        
        expected_second_stage += prob_n * second_stage_profit_n
    
    saa_model.setObjective(expected_second_stage - first_stage_cost, GRB.MAXIMIZE)
    
    # 限制式
    # 第一階段：土地限制
    saa_model.addConstr(x_saa[0] + x_saa[1] + x_saa[2] <= TOTAL_LAND, "land")
    
    # 第二階段：每個樣本情境的限制
    for n in range(N):
        mult_n = yield_multipliers[n]
        yield_n = [AVG_YIELD[i] * mult_n for i in range(3)]
        
        # 小麥平衡
        saa_model.addConstr(
            yield_n[0]*x_saa[0] + w_saa[n][0] - y_saa[n][0] >= DEMAND[0],
            f"wheat_n{n}"
        )
        
        # 玉米平衡
        saa_model.addConstr(
            yield_n[1]*x_saa[1] + w_saa[n][1] - y_saa[n][1] >= DEMAND[1],
            f"corn_n{n}"
        )
        
        # 甜菜產量
        saa_model.addConstr(
            yield_n[2]*x_saa[2] == y_saa[n][2] + y_saa[n][3],
            f"beet_n{n}"
        )
        
        # 甜菜價格門檻
        saa_model.addConstr(y_saa[n][2] <= 6000, f"beet_threshold_n{n}")
    
    # 步驟3：求解
    saa_model.optimize()
    
    if saa_model.status == GRB.OPTIMAL:
        solution = {
            'batch': m+1,
            'acres': [x_saa[i].X for i in range(3)],
            'objective': saa_model.objVal,
            'samples_mean': np.mean(yield_multipliers),
            'samples_std': np.std(yield_multipliers)
        }
        
        saa_solutions.append(solution)
        saa_objectives.append(saa_model.objVal)
        
        print(f"\n求解成功！")
        print(f"  種植決策: 小麥={solution['acres'][0]:.2f}, "
              f"玉米={solution['acres'][1]:.2f}, 甜菜={solution['acres'][2]:.2f}")
        print(f"  目標值: ${solution['objective']:,.2f}")
    else:
        print(f"求解失敗！狀態: {saa_model.status}")

saa_mean = np.mean(saa_objectives)
saa_std = np.std(saa_objectives, ddof=1)  # 使用樣本標準差
saa_se = saa_std / np.sqrt(M)  # 標準誤

print(f"\n目標值統計（M={M}個批次）:")
print(f"  樣本平均: ${saa_mean:,.2f}")
print(f"  標準差: ${saa_std:,.2f}")
print(f"  標準誤: ${saa_se:,.2f}")
print(f"  最小值: ${np.min(saa_objectives):,.2f}")
print(f"  最大值: ${np.max(saa_objectives):,.2f}")

# 計算95%信賴區間
confidence_level = 0.95
alpha = 1 - confidence_level
df = M - 1  # 自由度
t_value = stats.t.ppf(1 - alpha/2, df)

ci_lower_train = saa_mean - t_value * saa_se
ci_upper_train = saa_mean + t_value * saa_se

print(f"\n95% 信賴區間:")
print(f"  下界: ${ci_lower_train:,.2f}")
print(f"  上界: ${ci_upper_train:,.2f}")
print(f"  區間寬度: ${ci_upper_train - ci_lower_train:,.2f}")

# 種植決策的統計
acres_array = np.array([sol['acres'] for sol in saa_solutions])
mean_acres = np.mean(acres_array, axis=0)
std_acres = np.std(acres_array, axis=0, ddof=1)

print(f"\n種植決策統計（M={M}個批次）:")
print(f"  小麥: {mean_acres[0]:.2f} ± {std_acres[0]:.2f} 英畝")
print(f"  玉米: {mean_acres[1]:.2f} ± {std_acres[1]:.2f} 英畝")
print(f"  甜菜: {mean_acres[2]:.2f} ± {std_acres[2]:.2f} 英畝")

# 選擇最佳解（目標值最高的批次）
best_batch_idx = np.argmax(saa_objectives)
best_solution = saa_solutions[best_batch_idx]

print(f"\n最佳解（批次 {best_solution['batch']}）:")
print(f"  小麥: {best_solution['acres'][0]:.2f} 英畝")
print(f"  玉米: {best_solution['acres'][1]:.2f} 英畝")
print(f"  甜菜: {best_solution['acres'][2]:.2f} 英畝")
print(f"  目標值: ${best_solution['objective']:,.2f}")

print("\n" + "="*70)
print("階段 2: 驗證階段 - 評估最佳解的性能")
print("="*70)
print(f"使用批次 {best_solution['batch']} 的解進行驗證")
print(f"驗證參數: T={T} 批次，每批 N̄={N_bar} 個樣本")

best_acres = best_solution['acres']
validation_objectives = []

for t in range(T):
    print(f"\n驗證批次 {t+1}/{T}...", end=" ")
    
    # 產生新的驗證樣本
    yield_mults_val = np.random.normal(MU, SIGMA, N_bar)
    
    # 計算在這些樣本下的期望利潤
    batch_profits = []
    
    for n in range(N_bar):
        mult = yield_mults_val[n]
        
        # 建立評估模型（固定第一階段決策）
        eval_model = gp.Model(f"Eval_t{t}_n{n}")
        eval_model.setParam('OutputFlag', 0)
        
        # 只有第二階段變數
        w_eval = eval_model.addVars(2, name="buy", lb=0)
        y_eval = eval_model.addVars(4, name="sell", lb=0)
        
        # 此樣本的產量
        yield_eval = [AVG_YIELD[i] * mult for i in range(3)]
        
        # 目標：最大化第二階段利潤
        second_profit = (
            SELL_PRICE[0] * y_eval[0] +
            SELL_PRICE[1] * y_eval[1] +
            SELL_PRICE[2] * y_eval[2] +
            SELL_PRICE[3] * y_eval[3] -
            BUY_PRICE[0] * w_eval[0] -
            BUY_PRICE[1] * w_eval[1]
        )
        
        eval_model.setObjective(second_profit, GRB.MAXIMIZE)
        
        # 限制式（使用固定的種植決策）
        eval_model.addConstr(
            yield_eval[0]*best_acres[0] + w_eval[0] - y_eval[0] >= DEMAND[0]
        )
        eval_model.addConstr(
            yield_eval[1]*best_acres[1] + w_eval[1] - y_eval[1] >= DEMAND[1]
        )
        eval_model.addConstr(
            yield_eval[2]*best_acres[2] == y_eval[2] + y_eval[3]
        )
        eval_model.addConstr(y_eval[2] <= 6000)
        
        eval_model.optimize()
        
        if eval_model.status == GRB.OPTIMAL:
            # 總利潤 = 第二階段利潤 - 第一階段成本
            first_cost = sum(PLANT_COST[i] * best_acres[i] for i in range(3))
            total_profit = eval_model.objVal - first_cost
            batch_profits.append(total_profit)
    
    # 此批次的平均利潤
    batch_avg = np.mean(batch_profits)
    validation_objectives.append(batch_avg)
    
    print(f"平均利潤: ${batch_avg:,.2f}")

val_mean = np.mean(validation_objectives)
val_std = np.std(validation_objectives, ddof=1)
val_se = val_std / np.sqrt(T)

print(f"\n期望利潤估計（T={T}個驗證批次）:")
print(f"  樣本平均: ${val_mean:,.2f}")
print(f"  標準差: ${val_std:,.2f}")
print(f"  標準誤: ${val_se:,.2f}")
print(f"  最小值: ${np.min(validation_objectives):,.2f}")
print(f"  最大值: ${np.max(validation_objectives):,.2f}")

# 計算95%信賴區間
df_val = T - 1
t_value_val = stats.t.ppf(1 - alpha/2, df_val)

ci_lower_val = val_mean - t_value_val * val_se
ci_upper_val = val_mean + t_value_val * val_se

print(f"\n95% 信賴區間:")
print(f"  下界 (Lower Bound): ${ci_lower_val:,.2f}")
print(f"  上界 (Upper Bound): ${ci_upper_val:,.2f}")
print(f"  區間寬度: ${ci_upper_val - ci_lower_val:,.2f}")

print(f"\n【最佳種植策略】")
print(f"  小麥: {best_acres[0]:.2f} 英畝")
print(f"  玉米: {best_acres[1]:.2f} 英畝")
print(f"  甜菜: {best_acres[2]:.2f} 英畝")

print(f"\n【期望利潤估計】")
print(f"  點估計: ${val_mean:,.2f}")
print(f"  95% 信賴區間: [${ci_lower_val:,.2f}, ${ci_upper_val:,.2f}]")

print(f"\n【統計顯著性】")
relative_error = (ci_upper_val - ci_lower_val) / (2 * val_mean) * 100
print(f"  相對誤差: ±{relative_error:.2f}%")

if relative_error < 2:
    precision = "非常高"
elif relative_error < 5:
    precision = "高"
elif relative_error < 10:
    precision = "中等"
else:
    precision = "較低"

print(f"  估計精度: {precision}")


print(f"\n需要先執行(d)小題獲得RP解，然後進行比較:")
print(f"  連續情境期望利潤: ${val_mean:,.2f}")
print(f"  連續情境95% CI: [${ci_lower_val:,.2f}, ${ci_upper_val:,.2f}]")
print(f"  離散情境期望利潤: $_______ （來自(d)小題的RP解）")

print(f"\n觀察：")
print(f"  1. 連續情境提供了更細緻的不確定性建模")
print(f"  2. 信賴區間提供了風險評估")
print(f"  3. 可以評估最壞情況（下界）和最好情況（上界）")


print("敏感度分析")
print(f"\n產量率分佈 N(1, 0.1) 的含義:")
print(f"  68% 的情況: 產量在 [0.9, 1.1] 之間（±1σ）")
print(f"  95% 的情況: 產量在 [0.8, 1.2] 之間（±2σ）")
print(f"  99.7% 的情況: 產量在 [0.7, 1.3] 之間（±3σ）")

print(f"\n最壞情況分析（下界 ${ci_lower_val:,.2f}）:")
print(f"  即使在不利情況下，仍能保證至少此利潤")
print(f"  與期望值相比下降: ${val_mean - ci_lower_val:,.2f} "
      f"({(val_mean - ci_lower_val)/val_mean*100:.1f}%)")

print(f"\n最好情況分析（上界 ${ci_upper_val:,.2f}）:")
print(f"  在有利情況下，最多能達到此利潤")
print(f"  與期望值相比上升: ${ci_upper_val - val_mean:,.2f} "
      f"({(ci_upper_val - val_mean)/val_mean*100:.1f}%)")

print("結論與建議")
print(f"""
1. **模型精度**
   - 使用連續常態分佈更貼近實際天氣變化
   - 95%信賴區間提供了可靠的風險評估

2. **決策建議**
   - 採用最佳解的種植策略
   - 準備應對下界情況（保守估計）
   - 期待期望值水平的利潤

3. **風險管理**
   - 下界提供了最壞情況的保障
   - 可根據風險偏好調整策略
   - 建議準備 ${val_mean - ci_lower_val:,.2f} 的緩衝資金

4. **進一步改進**
   - 可以增加樣本數（N, M, T）提高精度
   - 可以考慮其他分佈（如對數常態分佈）
   - 可以加入價格不確定性
""")
