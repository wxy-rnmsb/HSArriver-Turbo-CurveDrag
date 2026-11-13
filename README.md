# HSArriver-Turbo-CurveDrag

本仓库是 [Donald-Yip/HSArriver-Turbo](https://github.com/Donald-Yip/HSArriver-Turbo)
的 fork，只记录本 fork 的功能修改。

安装、使用、配置和原项目介绍请直接查看上游 README：

<https://github.com/Donald-Yip/HSArriver-Turbo>

## 功能更新

### 2026-11-13：点击坐标与固定行为随机化

- 所有炉石客户端点击坐标统一加入分布随机化；
- 横坐标不向左偏移，范围为原坐标到原坐标右侧 10 像素；
- 横坐标使用 Beta 分布，期望中心约为原坐标右侧 3 像素；
- 纵坐标使用三角分布，中心为原坐标，范围为上下各 15 像素；
- 右键、窗口激活点和战网点击也加入同类随机化；
- 卡牌拖拽的起点、战场落点和牌库落点加入同类随机化；
- 鼠标相关固定延时加入 ±8% 的小幅随机波动；
- 自动认输、换牌确认、结算等待等固定等待也加入小幅随机化。

### 2026-11-13：运行时间递增

- 每次自动化启动时重新开始计时；
- 30 分钟内速度和路径随机性平滑增长到原来的 2 倍；
- 使用 `smoothstep` 缓动，避免突然变快；
- 最大速度下移动时间约为起始时长的一半；
- 弧线幅度、摆动幅度和时长抖动同步增加。

### 2026-11-12：鼠标曲线移动

- 鼠标从瞬间跳转改为类椭圆曲线移动；
- 加入随机小幅摆动；
- 使用先加速后减速的缓动；
- 起始移动时间为 0.2～0.5 秒；
- 默认待命点改为右下角随机区域；
- 点击、悬停、复位和拖拽统一通过曲线移动函数执行。

## 修改文件

```text
click.py
manual_controller.py
FSM_action.py
tests/test_mouse_motion_curve.py
tests/test_mouse_reset_position.py
tests/test_human_like.py
tests/test_human_like_minion_hover.py
```

## 测试

鼠标轨迹、复位、点击安全、手动控制、推荐流程、换牌、进入对战和重启等相关测试均已更新并通过。

详细变更见 [FORK_CHANGES.md](FORK_CHANGES.md)。
