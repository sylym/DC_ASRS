from simulation import SimulationEnv
import time
import csv


# 初始多穿库存
first_day_sku_dic = {}  # {SKU编号：多穿内箱数}

# 读取测试选品表
MS_LIST = {}
TMP = csv.reader(open('tmp.csv', 'r'))
TMP = list(TMP)

for PER_TMP in range(1, len(TMP)):
    MS_LIST[int(TMP[PER_TMP][1])] = [int(TMP[PER_TMP][2]), int(TMP[PER_TMP][3])]

env = SimulationEnv()  # 构建仿真环境
start = time.perf_counter()

# 开始仿真
for i in range(1000):
    env.reset(first_day_sku_dic)  # 重置仿真环境
    goods_cells_empty_num_min = 10320
    while True:
        observation, reward, done, info = env.step(MS_LIST)  # MS_LIST格式: {SKU编号：[最小值，最大值],}
        if observation[0] < goods_cells_empty_num_min:
            goods_cells_empty_num_min = observation[0]
        if done:
            break

end = time.perf_counter()
availability = (reward[0] / reward[2]) * 100
print("多穿最少空货格数: %s" % goods_cells_empty_num_min)
print("多穿设备利用率: " + str(round(availability, 2)) + "%")
print("仿真状态: " + info)
print('仿真时长: %ss' % round((end-start), 2))


'''
返回值(！！！注意：对返回值进行修改前需进行深拷贝！！！)
observation: [多穿空货格数, {SKU编号：多穿内箱数}, {SKU编号：立库散拣剩余箱}, [[SKU编号, 出货箱数],..前一日的所有订单]]
reward: [多穿拣选的箱数（累计）, 订单触发的补货数（累计）, 总出货箱数]
done: true: 仿真结束： false: 仿真未结束
info: restriction!!!: 不满足限制条件强制结束；normal: 仿真正常运行/结束
'''
