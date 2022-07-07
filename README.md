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

a) **env.reset()**
```sh
env.reset()
```
对仿真类进行初始化。

b) **env.step()**
```sh
obs, reward, done, info = env.step(MS_LIST)
```

参数：

MS_LIST：每日的多穿列表, 数据类型为字典, 键值为SKU编号(int)，值为包含min值和max值的列表。

```sh
MS_LIST = {82292589: [0, 48], 082292590: [2, 50], 82292591: [3, 18]}
```


### 3. 加速仿真


## 鸣谢
我们的代码基于如下仓库:
* [OpenAI Gym](https://github.com/openai/gym)
