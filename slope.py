import numpy as np

x = np.array([0, 1, 2, 3, 4])
y = np.array([0, 1, 4, 9, 16])

# 计算所有点的斜率
slopes = np.gradient(y, x)  # x 可以是非均匀的

print("各点斜率:", slopes)  # [1.  2.5 4.  5.5 7. ]
print(f"在 x=2 处的斜率 ≈ {slopes[3]}")  # 4.0（非常准确）