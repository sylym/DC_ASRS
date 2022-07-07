from simulation import SimulationEnv


# 初始多穿库存
first_day_sku_dic = {}  # {SKU编号：多穿内箱数}
MS_LIST = {}  # {SKU编号：[最小值，最大值]}

env = SimulationEnv()  # 构建仿真环境
env.reset(first_day_sku_dic)  # 重置仿真环境

while True:
    observation, reward, done, info = env.step(MS_LIST)  # 进行每日仿真
    if done:
        break

'''
返回值
observation: [多穿空货格数, {SKU编号：多穿内箱数}, {SKU编号：立库散拣剩余箱}, [[SKU编号, 出货箱数],..前一日的所有订单], {SKU编号：[多穿货格零散箱数1, 多穿货格零散箱数2...]}, 仿真天数]
reward: [多穿拣选的箱数（累计）, 订单触发的补货数（累计）, 总出货箱数, 时间成本（累计）, 人员成本（累计）]
done: true: 仿真结束： false: 仿真未结束
info: restriction!!!: 不满足限制条件强制结束；normal: 仿真正常运行/结束
'''