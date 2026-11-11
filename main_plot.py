import matplotlib.pyplot as plt
import numpy as np
import mdp_func as mf

# 主要绘制收益变化曲线,以及决策变化曲线

# 基本参数设置
parameter_dict = {'p1': 100000, 'p2': 112000, 'p3': 124000, 'p4': 40000, 'c1': 64000,
                  'c2': 3150, 'c3': 56000, 'h1': 66, 'h2': 53, 'ri': 0.2}

# 海外仓的仓储成本
# h1_list = [2, 2.5, 3, 3.5, 4, 4.5, 5]
h1_list = [66]
# 固定运费成本
 # 小包裹运输成本
c3_list = [10, 12, 14, 15, 16, 18, 20]
# 定金比例
ratio_list = [0.1, 0.12, 0.14, 0.16, 0.18, 0.2]
# 预售价格变化
p1_list = [140, 145, 150, 155, 160]
# 订金变化，引发ki变化（支付尾款比例的变化）
ri_list = [0.2, 0.15, 0.1, 0.05]
# 最优收益变化
best_profit = []

# 逐一改变参数来观察效益和决策的变化
# 先改变h1查看情况
var = 'h1'
var_list = h1_list
for i in var_list:
    parameter_dict[var] = i
    # 调用马尔可夫决策过程进行求解
    # 返回最优收益期望值以及每一天的决策情况
    optimal_value, frequency_list = mf.mdp_solve(parameter_dict)
    best_profit.append(optimal_value)

# 绘图
# 设置中文字体的显示样式
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['axes.unicode_minus'] = False
# 创建主坐标轴
fig, ax1 = plt.subplots()
# 绘制收益曲线
ax1.plot(var_list, best_profit, color='darkblue', label='Optimal Profit')
# 设置x轴范围 x轴最小值至少为0；x轴最大值拓展1单位
x_range_min = max(min(var_list) - 1, 0)
x_range_max = max(var_list) + 1
#设置坐标轴标签
ax1.set_xlabel(var)
ax1.set_ylabel('Optimal Profit')
ax1.tick_params('y')
# 设置 x 轴刻度；将x轴氛围11个等间距可读
ax1.set_xticks(np.linspace(x_range_min, x_range_max, 11))

# 输出不同参数的设定
# 输出不同参数的模型最优目标值
# 输出不同参数的最优解图形

# print(f'参数{var}的不同取值为：{var_list}')
# print(f'对应的最优目标函数值为：{best_profit}')
# plt.show()