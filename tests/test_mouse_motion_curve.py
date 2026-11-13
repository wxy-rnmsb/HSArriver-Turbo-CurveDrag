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

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class MouseMotionCurveTests(unittest.TestCase):
    def setUp(self):
        self._saved_start = hearthstone_click.MOUSE_RUN_STARTED_AT

    def tearDown(self):
        hearthstone_click.MOUSE_RUN_STARTED_AT = self._saved_start

    def test_ease_in_out_accelerates_then_decelerates(self):
        self.assertAlmostEqual(0.0, hearthstone_click._ease_in_out(0.0))
        self.assertAlmostEqual(0.5, hearthstone_click._ease_in_out(0.5))
        self.assertAlmostEqual(1.0, hearthstone_click._ease_in_out(1.0))
        self.assertLess(hearthstone_click._ease_in_out(0.25), 0.25)
        self.assertGreater(hearthstone_click._ease_in_out(0.75), 0.75)

    def test_duration_follows_distance_and_stays_in_range(self):
        clock = FakeClock()
        with (
            patch.object(hearthstone_click.time, "monotonic",
                         side_effect=clock.monotonic),
            patch.object(hearthstone_click.random, "uniform", return_value=1.0),
        ):
            hearthstone_click.reset_mouse_runtime()
            near = hearthstone_click._move_duration(0)
            middle = hearthstone_click._move_duration(600)
            far = hearthstone_click._move_duration(1200)

        self.assertAlmostEqual(0.20, near)
        self.assertGreater(middle, near)
        self.assertLess(middle, far)
        self.assertAlmostEqual(0.50, far)

    def test_runtime_speed_and_randomness_reach_two_times(self):
        clock = FakeClock()
        with patch.object(hearthstone_click.time, "monotonic",
                          side_effect=clock.monotonic):
            hearthstone_click.reset_mouse_runtime()
            self.assertAlmostEqual(
                1.0, hearthstone_click._runtime_speed_multiplier())
            self.assertAlmostEqual(
                1.0, hearthstone_click._runtime_randomness_multiplier())

            clock.now = hearthstone_click.MOUSE_RAMP_SECONDS / 2
            self.assertAlmostEqual(
                1.5, hearthstone_click._runtime_speed_multiplier())

            clock.now = hearthstone_click.MOUSE_RAMP_SECONDS
            self.assertAlmostEqual(
                2.0, hearthstone_click._runtime_speed_multiplier())
            self.assertAlmostEqual(
                2.0, hearthstone_click._runtime_randomness_multiplier())

    def test_duration_approaches_half_after_runtime_ramp(self):
        clock = FakeClock()
        with (
            patch.object(hearthstone_click.time, "monotonic",
                         side_effect=clock.monotonic),
            patch.object(hearthstone_click.random, "uniform", return_value=1.0),
        ):
            hearthstone_click.reset_mouse_runtime()
            start = hearthstone_click._move_duration(1200)
            clock.now = hearthstone_click.MOUSE_RAMP_SECONDS
            end = hearthstone_click._move_duration(1200)

        self.assertAlmostEqual(0.50, start)
        self.assertAlmostEqual(0.25, end)

    def test_move_uses_a_curved_path_and_lands_exactly(self):
        mouse = MovingMouse((0, 0))
        clock = FakeClock()
        target = (100, 0)

        with (
            patch.object(hearthstone_click.time, "perf_counter",
                         side_effect=clock.perf_counter),
            patch.object(hearthstone_click.time, "monotonic",
                         side_effect=clock.monotonic),
            patch.object(hearthstone_click.time, "sleep",
                         side_effect=clock.sleep),
            patch.object(hearthstone_click.random, "uniform",
                         side_effect=[0.10, 1.0, 2.0, 0.0]),
            patch.object(hearthstone_click.random, "choice",
                         return_value=1.0),
        ):
            hearthstone_click.reset_mouse_runtime()
            hearthstone_click._move_mouse_to(
                mouse, target, duration=0.20)

        self.assertGreater(len(mouse.points), 10)
        self.assertEqual(target, mouse.points[-1])
        self.assertEqual((0, 0), mouse.points[0])
        self.assertTrue(any(y > 2 for _, y in mouse.points), mouse.points)
        self.assertGreaterEqual(clock.now, 0.20)

    def test_click_jitter_never_moves_left_and_stays_in_bounds(self):
        xs = []
        ys = []
        for _ in range(2000):
            x, y = hearthstone_click._jitter_click_point(500, 400)
            xs.append(x - 500)
            ys.append(y - 400)

        self.assertTrue(all(0 <= value <= 10 for value in xs), (min(xs), max(xs)))
        self.assertTrue(all(-15 <= value <= 15 for value in ys), (min(ys), max(ys)))
        self.assertGreater(sum(xs) / len(xs), 2.5)
        self.assertLess(sum(xs) / len(xs), 3.5)
        self.assertGreater(sum(ys) / len(ys), -1.0)
        self.assertLess(sum(ys) / len(ys), 1.0)

    def test_jitter_delay_uses_eight_percent_bounds(self):
        with patch.object(hearthstone_click.random, "uniform",
                          return_value=0.92):
            self.assertAlmostEqual(
                0.092, hearthstone_click.jitter_delay(0.1), places=6)
        with patch.object(hearthstone_click.random, "uniform",
                          return_value=1.08):
            self.assertAlmostEqual(
                0.108, hearthstone_click.jitter_delay(0.1), places=6)

    def test_reset_point_stays_inside_bottom_right_region(self):
        x1, y1, x2, y2 = hearthstone_click.MOUSE_RESET_REGION
        points = {hearthstone_click._random_reset_point() for _ in range(200)}

        self.assertGreater(len(points), 1)
        for x, y in points:
            self.assertTrue(x1 <= x <= x2)
            self.assertTrue(y1 <= y <= y2)


if __name__ == "__main__":
    unittest.main()
