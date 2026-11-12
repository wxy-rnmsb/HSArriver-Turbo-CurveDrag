# HSArriver-Turbo-CurveDrag 改动说明

本 fork 基于：

- 上游仓库：<https://github.com/Donald-Yip/HSArriver-Turbo>
- Fork 日期：2026-11-12

## 1. 鼠标曲线移动

原实现中，鼠标通过 `mouse.position = (x, y)` 直接从当前点跳到目标点。
本 fork 新增统一的 `_move_mouse_to()`，轨迹由以下部分组成：

1. 起点到终点的直线插值；
2. 垂直于移动方向的椭圆弧偏移；
3. 在起点和终点归零的随机小幅摆动。

弧线方向、弯曲幅度、摆动幅度、摆动次数和相位均带随机性。

## 2. 先加速后减速

使用 `smoothstep` 缓动：

```text
u = t² × (3 - 2t)
```

两端速度为 0，中段速度最大，实现先加速、后减速。

## 3. 移动时间

移动时间根据起点到终点的距离计算，并限制在：

```text
0.20 秒 ～ 0.50 秒
```

距离越长，移动时间越接近 0.5 秒；同时保留小幅随机波动。

## 4. 右下角随机待命位置

原默认待命点为左上角 `(70, 60)`。本 fork 改为客户区相对坐标区域：

```python
MOUSE_RESET_REGION = (1760, 950, 1875, 1045)
```

每次复位在该区域内随机选择一点。

## 5. 统一移动出口

以下操作全部改为调用 `_move_mouse_to()`：

- 普通左键和右键点击；
- 鼠标复位；
- 手牌区随机悬停；
- 对手新随从悬停；
- 随从拖到战场；
- 卡牌拖到牌库。

移动结束后仍会精确设置到目标坐标，保证点击位置不偏移。

## 6. 测试

新增：

```text
tests/test_mouse_motion_curve.py
```

更新：

```text
tests/test_mouse_reset_position.py
tests/test_human_like.py
tests/test_human_like_minion_hover.py
```

验证内容：

- 缓动两端速度为 0；
- 移动时间在 0.2～0.5 秒；
- 轨迹存在弯曲和摆动；
- 最终位置精确等于目标点；
- 随机待命点始终落在右下角区域内；
- 原有点击、悬停、拖拽和推荐流程测试不需要改变行为。

## 7. 时序影响

新增移动时间会叠加到原有操作间隔之上。现有操作均为同步调用，
因此不会出现“移动尚未完成就执行下一步点击”的竞态；但整体动作节奏会比上游稍慢。
如果希望更快或更慢，可调整：

```python
MOUSE_MOVE_MIN_SECONDS
MOUSE_MOVE_MAX_SECONDS
MOUSE_MOVE_REFERENCE_DISTANCE
```
