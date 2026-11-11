import copy
import datetime
import Function_part as fp
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd

from Function_part import k_func

# from collections import Counter

demand_mean1 = 3.0
demand_mean2 = 6.0
demand_mean3 = 2.0

def mdp_solve(parameter_dict):
    start_time = datetime.datetime.now()

    # 参数设置 - 字典类型
    parameter_dict = parameter_dict
    ri_value: float = parameter_dict['ri'] # Note: 新加

    # 输出各项参数设置
    print('参数名列表:')
    parameter_list = list(parameter_dict.keys())
    print(parameter_list)
    print('参数数值:')
    for i in parameter_dict.keys():
        parameter_value = parameter_dict[i]
        print(f'{parameter_value}')

    # 初始化各个变量
    w_t = 0
    q_t = 0
    b0_t = 0
    b1_t = 0
    b2_t = 0
    b3_t = 0
    pro = 1.0
    # 定义状态变量为元祖
    s_t = (w_t, q_t, b0_t, b1_t, b2_t, b3_t, pro)

    # 存储每一天的状态情况-总表：嵌套列表，外层可以包括多个[s_t]列表，而一个【s_t]列表，可包括多个s_t元祖
    # 添加新天的状态：state_list.append([new_s_t])
    # 或在某天内添加新状态：state_list[day].append(new_s_t)
    state_list = [[s_t]]
    # print(f'state_list: {state_list}')

    # 存储加总概率后的状态表
    true_state_list = []
    res_list = []
    print('下面输出从第0天到第36天的状态数目：')
    # 从第0天开始，到第36天为止，遍历每一天的可能状态
    for t in range(37):
        # 获得当天的所有状态集合
        raw_state_t = state_list[t]  # list
        # if t == 0: print(f'raw_state_t: {raw_state_t}')
        # if t == 1: print(f'raw_state_t: {raw_state_t}')
        # if t == 2: print(f'raw_state_t: {raw_state_t}')
        # 将重复的集合合并为一个集合，并加总其概率
        combined_dict = {} # 定义为字典
        for item in raw_state_t:
            key = item[:-1]  # 前六个元素作为键
            prob = item[-1]  # 最后一个元素作为概率
            key = tuple(key)  # 将键转换为元组，因为字典的键必须是不可变类型
            if key in combined_dict:
                combined_dict[key] += prob
            else:
                combined_dict[key] = prob
        # 合并成新的状态列表
        state_t = []
        for key, prob in combined_dict.items():
            state_t.append((key[0], key[1], key[2], key[3], key[4], key[5], prob))
        # 记录
        true_state_list.append(state_t)
        # 记录该状态下的决策结果
        state_res = {}  # dict
        # 定义空列表存储下一天的状态集合
        state_t1 = []  # list
        print(f'{len(state_t)}')
        # if t == 36: print(f'state_t: {state_t}')

        # 遍历当天整合的状态列表，并加入action，形成新的状态列表
        for s_t in state_t:
            state_at = {}
            # 当天的流程为：来订单需求，进行决策，进行状态转移
            # 遍历需求,进行发货决策
            for a_t in fp.a_func(t, s_t):
                # 当前决策的收益
                income, h1_cost, h2_cost, trans_cost = fp.income_func(t, s_t, a_t, parameter_dict)

                # 记录该决策下可能产生的状态
                next_state = []
                # 记录状态相对应的转移概率
                st_st1_list = []

                # for demand in range(fp.d_func(t)):
                # 修改的尝试需求
                if t <= 20:
                    for demand in [1,3,5]:
                        # 下一阶段的订单需求，可以为0
                        # 定义字典存储决策、状态、概率、收益
                        # 获得需求概率
                        st_st1 = fp.pro_func(t, demand)
                        # 获得下一个状态
                        st_1 = fp.state_trans(t, s_t, demand, a_t, st_st1,ri_value)
                        # 记录
                        st_st1_list.append(st_st1)
                        next_state.append(st_1)
                        state_t1.append(st_1)
                elif t == 21:
                    for demand in [1,3,5,7,9,11]:
                        # 下一阶段的订单需求，可以为0
                        # 定义字典存储决策、状态、概率、收益
                        st_st1 = fp.pro_func(t, demand)
                        # 获得下一个状态
                        st_1 = fp.state_trans(t, s_t, demand, a_t, st_st1,ri_value)
                        # 记录
                        st_st1_list.append(st_st1)
                        next_state.append(st_1)
                        state_t1.append(st_1)
                else:
                    for demand in [1,3]:
                        # 下一阶段的订单需求，可以为0
                        # 定义字典存储决策、状态、概率、收益
                        st_st1 = fp.pro_func(t, demand)
                        # 获得下一个状态
                        st_1 = fp.state_trans(t, s_t, demand, a_t, st_st1,ri_value)
                        # 记录
                        st_st1_list.append(st_st1)
                        next_state.append(st_1)
                        state_t1.append(st_1)
                # 存到字典中
                at_result = {'income': income, 'h1_cost': h1_cost, 'h2_cost': h2_cost, 'trans_cost': trans_cost,
                             'trans_pro': st_st1_list, 'next_state': next_state}
                state_at[a_t] = at_result  # dict
            state_res[s_t] = state_at  # dict

        # state_list应包含t个列表，每个列表包含第t天的所有可能状态
        state_list.append(state_t1)
        # res_list应该包含t个字典，每个字典包含第t天的所有可能状态以及决策结果
        res_list.append(state_res)
    # 添加最后一天的状态
    true_state_list.append([(0, 0, 0, 0, 0, 0, 1.0)])

    # 采用逆推法，计算最优的决策顺序
    # 首先设定第37天的结束状况
    st_last_list = true_state_list[37]
    last_st_value = {}
    for st_last in st_last_list:
        st_key = tuple(st_last[:6])
        last_st_value[st_key] = 0
    policy_set = []
    total_pro = []

    # 记录绘制边界需要的数据，每一天各个库存下的最优决策
    # 从第36天开始逆推
    frontier_set = []
    for t in range(36, -1, -1):
        # 存储每一天的最优决策
        stage_frontier = []
        # 获得t天可能的状态结果及决策结果
        state_res = res_list[t]  # dict
        # 记录最优决策
        opt_policy = {}
        temp_dict = {}
        # 记录期望库存
        # 用以存储下一阶段的期望运货量
        ex_at = 0
        proba_total = 0
        # 遍历t天的状态，并求各个状态对应的最优策略以及期望最优值
        for state in state_res.keys():
            state_at = state_res[state]  # dict
            state_pro = state[6]
            # 记录当前状态的库存情况
            w_t = state[0]
            q_t = state[1]
            # 记录不同决策的期望收益
            at_value = {}
            for a_t in state_at.keys():
                at_result = state_at[a_t]
                income = at_result['income']  # float
                trans_pro = at_result['trans_pro']  # list
                last_state = at_result['next_state']  # list
                # 用以存储最优值函数
                opt_value = income
                for i in range(len(last_state)):
                    st = last_state[i]
                    temp_key = tuple(st[:6])
                    # 获取当前决策可以抵达的下一个状态的值函数
                    last_value = last_st_value[temp_key]  # float
                    p = trans_pro[i]  # float
                    opt_value = opt_value + last_value * p
                # 记录
                at_value[a_t] = opt_value  # dict
            # 获得该状态下的最优决策及最优值
            max_key = max(at_value, key=at_value.get)
            stage_frontier.append((w_t, q_t, max_key))
            max_value = at_value[max_key]
            # 存储状态以及对应最优值
            # 记录每天的最优决策以及结果
            ex_at += max_key*state_pro
            opt_policy[state] = max_key
            temp_dict[tuple(state[:6])] = max_value
            proba_total += state_pro
        # 更新字典
        last_st_value = temp_dict
        # 更新列表
        frontier_set.append(stage_frontier)
        policy_set.append(opt_policy)
        total_pro.append(proba_total)

    # 优化的最优值
    value_optimized = min(last_st_value.values())
    print(f'最优值为：{value_optimized} 元')
    # 查看每天所作决策的频率
    frequency_list = []
    # for t in range(37):
    #     policy_t = list(policy_set[t].values())
    #     frequency = Counter(policy_t).most_common()
    #     print(f'第{36 - t}天的决策结果为：{frequency}')
    #     frequency_list.append(frequency)

    # 运行时间
    end_time = datetime.datetime.now()
    duration = end_time - start_time
    print(f'单次MDP运行时间为{duration.total_seconds()}秒')

    # 查看某一天的最优决策边界
    frontier_set = frontier_set[::-1]
    data = frontier_set[21]
    # 使用字典构造DataFrame
    matrix_dict = {}
    for a, b, c in data:
        if a not in matrix_dict:
            matrix_dict[a] = {}
        matrix_dict[a][b] = c

    # 构造DataFrame
    df = pd.DataFrame(matrix_dict).sort_index().sort_index(axis=1)

    # 将缺失值填充为NA
    df.fillna(pd.NA, inplace=True)
    # 存储为Excel文件，每次运行时需删掉本地文件
    df.to_excel("output.xlsx")

    data_1 = frontier_set[21]
    # 使用字典构造DataFrame
    matrix_dict_1 = {}
    for a, b, c in data_1:
        if a not in matrix_dict_1:
            matrix_dict_1[a] = {}
        matrix_dict_1[a][b] = c

    # 构造DataFrame
    df_1 = pd.DataFrame(matrix_dict_1).sort_index().sort_index(axis=1)

    # 将缺失值填充为NA
    df_1.fillna(pd.NA, inplace=True)
    # 存储为Excel文件，每次运行时需删掉本地文件
    # df_1.to_excel("output_1.xlsx")

    # 记录最优决策下可以达到的状态
    whole_real_state = [[(0, 0, 0, 0, 0, 0, 1.0)]]
    temp_policy_set = policy_set[::-1]
    wt_set = []
    qt_set = []
    part_set = []
    at_set = []
    b1_t_set = []
    b2_t_set = []
    b3_t_set = []
    # 查看每天的期望库存
    for t in range(37):
        ex_wt = 0
        ex_qt = 0
        ex_part = 0
        ex_at = 0
        ex_b1 = 0
        ex_b2 = 0
        ex_b3 = 0
        # 当天可能达到的可能状态
        real_state_set = whole_real_state[t]
        temp_whole_pro = 0
        for st_i in real_state_set:
            i_pro = st_i[6]
            temp_whole_pro += i_pro
        # 记录真实的状态概率
        temp_real_state_dict = {}
        for st_j in real_state_set:
            j_pro = st_j[6]
            temp_real_state_dict[st_j] = j_pro / temp_whole_pro
        # 下一天可能达到的状态
        next_real_state = []
        # 获得t天可能的状态结果及决策结果
        state_res = res_list[t]  # dict
        temp_dict = {}
        if t < 36:
            for i in state_res.keys():
                temp_state = i[:6]
                temp_dict[temp_state] = i
            # 获得t天各个状态的最优决策
            opt_decision = temp_policy_set[t]
            for st in real_state_set:
                temp_st = st[:6]
                state = temp_dict[temp_st]
                wt = int(state[0])
                qt = int(state[1])
                if t <= 22:
                    par_t = 0
                else:
                    par_t = int(state[2])
                b1_t = int(state[3])
                b2_t = int(state[4])
                b3_t = int(state[5])
                pro = temp_real_state_dict[st]

                ex_wt += wt * pro
                ex_qt += qt * pro
                ex_part += par_t * pro
                ex_b1 += b1_t * pro
                ex_b2 += b2_t * pro
                ex_b3 += b3_t * pro

                # 计算最优决策下当前状态能达到的下一状态
                opt_key = opt_decision[state]
                ex_at += opt_key * pro
                opt_result = state_res[state][opt_key]
                opt_trans_pro = opt_result['trans_pro']
                opt_state = opt_result['next_state']
                for st_index in range(len(opt_state)):
                    temp_st = opt_state[st_index][:6]
                    real_st = temp_st + (opt_trans_pro[st_index],)
                    next_real_state.append(real_st)
            # 将重复的状态合并为一个状态，并加总其概率
            combined_dict_1 = {}
            for item in next_real_state:
                key = item[:6]  # 前六个元素作为键
                prob = item[6]  # 最后一个元素作为概率
                key = tuple(key)  # 将键转换为元组，因为字典的键必须是不可变类型
                if key in combined_dict_1:
                    combined_dict_1[key] += prob
                else:
                    combined_dict_1[key] = prob
            # 合并成新的状态列表
            next_real_state_t1 = []
            for key, prob in combined_dict_1.items():
                next_real_state_t1.append((key[0], key[1], key[2], key[3], key[4], key[5], prob))
            whole_real_state.append(next_real_state_t1)
        # 对于第36天，不需要考虑下一个阶段
        else:
            for state in real_state_set:
                wt = state[0]
                qt = state[1]
                par_t = state[2]
                b1_t = state[3]
                b2_t = state[4]
                b3_t = state[5]
                pro = temp_real_state_dict[state]
                ex_wt += wt * pro
                ex_qt += qt * pro
                ex_part += par_t * pro
                ex_b1 += b1_t * pro
                ex_b2 += b2_t * pro
                ex_b3 += b3_t * pro
                ex_at += fp.a_func(t, state)[0] * pro
        # 记录
        wt_set.append(ex_wt)
        qt_set.append(ex_qt)
        part_set.append(ex_part)
        b1_t_set.append(ex_b1)
        b2_t_set.append(ex_b2)
        b3_t_set.append(ex_b3)
        at_set.append(ex_at)

    wt_set.append(0)
    qt_set.append(0)
    part_set.append(0)
    b1_t_set.append(0)
    b2_t_set.append(0)
    b3_t_set.append(0)
    at_set.append(0)
    days_list = list(range(0, 38))
    foreign_inventory = copy.deepcopy(wt_set)
    domestic_inventory = copy.deepcopy(qt_set)
    parcel_volume = copy.deepcopy(part_set)
    shipment_volume = copy.deepcopy(at_set)
    positive_foreign_inv = [x if x>0 else 0 for x in foreign_inventory] # note: 新加，为了fig显示正数

    total_inventory = []
    for i in range(len(foreign_inventory)):
        temp_value = foreign_inventory[i] + domestic_inventory[i]
        total_inventory.append(temp_value)

    # 绘图表示

    # Note：新增图线supplier inventory，需检查是否有计算错误
    supplier_inv = [100.0] * 38
    unsatisfied_demand = [0.0] * 38 # accumulative demand
    satisfied_demand = [0.0] * 38 # items will leave the system on next day
    satisfied_demand_sum = [0.0] * 38

    for i in range(1,37):
        if i < 22:
            unsatisfied_demand[i] = unsatisfied_demand[i-1] + demand_mean1
            satisfied_demand[i] = 0
        elif i == 22:
            unsatisfied_demand[i] = unsatisfied_demand[i-1] * k_func(ri_value)
            satisfied_demand[i] = unsatisfied_demand[i] + b1_t_set[i] + b2_t_set[i] + b3_t_set[i] - b2_t_set[i+1] - b3_t_set[i+1]
            # determine the demand amount that will be fulfilled on Day 22 and will leave the inventory system at the end of Day 22
            satisfied_demand_sum[i] = satisfied_demand[i]
        else:
            satisfied_demand[i] =  b1_t_set[i] + b2_t_set[i] + b3_t_set[i] -b2_t_set[i+1] - b3_t_set[i+1]
            # determine the demand amount that will be fulfilled on Day i and will leave the inventory system at the end of Day i
            satisfied_demand_sum[i] = satisfied_demand_sum[i-1] + satisfied_demand[i]
    for i in range(0,23):
        supplier_inv[i] = supplier_inv[i] - max(0.0, domestic_inventory[i]) - foreign_inventory[i]
    for i in range(23,24):
        supplier_inv[i] = supplier_inv[i]-satisfied_demand[i-1]-max(0,domestic_inventory[i])-foreign_inventory[i]
    for i in range(24,37):
        supplier_inv[i] = supplier_inv[i]-satisfied_demand_sum[i-1]-domestic_inventory[i]-foreign_inventory[i]
    supplier_inv[37] = 0.0 # just an ending in the figure, which does not represent the inventory level on the day

    plt.rcParams['font.size'] = 11 # 全局默认字体大小
    plt.rcParams['axes.labelsize'] = 11 # 坐标轴标签
    plt.rcParams['axes.titlesize'] = 12 #子图标题大小
    plt.rcParams['xtick.labelsize'] = 10 # X轴刻度标签大小
    plt.rcParams['ytick.labelsize'] = 10 # Y轴刻度标签大小
    plt.rcParams['legend.fontsize'] = 10 # 图例文字大小
    plt.rcParams['figure.titlesize'] = 13 # 总标题大小
    plt.rcParams['lines.linewidth'] = 1.8 # 数据线宽度
    plt.rcParams['axes.linewidth'] = 1.2  # 坐标轴线宽
    plt.rcParams['axes.grid'] = True  # 是否显示网格线
    plt.rcParams['grid.linestyle'] = '--' # 网格线线型
    plt.rcParams['grid.alpha'] = 0.3 # 网格线透明度
    plt.rcParams['mathtext.fontset'] = 'stix'  # 数学公式字体

    # 设置字体的显示样式
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['axes.unicode_minus'] = False
    # 创建一个包含两个子图的网格，并设置比例
    fig = plt.figure(figsize=(10, 12))
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1], figure=fig)

    # note：新加fig设置
    plt.rcParams.update({
        # 'figure.dpi': 300,  # 输出分辨率（期刊要求≥300dpi）
        # 'savefig.dpi': 300,
        'savefig.format': 'pdf',  # 矢量图格式（避免像素化）
        'savefig.bbox': 'tight',  # 去除多余白边
        # 'figure.constrained_layout.use': True,  # 自动避免元素重叠
        'axes.spines.top': False,  # 隐藏顶部/右侧坐标轴（常见于期刊）
        'axes.spines.right': False,
    })

    # 定义学术色卡（避免红绿色盲问题）
    ACADEMIC_COLORS = [
        '#1f77b4',  # 蓝色
        '#d62728',  # 红色
        '#2ca02c',  # 绿色
        '#9467bd',  # 紫色
        '#8c564b',  # 棕色
    ]
    plt.rcParams['axes.prop_cycle'] = plt.cycler(color=ACADEMIC_COLORS)

    # 绘制第一个子图（运货量、国内仓库存、海外仓库存、速递量）
    # ax1 = plt.subplot(gs[0])
    ax1 = fig.add_subplot(gs[0])
    ax1.set_xticks(days_list)
    ax1.set_xticklabels(['{}'.format(i) for i in days_list])
    variables1 = [
        (supplier_inv, 'Supplier Inventory'),
        (domestic_inventory, 'Domestic Inventory'),
        (positive_foreign_inv, 'Overseas Inventory'),
        (shipment_volume, 'Bulk Shipping'),
        (parcel_volume, 'Expedited Shipping'),
    ]

    # 输出图例中的数据于 结果栏
    print("Supplier Inventory Amount:")
    rounded_list = [round(num, 2) for num in supplier_inv]
    print(rounded_list)
    print('Domestic Inventory Amount:')
    rounded_list = [round(num, 2) for num in domestic_inventory]
    print(rounded_list)
    print('Overseas Inventory Amount:')
    rounded_list = [round(num, 2) for num in foreign_inventory]
    print(rounded_list)
    print('Bulk Shipping Volume:')
    rounded_list = [round(num, 2) for num in shipment_volume]
    print(rounded_list)
    print("Expedited Shipping Volume:")
    rounded_list = [round(num, 2) for num in parcel_volume]
    print(rounded_list)

    for data, label in variables1:
        ax1.plot(days_list, data, label=label)
        for i in range(len(data)):
            ax1.text(days_list[i], data[i], f'{data[i]:.1f}', fontsize=9, ha='center', va='bottom')

    ax1.set_ylabel('Quantity')
    ax1.legend()

    # 绘制第二个子图（b1_t、b2_t、b3_t）
    # ax2 = plt.subplot(gs[1])
    ax2 = fig.add_subplot(gs[1])
    ax2.set_xticks(days_list)
    ax2.set_xticklabels(['{}'.format(i) for i in days_list])
    variables2 = [
        (b1_t_set, 'b1_t'),
        (b2_t_set, 'b2_t'),
        (b3_t_set, 'b3_t')
    ]

    # 输出图例中的数据于 结果栏
    print('b1_t state value:')
    rounded_list = [round(num, 2) for num in b1_t_set]
    print(rounded_list)
    print('b2_t state value:')
    rounded_list = [round(num, 2) for num in b2_t_set]
    print(rounded_list)
    print('b3_t state value:')
    rounded_list = [round(num, 2) for num in b3_t_set]
    print(rounded_list)

    for data, label in variables2:
        ax2.plot(days_list, data, label=label)
        for i in range(len(data)):
            ax2.text(days_list[i], data[i], f'{data[i]:.1f}', fontsize=9, ha='center', va='bottom')

    ax2.set_ylabel('Quantity')
    ax2.set_xlabel('Day')
    ax2.legend()

    # 在ax1和ax2创建后添加这些设置
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    p1 = parameter_dict['p1']
    p2 = parameter_dict['p2']
    p3 = parameter_dict['p3']
    p4 = parameter_dict['p4']
    c1 = parameter_dict['c1']
    c2 = parameter_dict['c2']
    c3 = parameter_dict['c3']
    h1 = parameter_dict['h1']
    h2 = parameter_dict['h2']
    ri = parameter_dict['ri']
    ki = fp.k_func(ri_value)
    # 添加标题和标签
    fig.suptitle(f'Expected Value Changes\n p1={p1}, p2={p2}, p3={p3}, p4={p4}, c1={c1}, c2={c2}, c3={c3},\n'
                 f'h1={h1}, h2={h2}, ri={ri}, ki={ki}', fontweight='bold', y=0.98)
    # 在plt.tight_layout前添加这些设置
    # plt.subplots_adjust(hspace=0.3)  # 调整子图间距
    # 调整子图间距
    # plt.tight_layout(rect=[0, 0, 1, 0.96])

    # 显示图形
    plt.show()

    return value_optimized, frequency_list

