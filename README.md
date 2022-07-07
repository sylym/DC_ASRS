# DC_ASRS


本仓库为清华暑期挑战项目0620保洁公司(DC)自动货架系统(ASRS)的python仿真。

仿真使用[OpenAI Gym](https://github.com/openai/gym) 风格API

 **一些重要更新**:
- v2.3: 根据需求更新 [sku_info](sku_info_new.csv)
- v2.2: [simulation](simulation.py) 修正为持续仿真并选取某日到某日进行测评
- v2.1: [simulation](simulation.py) 修正为大于18箱的订单都从多穿发货,reward添加时间成本和人员成本， 添加仿真使用 [example](example.py)
- v2.0: [simulation](simulation.py) 修正多穿补货规则（补货只能补到空料箱中)

 



### DC_ASRS仿真使用
#### 1. 准备工作

a) 下载并解压 [DC_ASRS.v2.3](https://github.com/sylym/DC_ASRS/releases/download/DC_ASRS/DC_ASRS.v2.3.rar)

b) 根据样例文件 [example](example.py) 调用仿真 [simulation](simulation.py) API


```sh
first_day_sku_dic = {}  # {SKU编号：多穿内箱数}
MS_LIST = {}  # {SKU编号：[最小值，最大值]}

env = SimulationEnv()  # 构建仿真环境
env.reset(first_day_sku_dic)  # 重置仿真环境

while True:
    observation, reward, done, info = env.step(MS_LIST)  # 进行每日仿真
    if done:
        break
```

#### 2. 仿真API文档

SimulationEnv为仿真环境类，其中包含仿真环境的初始化、进行每日仿真等方法。

**a) env.reset()**
```sh
env.reset()
```
对仿真类进行初始化。

**b) env.step()**
```sh
obs, reward, done, info = env.step(MS_LIST)
```

**传入参数：**

- MS_LIST：每日的多穿列表, 数据类型为dict, 键值为SKU编号(int)，值为包含min值和max值的list。

```sh
MS_LIST = {82292589: [0, 48], 082292590: [2, 50], 82292591: [3, 18]}
```

**返回值：**

- obs：仿真环境的状态，数据类型为list。
    - obs[0]：多穿空货格数，数据类型为int。
    - obs[1]：不同SKU在多穿内箱数，数据类型为dict。键值为SKU编号(int)，值为多穿内箱数(float)。
    - obs[2]：不同SKU在立库散拣后剩余箱数，数据类型为dict。键值为SKU编号(int)，值为散拣后剩余箱数(float)。
    - obs[3]：仿真当天的所有订单，数据类型list，列表中每个元素每个订单行(list)，订单行列表样例：[SKU编号(int), 出货箱数(float), [一箱支数(int)，一板箱数(int)，多穿料箱可放箱数(int)]]。
    - obs[4]：不同SKU在多穿货格内的情况（只记录未装满该SKU的货格），数据类型为dict。键值为SKU编号(int)，值为该SKU在不同多穿货格内的箱数(list)。
    - obs[5]：仿真当天为第几天，数据类型为int。

```sh
obs = [7020, {82303465: 0, 82305681: 14.0}, {82303465: 12, 82305681: 0}, [[82303465, 12, [1, 108, 4]], [82305681, 10.0, [12, 24, 2]]], {82315635: [], 82305682: [2.0, 1]}, 1]
```

- reward：仿真的结果，数据类型为list。
    - reward[0]：累计多穿拣选的箱数，数据类型为float。
    - reward[1]：累计订单触发的补货数，数据类型为int。
    - reward[2]：累计出货箱数，数据类型为float。
    - reward[3]：累计时间成本，数据类型为float。
    - reward[4]：累计人员成本，数据类型为float。

```sh
reward = [123523.08333333374, 1447, 288941.83333333343, 31867.222222249267, 288941.8333333335]
```
- done：仿真是否结束，数据类型为bool。

- info：仿真状态，数据类型str
    - "restriction!!!": 不满足限制条件强制结束
    - "normal": 仿真正常运行/结束


### 3. 加速仿真

使用 [pypy解释器](https://www.pypy.org/) 代替python解释器

使用方法参考 [官方文档](https://doc.pypy.org/en/latest/)

## 鸣谢
我们的代码参考如下仓库:
* [OpenAI Gym](https://github.com/openai/gym)
