prior = {
    'H': 0.41,  # P(θ=1) = P(高需求)
    'L': 0.59   # P(θ=0) = P(低需求)
}

print("\n先驗機率:")
print(f"  P(θ=1) = P(高需求) = {prior['H']}")
print(f"  P(θ=0) = P(低需求) = {prior['L']}")

# 條件機率 (Conditional Probability)
# P(X|θ) = 在真實需求為θ的條件下，調查結果為X的機率
conditional = {
    ('Encouraging', 'H'): 0.8,   # P(X=1|θ=1)
    ('Discouraging', 'L'): 0.7   # P(X=0|θ=0)
}

# 計算其他條件機率
conditional[('Discouraging', 'H')] = 1 - conditional[('Encouraging', 'H')]  # P(X=0|θ=1)
conditional[('Encouraging', 'L')] = 1 - conditional[('Discouraging', 'L')]  # P(X=1|θ=0)

print("\n條件機率（調查可靠性）:")
print(f"  P(X=1|θ=1) = P(樂觀|高需求) = {conditional[('Encouraging', 'H')]}")
print(f"  P(X=0|θ=1) = P(悲觀|高需求) = {conditional[('Discouraging', 'H')]}")
print(f"  P(X=1|θ=0) = P(樂觀|低需求) = {conditional[('Encouraging', 'L')]}")
print(f"  P(X=0|θ=0) = P(悲觀|低需求) = {conditional[('Discouraging', 'L')]}")

print("聯合機率公式")

print("""
聯合機率 P(X, θ) 表示「調查結果X」和「真實需求θ」同時發生的機率

公式: P(X, θ) = P(X|θ) × P(θ)

其中:
  P(X|θ) = 條件機率（在θ條件下X的機率）
  P(θ)   = 先驗機率（θ發生的機率）
""")
print("計算聯合機率")
# 定義符號映射
theta_map = {'H': 1, 'L': 0}
x_map = {'Encouraging': 1, 'Discouraging': 0}

joint = {}

# 1. P(X=0, θ=0) - 悲觀且低需求
x_label = 'Discouraging'
theta_label = 'L'
joint[(0, 0)] = conditional[(x_label, theta_label)] * prior[theta_label]

print(f"\n1. P(X=0, θ=0) = P(悲觀, 低需求)")
print(f"   = P(X=0|θ=0) × P(θ=0)")
print(f"   = {conditional[(x_label, theta_label)]} × {prior[theta_label]}")
print(f"   = {joint[(0, 0)]:.4f}")

# 2. P(X=0, θ=1) - 悲觀且高需求
x_label = 'Discouraging'
theta_label = 'H'
joint[(0, 1)] = conditional[(x_label, theta_label)] * prior[theta_label]

print(f"\n2. P(X=0, θ=1) = P(悲觀, 高需求)")
print(f"   = P(X=0|θ=1) × P(θ=1)")
print(f"   = {conditional[(x_label, theta_label)]} × {prior[theta_label]}")
print(f"   = {joint[(0, 1)]:.4f}")

# 3. P(X=1, θ=0) - 樂觀且低需求
x_label = 'Encouraging'
theta_label = 'L'
joint[(1, 0)] = conditional[(x_label, theta_label)] * prior[theta_label]

print(f"\n3. P(X=1, θ=0) = P(樂觀, 低需求)")
print(f"   = P(X=1|θ=0) × P(θ=0)")
print(f"   = {conditional[(x_label, theta_label)]} × {prior[theta_label]}")
print(f"   = {joint[(1, 0)]:.4f}")

# 4. P(X=1, θ=1) - 樂觀且高需求
x_label = 'Encouraging'
theta_label = 'H'
joint[(1, 1)] = conditional[(x_label, theta_label)] * prior[theta_label]

print(f"\n4. P(X=1, θ=1) = P(樂觀, 高需求)")
print(f"   = P(X=1|θ=1) × P(θ=1)")
print(f"   = {conditional[(x_label, theta_label)]} × {prior[theta_label]}")
print(f"   = {joint[(1, 1)]:.4f}")

print("聯合機率表")
print(f"""
┌─────────────────┬──────────────┬──────────────┬──────────┐
│  真實需求 \\ 調查 │  X=0 (悲觀)  │  X=1 (樂觀)  │  合計    │
├─────────────────┼──────────────┼──────────────┼──────────┤
│ θ=0 (低需求)    │   {joint[(0,0)]:.4f}     │   {joint[(1,0)]:.4f}     │  {prior['L']:.2f}    │
│ θ=1 (高需求)    │   {joint[(0,1)]:.4f}     │   {joint[(1,1)]:.4f}     │  {prior['H']:.2f}    │
├─────────────────┼──────────────┼──────────────┼──────────┤
│ 合計            │   {joint[(0,0)] + joint[(0,1)]:.4f}     │   {joint[(1,0)] + joint[(1,1)]:.4f}     │  1.00    │
└─────────────────┴──────────────┴──────────────┴──────────┘
""")

total_joint = sum(joint.values())
print(f"\n所有聯合機率的總和:")
print(f"  Σ P(X, θ) = {joint[(0,0)]:.4f} + {joint[(0,1)]:.4f} + "
      f"{joint[(1,0)]:.4f} + {joint[(1,1)]:.4f}")
print(f"  = {total_joint:.4f}")

if abs(total_joint - 1.0) < 0.0001:
    print(f"  ✓ 驗證通過！總和 = 1")
else:
    print(f"  ✗ 驗證失敗！總和應該 = 1")

# 驗證行總和
row_sum_L = joint[(0, 0)] + joint[(1, 0)]
row_sum_H = joint[(0, 1)] + joint[(1, 1)]

print(f"\n行總和驗證（應等於先驗機率）:")
print(f"  低需求行: {joint[(0,0)]:.4f} + {joint[(1,0)]:.4f} = {row_sum_L:.4f}")
print(f"  應等於 P(θ=0) = {prior['L']:.2f}")
print(f"  ✓ 正確" if abs(row_sum_L - prior['L']) < 0.0001 else "  ✗ 錯誤")

print(f"\n  高需求行: {joint[(0,1)]:.4f} + {joint[(1,1)]:.4f} = {row_sum_H:.4f}")
print(f"  應等於 P(θ=1) = {prior['H']:.2f}")
print(f"  ✓ 正確" if abs(row_sum_H - prior['H']) < 0.0001 else "  ✗ 錯誤")

print("總結")
print(f"""
四個聯合機率計算完成：

P(X=0, θ=0) = {joint[(0, 0)]:.4f}  (悲觀報告且實際低需求)
P(X=0, θ=1) = {joint[(0, 1)]:.4f}  (悲觀報告但實際高需求)
P(X=1, θ=0) = {joint[(1, 0)]:.4f}  (樂觀報告但實際低需求)
P(X=1, θ=1) = {joint[(1, 1)]:.4f}  (樂觀報告且實際高需求)
""")

# 儲存結果供後續使用
results = {
    'joint_prob': joint,
    'prior_prob': prior,
    'conditional_prob': conditional
}
