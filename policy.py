from simulation import SimulationEnv, PICKING_HISTORY, NEED_MONTH, get_date, SKU_DIC_TEMP
import time

SHORT_TERM_DATA_DAYS = 30
PICKING_DIC_HISTORY = {}
for PER_PICKING in range(len(PICKING_HISTORY)-1, 0, -1):
    SKU_ID = int(PICKING_HISTORY[PER_PICKING][3])
    SKU_QTY = int(PICKING_HISTORY[PER_PICKING][4])
    SKU_DATE = PICKING_HISTORY[PER_PICKING][0]
    if SKU_ID not in SKU_DIC_TEMP:
        continue
    # 支转换成箱（保留小数）
    if PICKING_HISTORY[PER_PICKING][5] == 'IT':
        SKU_BUOM = SKU_DIC_TEMP[SKU_ID][0]
        SKU_QTY = SKU_QTY / SKU_BUOM
    SKU_MONTH, SKU_DAY = get_date(SKU_DATE)
    if SKU_MONTH != NEED_MONTH and SKU_QTY < 18:
        if SKU_ID in PICKING_DIC_HISTORY:
            PICKING_DIC_HISTORY[SKU_ID][0] += SKU_QTY
        else:
            PICKING_DIC_HISTORY[SKU_ID] = [SKU_QTY, SKU_DIC_TEMP[SKU_ID][2]]

print(PICKING_DIC_HISTORY)
raise Exception('stop')

env = SimulationEnv()  # 构建仿真环境
start = time.perf_counter()

# 开始仿真
for i in range(1000):
    env.reset({})  # 重置仿真环境
    goods_cells_empty_num_min = 10320
    while True:
        ms_list = get_ms_list()
        observation, reward, done, info = env.step(ms_list)  # MS_LIST格式: {SKU编号：[最小值，最大值],}

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