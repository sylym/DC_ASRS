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
env.reset(first_day_sku_dic)  # 重置仿真环境
for _ in range(5):
    obs, reward, done, info = env.step(MS_LIST)
print(env.backup())
for _ in range(10):
    obs, reward, done, info = env.step(MS_LIST)  # MS_LIST格式: {SKU编号：[最小值，最大值],}
    env.restore()
    print(obs[0], info)

end = time.perf_counter()
print('仿真时长: %ss' % round((end-start), 2))