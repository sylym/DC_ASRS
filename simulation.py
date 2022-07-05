"""
额外补充多穿补货规则:
1.整版补货优先补充立库散拣剩余箱(整版剩余箱)
2.补货只能补到空料箱中
3.触发补货时一次性补充足够的货
额外补充立库散拣出库规则:
1.立库散拣优先利用之前散拣剩余箱
额外补充多穿料箱出库规则:
1.料箱出库优先利用该SKU数量最少的料箱
"""
import calendar
import math
import csv
import copy

NEED_MONTH = 6  # 订单月份


SKU_DIC_TEMP = {}  # 减少使用次数 SKU编号(int)：[一箱支数(int)，一板箱数(int)，多穿料箱可放箱数(int)]

PICKING_LIST = [[] for _ in range(calendar.monthrange(2021, NEED_MONTH)[1])]
# [[[SKU编号(int), 订单箱数(float), [一箱支数(int)，一板箱数(int)，多穿料箱可放箱数(int)]],..]，[第二天订单]]

# PICKING_LIST和SKU_DIC_TEMP的预处理
SKU_INFO = csv.reader(open('sku_info_new.csv', 'r'))
SKU_INFO = list(SKU_INFO)

for PER_SKU in range(1, len(SKU_INFO)):
    SKU_DIC_TEMP[int(SKU_INFO[PER_SKU][1])] = [int(SKU_INFO[PER_SKU][2]), int(SKU_INFO[PER_SKU][3]),
                                               int(SKU_INFO[PER_SKU][4])]

PICKING_HISTORY = csv.reader(open('picking_history.csv', 'r'))
PICKING_HISTORY = list(PICKING_HISTORY)


def get_date(date):
    t1 = date.split(' ')
    t2 = t1[0].split('/')
    return int(t2[1]), int(t2[2])


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
    if SKU_MONTH == NEED_MONTH:
        PICKING_LIST[SKU_DAY-1].append([SKU_ID, SKU_QTY, SKU_DIC_TEMP[SKU_ID]])


class Ms:
    def __init__(self, pr):
        self.sku_dic = {}  # SKU编号：多穿内箱数
        self.sku_scattered_dic = {}  # SKU编号：[多穿货格零散箱数1, 多穿货格零散箱数2...]
        self.goods_cells_empty_num = 10320  # 多穿空货格数
        self.sell_supplement_num = 0  # 订单触发的补货数（累计）
        self.ms_sell_num = 0  # 多穿拣选的箱数（累计）
        self.pr = pr
        self.restriction = False  # 是否触发限制条件

    # 出库更新sku_dic和sell_supplement_num
    def sell_manage(self, sku_id, sku_qty, sku_info):
        past_used_cells = math.ceil(self.sku_dic[sku_id] / sku_info[2])
        now_used_cells = math.ceil((self.sku_dic[sku_id] - sku_qty) / sku_info[2])
        self.goods_cells_empty_num += (past_used_cells - now_used_cells)
        self.sku_dic[sku_id] -= sku_qty

    # 补货更新sku_dic和sell_supplement_num
    def supplement_manage(self, sku_id, supplement_num, sku_info):
        past_used_cells = math.ceil(self.sku_dic[sku_id] / sku_info[2])
        now_used_cells = math.ceil((self.sku_dic[sku_id] + supplement_num) / sku_info[2])
        self.goods_cells_empty_num -= (now_used_cells - past_used_cells)
        self.sku_dic[sku_id] += supplement_num

    # 多穿出库
    def ms_sell(self, sku_id, sku_qty, sku_info):
        self.ms_sell_num += sku_qty
        if self.sku_dic[sku_id] >= sku_qty:
            self.sell_manage(sku_id, sku_qty, sku_info)
        else:
            surplus_qty = sku_qty - self.sku_dic[sku_id]
            self.sell_manage(sku_id, self.sku_dic[sku_id], sku_info)
            # 进行订单触发的补货
            self.ms_supplement(sku_id, surplus_qty, sku_info, "sell")
            # 检测是否触发限制条件
            if self.goods_cells_empty_num < 0:
                self.restriction = True
            self.sell_manage(sku_id, surplus_qty, sku_info)

    # 订单和min触发的多穿补货
    def ms_supplement(self, sku_id, supplement_num, sku_info, supplement_type):
        if supplement_type == 'sell':
            self.sell_supplement_num += 1
        if self.pr[sku_id] >= supplement_num:
            self.supplement_manage(sku_id, self.pr[sku_id], sku_info)
            self.pr[sku_id] = 0
        else:
            supplement_num -= self.pr[sku_id]
            self.pr[sku_id] = 0
            supplement_num = sku_info[1] * math.ceil(supplement_num / sku_info[1])
            self.supplement_manage(sku_id, supplement_num, sku_info)


class Mainwork:
    def __init__(self, first_day_sku_dic):
        self.daytime = 0
        self.picking_list_day = []
        self.total_sell_num = 0  # 总出货箱数
        self.pr = {}  # SKU编号：立库散拣剩余箱
        self.ms = Ms(self.pr)
        self.ms.sku_dic = first_day_sku_dic.copy()  # 自定义初始多穿库存
        # 计算初始多穿空货格数并填充sku_scattered_dic
        for sku_id in first_day_sku_dic:
            self.ms.goods_cells_empty_num -= math.ceil(self.ms.sku_dic[sku_id] / SKU_DIC_TEMP[sku_id][2])
            self.ms.sku_scattered_dic[sku_id] = [self.ms.sku_dic[sku_id] % SKU_DIC_TEMP[sku_id][2]]

    # 添加每天的订单
    def add_day_picking(self):
        self.daytime += 1
        self.picking_list_day = PICKING_LIST[self.daytime - 1]

    # 立库出库
    def pr_sell(self, sku_id, sku_qty, ms_list, sku_info):
        # 立库散拣优先利用散拣剩余箱
        if sku_qty > self.pr[sku_id]:
            sku_qty -= self.pr[sku_id]
            self.pr[sku_id] = 0
        else:
            self.pr[sku_id] -= sku_qty
            return 0
        sku_qty_surplus = sku_qty % sku_info[1]
        if sku_id in ms_list:
            if ms_list[sku_id][1] < (sku_info[1] - sku_qty_surplus + self.ms.sku_dic[sku_id]):
                self.pr[sku_id] = sku_info[1] - sku_qty_surplus
            else:
                self.ms.supplement_manage(sku_id, sku_info[1] - sku_qty_surplus, sku_info)
                # 检测是否触发限制条件
                if self.ms.goods_cells_empty_num < 0:
                    self.ms.restriction = True
                self.pr[sku_id] = 0
        else:
            self.pr[sku_id] = sku_info[1] - sku_qty_surplus

    # 主函数(ms_list格式：SKU编号：[最小值，最大值])
    def start_work_step(self, ms_list):
        self.add_day_picking()
        for i in range(len(self.picking_list_day)):
            # 获取一个订单的信息并预处理
            sku_id = self.picking_list_day[i][0]
            sku_qty = self.picking_list_day[i][1]
            sku_info = self.picking_list_day[i][2]
            self.total_sell_num += sku_qty
            if sku_id not in self.ms.sku_dic:
                self.ms.sku_dic[sku_id] = 0
            if sku_id not in self.pr:
                self.pr[sku_id] = 0
            # 订单出货
            if sku_id in ms_list:
                if sku_qty >= 18:
                    self.total_sell_num -= sku_qty  # 计算总出货箱数不计算大于等于18箱的订单
                    self.pr_sell(sku_id, sku_qty, ms_list, sku_info)
                else:
                    self.ms.ms_sell(sku_id, sku_qty, sku_info)
            else:
                # 尽可能从多穿出货
                if self.ms.sku_dic[sku_id] >= sku_qty:
                    self.ms.sku_dic[sku_id] -= sku_qty
                    self.ms.ms_sell_num += sku_qty
                else:
                    sku_qty -= self.ms.sku_dic[sku_id]
                    self.ms.ms_sell_num += self.ms.sku_dic[sku_id]
                    self.ms.sku_dic[sku_id] = 0
                    self.pr_sell(sku_id, sku_qty, ms_list, sku_info)
            # 进行min触发的补货
            if sku_id in ms_list:
                if self.ms.sku_dic[sku_id] < ms_list[sku_id][0]:
                    self.ms.ms_supplement(sku_id, ms_list[sku_id][0] - self.ms.sku_dic[sku_id], sku_info, "min")
            # 检测是否触发限制条件
            if self.ms.goods_cells_empty_num < 0 or self.ms.restriction:
                self.ms.restriction = True
                break
        # 检测仿真是否结束
        obs = [self.ms.goods_cells_empty_num, self.ms.sku_dic, self.pr, self.picking_list_day,
               self.ms.sku_scattered_dic, self.daytime]
        reward = [self.ms.ms_sell_num, self.ms.sell_supplement_num, self.total_sell_num]
        if self.ms.restriction:
            return obs, reward, True, "restriction!!!"
        elif self.daytime == calendar.monthrange(2021, NEED_MONTH)[1]:
            return obs, reward, True, "normal"
        else:
            return obs, reward, False, "normal"


# 仿真接口
class SimulationEnv:
    def __init__(self):
        self.work = Mainwork({})

    def reset(self, first_day_sku_dic):
        self.work = Mainwork(first_day_sku_dic)

    def step(self, ms_list):
        obs, reward, done, info = self.work.start_work_step(ms_list)
        # 返回obs的深拷贝会大幅度降低仿真性能, 如需要更快仿真速度, 可以改为直接返回obs, 但是不规范的使用可能obs可能导致出现仿真异常
        return copy.deepcopy(obs), reward, done, info
