import math

bigm = 8 # 最大运输量
action_list = [0,1,2,3,4,5,6,7,8] # shipping decision 集合
demand_possibility_list_1 = [0.16, 0.68, 0.16] # Demand Possibility before Nov 11
demand_possibility_list_2 = [0.02, 0.14, 0.34, 0.34, 0.14, 0.02] # Demand Possibility on Nov 11
demand_possibility_list_3 = [0.5, 0.5] # Demand Possibility after Nov 11

# 定义发货决策与时间的关系函数
def a_func(t, s_t):
    if t < 36: # daily shipping options
        a_list = action_list
    else: # shipping amount at last day is computed complying with the model formular
        b1_t = s_t[3]
        b2_t = s_t[4]
        b3_t = s_t[5]
        q_t = s_t[1]
        temp1 = q_t - b3_t
        temp2 = b1_t + b2_t - max(temp1, 0)
        temp3 = max(temp2, 0)
        a_t = min(temp3, bigm)
        a_list = [a_t]
    return a_list


# 时间——最大需求定义函数
def d_func(t):
    if t <= 20:
        demand = 5  # 预售期最大需求
    elif t == 21:
        demand = 11  # 双十一当天最大需求
    else:
        demand = 3  # 保价期最大需求
    dMax = demand + 1
    return dMax


# 时间——需求——概率定义函数
def pro_func(t, demand):
    # 取泊松分布
    # 保证最大需求位于 均值加两个标准差 附近，即涵盖95%的数据
    if t <= 20:
        d1p_list = demand_possibility_list_1
        demandIndex = int((demand - 1) / 2)  # 仅当需求是奇数，且需求范围是2，才是这样计算
        pro_res = d1p_list[demandIndex]
    elif t == 21:
        d2p_list = demand_possibility_list_2
        demandIndex = int((demand-1) / 2)  # 仅当需求是奇数，且需求范围是2，才是这样计算
        pro_res = d2p_list[demandIndex]
    else:
        d3p_list = demand_possibility_list_3
        demandIndex = int((demand-1) / 2)  # 仅当需求是奇数，且需求范围是2，才是这样计算
        pro_res = d3p_list[demandIndex]
    return pro_res


# 定义运费函数
def gt_func(t, a_t):
    # 关于时间
    if t <= 21:
        c_t = 25
    elif t == 22:
        c_t = 32.5
    else:
        c_t = 27.5
    # 关于运量
    if a_t <= 3:
        c_a = 7.5
    elif a_t <= 5:
        c_a = 5
    elif a_t <= 7:
        c_a = 2.5
    else:
        c_a = 0
    # 单位运费
    cost = c_t + c_a
    # 总运费
    total_cost = cost * a_t
    return total_cost


# 定义履约比例与定金比例的相关函数
def k_func(i):
    i_value = i
    if i_value >= 0.2:
        settlement_rate = 1
    elif i_value >= 0.15:
        settlement_rate = 0.95
    elif i_value >=0.1:
        settlement_rate = 0.9
    elif i_value >=0.05:
        settlement_rate = 0.85
    else:
        settlement_rate = 0.8
    return settlement_rate


# 定义判断小包裹运输量的函数
def parcel(t, s_t):
    q_t = s_t[1]
    b3_t = s_t[5]
    if t < 36:
        parcel_t = max(0, b3_t - q_t)
    else:
        b1_t = s_t[3]
        b2_t = s_t[4]
        b3_t = s_t[5]
        temp1 = max(0, q_t - b3_t)
        temp2 = b1_t + b2_t - temp1 - bigm
        parcel_t = max(0,temp2) + max(0, b3_t - q_t) # NOTE: 已更正，原程序漏了后面的一项
    return parcel_t


# 定义状态转移的函数
def state_trans(t, s_t, demand, a_t, trans_pro,ri):
    # 数组s_t = (w_t, q_t, b0_t, b1_t, b2_t, b3_t, pro)
    # 可能采取的决策数目
    ri_value = ri
    at_num = len(action_list)
    # 获取当前的状态
    w_t = s_t[0]
    q_t = s_t[1]
    b0_t = s_t[2]
    b1_t = s_t[3]
    b2_t = s_t[4]
    b3_t = s_t[5]
    state_pro_t = s_t[6]
    state_pro_t1 = state_pro_t * trans_pro / at_num
    # 获取当前需要小包裹运输的量
    par_t = parcel(t, s_t)
    # 进行状态转移。计算下一个状态的结果
    if t <= 20:
        # 更新状态
        b0_t1 = demand
        b1_t1, b2_t1, b3_t1 = 0, 0, 0
        w_t1 = w_t + b0_t - a_t
        q_t1 = q_t + a_t
        s_t1 = (w_t1, q_t1, b0_t1, b1_t1, b2_t1, b3_t1, state_pro_t1)
        return s_t1
    elif t == 21:
        # 更新状态
        b0_t1 = 0
        b1_t1 = demand
        b2_t1 = 0
        b3_t1 = 0
        # 向下取整
        w_t1 = w_t + b0_t - a_t
        q_t1 = q_t + a_t
        s_t1 = (w_t1, q_t1, b0_t1, b1_t1, b2_t1, b3_t1, state_pro_t1)
        return s_t1
    elif t == 22:
        # 更新状态
        b0_t1 = 0
        b1_t1 = demand
        # 向下取整
        temp1 = q_t - math.floor((w_t + q_t)*k_func(ri_value)) - b1_t
        tem1 = q_t - math.floor((w_t + q_t)*k_func(ri_value))
        # tem2 = b1_t - max(0, tem1) - max(0, w_t) # note: To check
        tem2 = b1_t - max(0, tem1) # note: To check
        w_t1 = max(0, max(0,w_t) + max(tem2, 0) - a_t)
        q_t1 = max(0, temp1) + a_t
        if temp1 >= 0:
            b2_t1 = 0
        else:
            b2_t1 = math.floor((w_t + q_t)*k_func(ri_value)) + b1_t - q_t
        b3_t1 = 0
        s_t1 = (w_t1, q_t1, b0_t1, b1_t1, b2_t1, b3_t1, state_pro_t1)
        return s_t1
    elif t in list(range(23, 36)):
        # 更新状态
        b0_t1 = 0
        b1_t1 = demand
        temp1 = b2_t + b3_t
        temp2 = b1_t + b2_t + b3_t
        temp3 = q_t - temp2
        tem1 = q_t - b3_t
        tem2 = max(tem1, 0) - b2_t
        # tem3 = b1_t - max(tem2, 0) - max(0, w_t) # note: old version
        tem3 = b1_t - max(tem2, 0)
        w_t1 = max(0, w_t + max(tem3, 0) - a_t - max(0,b3_t-q_t))
        # w_t1 = w_t + max(tem3, 0) - a_t - par_t
        q_t1 = max(0, temp3) + a_t
        if q_t < b3_t:
            b2_t1 = b1_t  # b2_t1 = b1_t = demand
            b3_t1 = b2_t  # b3_t1 = b2_t
        elif b3_t <= q_t < temp1:
            b3_t1 = temp1 - q_t
            b2_t1 = b1_t
        elif temp1 <= q_t < temp2:
            b2_t1 = temp2 - q_t
            b3_t1 = 0
        elif q_t >= temp2:
            b2_t1 = 0
            b3_t1 = 0
        else:
            print(f'第{t}天报错')
            b2_t1 = 0
            b3_t1 = 0
        b0_t1 = max(0, b3_t1 - q_t1)  # 暂时性替换
        s_t1 = (w_t1, q_t1, b0_t1, b1_t1, b2_t1, b3_t1, state_pro_t1)
        return s_t1
    # 最后一天的下一阶段状态应为：s_t1 = (0, 0, 0, 0, 0, 0, 1.0)
    else:
        s_t1 = (0, 0, 0, 0, 0, 0, 1.0)
        return s_t1


# 定义决策收益函数
def income_func(t, s_t, a_t, parm_dict):
    # 数组s_t = (w_t, q_t, b0_t, b1_t, b2_t, b3_t)
    p_1 = parm_dict['p1']  # 预售价格
    p_2 = parm_dict['p2']  # 双十一当天价格
    p_3 = parm_dict['p3']  # 保价期价格
    p_4 = parm_dict['p4']  # 残值
    c_1 = parm_dict['c1']  # 单位产品成本
    c_2 = parm_dict['c2']  # 固定运费
    c_3 = parm_dict['c3']  # 小包裹单位运费成本
    h_1 = parm_dict['h1']  # 海外仓单位成本
    h_2 = parm_dict['h2']  # 国内仓单位成本
    ri = parm_dict['ri']  # 定金比例
    # 当天状态各个变量的取值
    w_t = s_t[0]
    q_t = s_t[1]
    b0_t = s_t[2]
    b1_t = s_t[3]
    b2_t = s_t[4]
    b3_t = s_t[5]
    par_t = parcel(t, s_t)
    # 预售期的利润
    if t <= 21:
        if a_t > 0:
            temp = max(0, w_t + b0_t - a_t)
            h1_cost = h_1*temp
            h2_cost = h_2*q_t
            trans_cost = gt_func(t, a_t) + c_2
            revenue = ri*p_1*b0_t - h1_cost - h2_cost - trans_cost
            return revenue, h1_cost, h2_cost, trans_cost
        else:
            temp = max(0, w_t + b0_t)
            h1_cost = h_1 * temp
            h2_cost = h_2 * q_t
            trans_cost = 0
            revenue = ri*p_1*b0_t - h1_cost - h2_cost
            return revenue, h1_cost, h2_cost, trans_cost
    # 双十一当天的利润
    elif t == 22:
        if a_t > 0:
            temp1 = math.floor((w_t + q_t) * k_func(ri))
            temp2 = max(0, w_t + b1_t - a_t)
            temp3 = max(0, q_t - temp1 - b1_t)
            h1_cost = h_1 * temp2
            h2_cost = h_2 * temp3
            trans_cost = gt_func(t, a_t) + c_2
            # note: 原收入项有错，已订正
            revenue = (1-1.3*ri)*p_1*temp1 -c_1*temp1 + (p_2-c_1)*b1_t - h1_cost - h2_cost - trans_cost
            return revenue, h1_cost, h2_cost, trans_cost
        else:
            temp1 = math.floor((w_t + q_t) * k_func(ri))
            temp2 = max(0, w_t + b1_t)
            temp3 = max(0, q_t - temp1 - b1_t)
            h1_cost = h_1 * temp2
            h2_cost = h_2 * temp3
            trans_cost = 0
            revenue = (1-1.3*ri)*p_1*temp1 -c_1*temp1 + (p_2-c_1)*b1_t - h1_cost - h2_cost
            return revenue, h1_cost, h2_cost, trans_cost
    # 保价期利润
    elif t in list(range(23, 36)):
        if a_t > 0:
            temp1 = max(0, w_t + b1_t - a_t - max(0,b3_t-q_t))
            temp2 = max(0, q_t - b1_t - b2_t - b3_t)
            h1_cost = h_1 * temp1
            h2_cost = h_2 * temp2
            trans_cost = gt_func(t, a_t) + c_2
            revenue = (p_3-c_1)*b1_t - h1_cost - h2_cost - trans_cost - c_3*max(0,b3_t-q_t)
            return revenue, h1_cost, h2_cost, trans_cost
        else:
            temp1 = max(0, w_t + b1_t - max(0,b3_t-q_t))
            temp2 = max(0, q_t - b1_t - b2_t - b3_t)
            h1_cost = h_1 * temp1
            h2_cost = h_2 * temp2
            trans_cost = 0
            revenue = (p_3-c_1)*b1_t - h1_cost - h2_cost - c_3*max(0,b3_t-q_t)
            return revenue, h1_cost, h2_cost, trans_cost
    # 最后一天的利润，考虑残值处理
    else:
        h1_cost, h2_cost = 0, 0
        act_list = a_func(t,s_t)
        bulkshipping: int = int(act_list[0])
        if bulkshipping > 0:
            trans_cost = gt_func(t,bulkshipping) + c_2
        else:
            trans_cost = 0
        temp1 = max(0,q_t-b1_t-b2_t-b3_t)
        temp2 = max(0, w_t-(b1_t+b2_t-max(0,q_t-b3_t)))
        # original version that does not consider P5
        # revenue = (p_3-c_1)*b1_t + (p_4-c_1)*temp1 + (p_4-c_1)*temp2 - c_3*par_t - trans_cost
        # Below is the version that assumes P5 = C1
        revenue = (p_3 - c_1) * b1_t + (p_4 - c_1) * temp1 + 0 * temp2 - c_3 * par_t - trans_cost
        return revenue, h1_cost, h2_cost, trans_cost

        # 下面是旧程序：计算最后一天的收益
        # temp1 = max(0, q_t - b3_t)
        # temp2 = b1_t + b2_t - temp1
        # if q_t < b3_t: # b3_t需要expedited shipping
        #     temp3 = max(0, w_t - b1_t - b2_t) # domestic满足b1和b2后，还剩多少
        #     h1_cost, h2_cost = 0, 0
        #     trans_cost = gt_func(t, a_t) + c_2
        #     revenue = (p_3-c_1)*b1_t + (p_4-c_1)*temp3 - trans_cost - c_3*par_t
        #     return revenue, h1_cost, h2_cost, trans_cost
        # elif temp2 >= w_t: # 无domestic剩余
        #     h1_cost, h2_cost = 0, 0
        #     trans_cost = gt_func(t, a_t) + c_2
        #     revenue = (p_3-c_1)*b1_t - trans_cost
        #     return revenue, h1_cost, h2_cost, trans_cost
        # elif temp2 in list(range(0, w_t)): # domestic有剩余
        #     h1_cost, h2_cost = 0, 0
        #     trans_cost = gt_func(t, a_t) + c_2
        #     revenue = (p_3-c_1)*b1_t + (p_4-c_1)*(w_t - temp2) - trans_cost
        #     return revenue, h1_cost, h2_cost, trans_cost
        # else:
        #     temp4 = q_t - b1_t - b2_t - b3_t
        #     h1_cost, h2_cost, trans_cost = 0, 0, 0
        #     revenue = (p_3-c_1)*b1_t + (p_4-c_1)*temp4 + p_4*max(0, w_t)
        #     return revenue, h1_cost, h2_cost, trans_cost


