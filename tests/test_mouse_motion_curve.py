"""新增曲线移动的回归测试：时长、缓动、弧线和右下角复位区域。"""

import unittest
from unittest.mock import patch

import click as hearthstone_click


class MovingMouse:
    def __init__(self, start=(0, 0)):
        self._position = start
        self.points = []

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value
        self.points.append(value)


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def perf_counter(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class MouseMotionCurveTests(unittest.TestCase):
    def test_ease_in_out_accelerates_then_decelerates(self):
        self.assertAlmostEqual(0.0, hearthstone_click._ease_in_out(0.0))
        self.assertAlmostEqual(0.5, hearthstone_click._ease_in_out(0.5))
        self.assertAlmostEqual(1.0, hearthstone_click._ease_in_out(1.0))
        self.assertLess(hearthstone_click._ease_in_out(0.25), 0.25)
        self.assertGreater(hearthstone_click._ease_in_out(0.75), 0.75)

    def test_duration_follows_distance_and_stays_in_range(self):
        with patch.object(hearthstone_click.random, "uniform", return_value=1.0):
            near = hearthstone_click._move_duration(0)
            middle = hearthstone_click._move_duration(600)
            far = hearthstone_click._move_duration(1200)

        self.assertAlmostEqual(0.20, near)
        self.assertGreater(middle, near)
        self.assertLess(middle, far)
        self.assertAlmostEqual(0.50, far)

    def test_move_uses_a_curved_path_and_lands_exactly(self):
        mouse = MovingMouse((0, 0))
        clock = FakeClock()
        target = (100, 0)

        with (
            patch.object(hearthstone_click.time, "perf_counter",
                         side_effect=clock.perf_counter),
            patch.object(hearthstone_click.time, "sleep",
                         side_effect=clock.sleep),
            patch.object(hearthstone_click.random, "uniform",
                         side_effect=[0.10, 1.0, 2.0, 0.0]),
            patch.object(hearthstone_click.random, "choice",
                         return_value=1.0),
        ):
            hearthstone_click._move_mouse_to(
                mouse, target, duration=0.20)

        self.assertGreater(len(mouse.points), 10)
        self.assertEqual(target, mouse.points[-1])
        self.assertEqual((0, 0), mouse.points[0])
        self.assertTrue(any(y > 2 for _, y in mouse.points), mouse.points)
        self.assertGreaterEqual(clock.now, 0.20)

    def test_reset_point_stays_inside_bottom_right_region(self):
        x1, y1, x2, y2 = hearthstone_click.MOUSE_RESET_REGION
        points = {hearthstone_click._random_reset_point() for _ in range(200)}

        self.assertGreater(len(points), 1)
        for x, y in points:
            self.assertTrue(x1 <= x <= x2)
            self.assertTrue(y1 <= y <= y2)


if __name__ == "__main__":
    unittest.main()
