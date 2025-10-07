prior = {'H': 0.41, 'L': 0.59}

joint = {
    (0, 0): 0.413,   # P(X=0, θ=0)
    (0, 1): 0.082,   # P(X=0, θ=1)
    (1, 0): 0.177,   # P(X=1, θ=0)
    (1, 1): 0.328    # P(X=1, θ=1)
}

# 邊際機率（從 (f)）
marginal = {
    0: 0.495,  # P(X=0)
    1: 0.505   # P(X=1)
}

print("\n先驗機率:")
print(f"  P(θ=0) = {prior['L']}")
print(f"  P(θ=1) = {prior['H']}")

print("\n邊際機率:")
print(f"  P(X=0) = {marginal[0]:.4f}")
print(f"  P(X=1) = {marginal[1]:.4f}")


print("計算後驗機率")
posterior = {}

# 1. P(θ=0|X=0) - 調查悲觀，實際是低需求的機率
print("\n1. P(θ=0|X=0) = P(低需求|悲觀報告)")
print(f"   = P(X=0, θ=0) / P(X=0)")
print(f"   = {joint[(0, 0)]:.4f} / {marginal[0]:.4f}")
posterior[(0, 0)] = joint[(0, 0)] / marginal[0]
print(f"   = {posterior[(0, 0)]:.4f}")

print(f"\n   解釋：如果調查顯示悲觀，實際為低需求的機率是 {posterior[(0, 0)]:.2%}")

# 2. P(θ=1|X=0) - 調查悲觀，實際是高需求的機率
print("\n2. P(θ=1|X=0) = P(高需求|悲觀報告)")
print(f"   = P(X=0, θ=1) / P(X=0)")
print(f"   = {joint[(0, 1)]:.4f} / {marginal[0]:.4f}")
posterior[(1, 0)] = joint[(0, 1)] / marginal[0]
print(f"   = {posterior[(1, 0)]:.4f}")

print(f"\n   解釋：如果調查顯示悲觀，實際為高需求的機率是 {posterior[(1, 0)]:.2%}")

# 3. P(θ=0|X=1) - 調查樂觀，實際是低需求的機率
print("\n3. P(θ=0|X=1) = P(低需求|樂觀報告)")
print(f"   = P(X=1, θ=0) / P(X=1)")
print(f"   = {joint[(1, 0)]:.4f} / {marginal[1]:.4f}")
posterior[(0, 1)] = joint[(1, 0)] / marginal[1]
print(f"   = {posterior[(0, 1)]:.4f}")

print(f"\n   解釋：如果調查顯示樂觀，實際為低需求的機率是 {posterior[(0, 1)]:.2%}")

# 4. P(θ=1|X=1) - 調查樂觀，實際是高需求的機率
print("\n4. P(θ=1|X=1) = P(高需求|樂觀報告)")
print(f"   = P(X=1, θ=1) / P(X=1)")
print(f"   = {joint[(1, 1)]:.4f} / {marginal[1]:.4f}")
posterior[(1, 1)] = joint[(1, 1)] / marginal[1]
print(f"   = {posterior[(1, 1)]:.4f}")

print(f"\n   解釋：如果調查顯示樂觀，實際為高需求的機率是 {posterior[(1, 1)]:.2%}")

print("驗證")

sum_given_x0 = posterior[(0, 0)] + posterior[(1, 0)]
sum_given_x1 = posterior[(0, 1)] + posterior[(1, 1)]

print(f"\n給定 X=0 (悲觀報告) 的後驗機率總和:")
print(f"  P(θ=0|X=0) + P(θ=1|X=0) = {posterior[(0, 0)]:.4f} + {posterior[(1, 0)]:.4f}")
print(f"  = {sum_given_x0:.4f}")
print(f"  ✓ 正確" if abs(sum_given_x0 - 1.0) < 0.0001 else "  ✗ 錯誤")

print(f"\n給定 X=1 (樂觀報告) 的後驗機率總和:")
print(f"  P(θ=0|X=1) + P(θ=1|X=1) = {posterior[(0, 1)]:.4f} + {posterior[(1, 1)]:.4f}")
print(f"  = {sum_given_x1:.4f}")
print(f"  ✓ 正確" if abs(sum_given_x1 - 1.0) < 0.0001 else "  ✗ 錯誤")


print("後驗機率表")

print(f"""
┌────────────────────────┬─────────────────┬─────────────────┐
│   調查結果 \\ 真實需求   │  θ=0 (低需求)   │  θ=1 (高需求)   │
├────────────────────────┼─────────────────┼─────────────────┤
│ X=0 (悲觀報告)         │    {posterior[(0,0)]:.4f}       │    {posterior[(1,0)]:.4f}       │
│ X=1 (樂觀報告)         │    {posterior[(0,1)]:.4f}       │    {posterior[(1,1)]:.4f}       │
└────────────────────────┴─────────────────┴─────────────────┘
""")

print("先驗機率 vs 後驗機率比較")
print("\n【情況1：收到悲觀報告 (X=0)】")
print(f"  先驗: P(θ=0) = {prior['L']:.4f}, P(θ=1) = {prior['H']:.4f}")
print(f"  後驗: P(θ=0|X=0) = {posterior[(0,0)]:.4f}, P(θ=1|X=0) = {posterior[(1,0)]:.4f}")
print(f"\n  變化:")
print(f"    低需求機率: {prior['L']:.4f} → {posterior[(0,0)]:.4f} "
      f"(增加 {(posterior[(0,0)] - prior['L'])*100:+.1f} 百分點)")
print(f"    高需求機率: {prior['H']:.4f} → {posterior[(1,0)]:.4f} "
      f"(減少 {(posterior[(1,0)] - prior['H'])*100:+.1f} 百分點)")
print(f"  → 悲觀報告使我們更相信需求會低")

print("\n【情況2：收到樂觀報告 (X=1)】")
print(f"  先驗: P(θ=0) = {prior['L']:.4f}, P(θ=1) = {prior['H']:.4f}")
print(f"  後驗: P(θ=0|X=1) = {posterior[(0,1)]:.4f}, P(θ=1|X=1) = {posterior[(1,1)]:.4f}")
print(f"\n  變化:")
print(f"    低需求機率: {prior['L']:.4f} → {posterior[(0,1)]:.4f} "
      f"(減少 {(posterior[(0,1)] - prior['L'])*100:+.1f} 百分點)")
print(f"    高需求機率: {prior['H']:.4f} → {posterior[(1,1)]:.4f} "
      f"(增加 {(posterior[(1,1)] - prior['H'])*100:+.1f} 百分點)")
print(f"  → 樂觀報告使我們更相信需求會高")

print(f"""
先驗機率（調查前）:
  低需求: ████████████████████ {prior['L']:.0%}
  高需求: █████████████ {prior['H']:.0%}

收到悲觀報告後:
  低需求: ███████████████████████████ {posterior[(0,0)]:.0%} ↑
  高需求: ████████ {posterior[(1,0)]:.0%} ↓

收到樂觀報告後:
  低需求: ██████████████ {posterior[(0,1)]:.0%} ↓
  高需求: ████████████████████████ {posterior[(1,1)]:.0%} ↑
""")
print("總結")
print(f"""
四個後驗機率計算完成：

如果收到悲觀報告 (X=0):
  P(θ=0|X=0) = {posterior[(0,0)]:.4f}  (低需求的機率)
  P(θ=1|X=0) = {posterior[(1,0)]:.4f}  (高需求的機率)

如果收到樂觀報告 (X=1):
  P(θ=0|X=1) = {posterior[(0,1)]:.4f}  (低需求的機率)
  P(θ=1|X=1) = {posterior[(1,1)]:.4f}  (高需求的機率)
""")
