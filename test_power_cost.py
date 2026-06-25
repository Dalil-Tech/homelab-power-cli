"""Tests for homelab-power. Stdlib unittest, no dependencies. Run: python -m unittest -v"""

import unittest

from power_cost import Device, cost_for, parse_device, total


class TestCost(unittest.TestCase):
    def test_kwh_per_day(self):
        # 100 W for 24 h = 2.4 kWh
        self.assertAlmostEqual(Device("x", 100).kwh_per_day(), 2.4)

    def test_partial_day(self):
        # 100 W for 12 h = 1.2 kWh
        self.assertAlmostEqual(Device("x", 100, 12).kwh_per_day(), 1.2)

    def test_cost_yearly(self):
        # 100 W, 24 h, 0.10/kWh -> 2.4 kWh/day -> 876.6 kWh/yr -> 87.66
        line = cost_for(Device("x", 100), rate=0.10)
        self.assertAlmostEqual(line.kwh_year, 876.6, places=1)
        self.assertAlmostEqual(line.cost_year, 87.66, places=2)

    def test_monthly_times_twelve_equals_yearly(self):
        line = cost_for(Device("x", 73), rate=0.18)
        self.assertAlmostEqual(line.cost_month * 12, line.cost_year, places=6)

    def test_total_sums_devices(self):
        lines = [cost_for(Device("a", 50), 0.2), cost_for(Device("b", 50), 0.2)]
        t = total(lines)
        self.assertAlmostEqual(t.kwh_day, 2.4)
        self.assertAlmostEqual(t.cost_year, lines[0].cost_year + lines[1].cost_year)

    def test_rejects_negative_watts(self):
        with self.assertRaises(ValueError):
            cost_for(Device("x", -5), 0.1)

    def test_rejects_hours_over_24(self):
        with self.assertRaises(ValueError):
            cost_for(Device("x", 5, 25), 0.1)


class TestParse(unittest.TestCase):
    def test_name_watts(self):
        d = parse_device("NAS:60")
        self.assertEqual(d.name, "NAS")
        self.assertEqual(d.watts, 60)
        self.assertEqual(d.hours_per_day, 24)

    def test_name_watts_hours(self):
        d = parse_device("Mini PC:15:8")
        self.assertEqual(d.name, "Mini PC")
        self.assertEqual(d.hours_per_day, 8)

    def test_bad_specs_raise(self):
        for bad in ["", "NAS", ":60", "NAS:abc", "NAS:60:8:9"]:
            with self.assertRaises(ValueError):
                parse_device(bad)


if __name__ == "__main__":
    unittest.main()
