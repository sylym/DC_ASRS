# DC_ASRS


本仓库为清华暑期挑战项目0620保洁DC自动货架系统(ASRS)的python仿真。

仿真使用[OpenAI Gym](https://github.com/openai/gym) 风格API

 **一些重要更新**:
- v2.6: [simulation](simulation.py) bug修复
- v2.5: [simulation](simulation.py) 更新obs[4]为SKU在多穿每个货格中的箱数
- v2.4：[simulation](simulation.py) 添加每日更新多穿列表后触发min补货检测
- v2.3: 根据需求更新 [sku_info](sku_info_new.csv)
- v2.2: [simulation](simulation.py) 修正为持续仿真并选取某日到某日进行测评
- v2.1: [simulation](simulation.py) 修正为大于18箱的订单都从多穿发货，reward添加时间成本和人员成本，添加仿真使用 [example](example.py)


 



## DC_ASRS仿真使用
### 1. 准备工作

a) 下载并解压 [DC_ASRS.v2.4](https://github.com/sylym/DC_ASRS/releases/download/DC_ASRS_v2.4/DC_ASRS.v2.4.rar)

b) 下载最新版本的 [simulation](simulation.py) 并替换DC_ASRS v2.4文件夹下的simulation.py

c) 根据样例文件 [example](example.py) 调用仿真 [simulation](simulation.py) API


```python
from simulation import SimulationEnv


MS_LIST = {}  # {SKU编号：[最小值，最大值]}

env = SimulationEnv()  # 构建仿真环境
env.reset()  # 重置仿真环境

while True:
    observation, reward, done, info = env.step(MS_LIST)  # 进行每日仿真
    if done:
        break
```

### 2. 仿真API文档

SimulationEnv为仿真环境类，其中包含仿真环境的初始化、进行每日仿真等方法。

#### a) env.reset()
```python
env.reset()
```
对仿真类进行初始化。

#### b) env.step()
```python
obs, reward, done, info = env.step(MS_LIST)
```

传入每日多穿列表并进行一天的仿真

**传入参数：**

- MS_LIST：每日的多穿列表, 数据类型为dict, 键值为SKU编号(int)，值为包含min值和max值的list。

```python
MS_LIST = {82292589: [0, 48], 082292590: [2, 50], 82292591: [3, 18]}
```

**返回值：**

- obs：仿真环境的状态，数据类型为list。
    - obs[0]：多穿空货格数，数据类型为int。
    - obs[1]：不同SKU在多穿内箱数，数据类型为dict。键为SKU编号(int)，值为多穿内箱数(float)。
    - obs[2]：不同SKU在立库散拣后剩余箱数，数据类型为dict。键为SKU编号(int)，值为散拣后剩余箱数(float)。
    - obs[3]：仿真当天的所有订单，数据类型list，列表中每个元素为每个订单行(list)，订单行list样例：[SKU编号(int), 出货箱数(float), [一箱支数(int)，一板箱数(int)，多穿料箱可放箱数(int)]]。
    - obs[4]：不同SKU在多穿货格内的情况，数据类型为dict。键为SKU编号(int)，值为该SKU在不同多穿货格内的箱数(list), 样例：[该SKU在货格1箱数(float), 该SKU在货格2箱数(float)]。
    - obs[5]：仿真当天为第几天，数据类型为int。

```python
obs = [7020, {82303465: 12, 82305681: 14.0}, {82303465: 12, 82305681: 11.1}, [[82303465, 12.0, [1, 108, 4]], [82305681, 10.0, [12, 24, 2]]], {82315635: [6, 6, 5.0], 82305682: [2.0, 1]}, 1]
```

- reward：仿真的结果，数据类型为list。
    - reward[0]：累计多穿拣选的箱数，数据类型为float。
    - reward[1]：累计订单触发的补货数，数据类型为float。
    - reward[2]：累计出货箱数，数据类型为float。
    - reward[3]：累计时间成本，数据类型为float。
    - reward[4]：累计人员成本，数据类型为float。
  
  注意：reward返回值只有在仿真天数在评测开始之后才有意义

```python
reward = [123523.08333333374, 1447.83333333343, 288941.83333333343, 31867.222222249267, 288941.8333333335]
```
- done：仿真是否结束，数据类型为bool。

- info：仿真状态，数据类型str
    - "restriction!!!": 不满足限制条件强制结束
    - "normal": 仿真正常运行/结束

### 3. 仿真可调参数

```python
START_EVALUATING_DAYTIME = [8, 11] # 8月11日
END_EVALUATING_DAYTIME = [9, 10] # 9月10日
```
START_EVALUATING_DAYTIME：评测开始日期（当日记入评测结果），数据类型为list，样例：[月份(int), 日期(int)]。

END_EVALUATING_DAYTIME：评测结束日期（当日记入评测结果），数据类型为list，样例：[月份(int), 日期(int)]。

## 加速仿真

a) 使用 [pypy解释器](https://www.pypy.org/) 代替python解释器，使用方法参考 [官方文档](https://doc.pypy.org/en/latest/)

b) 改变 [仿真](simulation.py)，使其直接返回obs

```python
def step(self, ms_list):
    obs, reward, done, info = self.work.start_work_step(ms_list)
    # 返回obs的深拷贝会大幅度降低仿真性能, 如需要更快仿真速度, 可以改为直接返回obs, 但是不规范的使用可能obs可能导致出现仿真异常
    return copy.deepcopy(obs), reward, done, info
```
将 copy.deepcopy(obs) 改为 obs

注意：若直接返回obs时，在调用obs时要注意 [python的list拷贝性质](https://blog.csdn.net/qq_24502469/article/details/104185122)

## 鸣谢
我们的代码参考如下仓库:
* [OpenAI Gym](https://github.com/openai/gym)
