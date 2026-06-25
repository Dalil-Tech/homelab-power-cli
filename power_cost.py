#!/usr/bin/env python3
"""homelab-power: estimate the electricity cost of always-on hardware.

Give it the wattage and hours per day of each device plus your electricity
rate, and it prints daily, monthly, and yearly energy use and cost. Built for
homelab and home-server gear that runs around the clock.

For an interactive version with idle-vs-load profiles, per-device presets, and
shareable result URLs, use the web calculator:
https://dalil-tech.com/power-calculator
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass

DAYS_PER_YEAR = 365.25
DAYS_PER_MONTH = DAYS_PER_YEAR / 12  # average month, so monthly x 12 equals yearly


@dataclass(frozen=True)
class Device:
    name: str
    watts: float
    hours_per_day: float = 24.0

    def kwh_per_day(self) -> float:
        return self.watts * self.hours_per_day / 1000.0


@dataclass(frozen=True)
class CostLine:
    name: str
    kwh_day: float
    kwh_month: float
    kwh_year: float
    cost_day: float
    cost_month: float
    cost_year: float


def cost_for(device: Device, rate: float) -> CostLine:
    """Energy and cost for one device at a given price per kWh.

    rate is the all-in price you pay per kilowatt-hour, in your own currency.
    """
    if device.watts < 0:
        raise ValueError(f"{device.name}: watts cannot be negative")
    if not 0 <= device.hours_per_day <= 24:
        raise ValueError(f"{device.name}: hours per day must be between 0 and 24")
    if rate < 0:
        raise ValueError("rate cannot be negative")

    day = device.kwh_per_day()
    month = day * DAYS_PER_MONTH
    year = day * DAYS_PER_YEAR
    return CostLine(
        name=device.name,
        kwh_day=day,
        kwh_month=month,
        kwh_year=year,
        cost_day=day * rate,
        cost_month=month * rate,
        cost_year=year * rate,
    )


def total(lines: list[CostLine]) -> CostLine:
    return CostLine(
        name="Total",
        kwh_day=sum(l.kwh_day for l in lines),
        kwh_month=sum(l.kwh_month for l in lines),
        kwh_year=sum(l.kwh_year for l in lines),
        cost_day=sum(l.cost_day for l in lines),
        cost_month=sum(l.cost_month for l in lines),
        cost_year=sum(l.cost_year for l in lines),
    )


def parse_device(spec: str) -> Device:
    """Parse a NAME:WATTS[:HOURS] string. Hours defaults to 24."""
    parts = spec.split(":")
    if len(parts) not in (2, 3):
        raise ValueError(
            f"bad device '{spec}'. Use NAME:WATTS or NAME:WATTS:HOURS, "
            "for example NAS:60:24"
        )
    name = parts[0].strip()
    if not name:
        raise ValueError(f"bad device '{spec}': name is empty")
    try:
        watts = float(parts[1])
        hours = float(parts[2]) if len(parts) == 3 else 24.0
    except ValueError:
        raise ValueError(f"bad device '{spec}': watts and hours must be numbers")
    return Device(name=name, watts=watts, hours_per_day=hours)


def format_report(lines: list[CostLine], rate: float, currency: str) -> str:
    tot = total(lines)
    width = max(len(l.name) for l in lines + [tot])
    header = f"{'Device'.ljust(width)}   kWh/mo   kWh/yr   {currency}/mo   {currency}/yr"
    rows = [header, "-" * len(header)]
    for l in lines:
        rows.append(
            f"{l.name.ljust(width)}   {l.kwh_month:6.1f}   {l.kwh_year:6.1f}   "
            f"{l.cost_month:6.2f}   {l.cost_year:7.2f}"
        )
    if len(lines) > 1:
        rows.append("-" * len(header))
        rows.append(
            f"{tot.name.ljust(width)}   {tot.kwh_month:6.1f}   {tot.kwh_year:6.1f}   "
            f"{tot.cost_month:6.2f}   {tot.cost_year:7.2f}"
        )
    rows.append("")
    rows.append(f"Rate: {rate} {currency}/kWh")
    rows.append("Interactive version: https://dalil-tech.com/power-calculator")
    return "\n".join(rows)


def build_devices(args: argparse.Namespace) -> list[Device]:
    if args.device:
        return [parse_device(s) for s in args.device]
    if args.watts is not None:
        return [Device(name="Device", watts=args.watts, hours_per_day=args.hours)]
    raise ValueError("give at least one --device, or --watts")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="homelab-power",
        description="Estimate the electricity cost of always-on homelab hardware.",
        epilog="Web version: https://dalil-tech.com/power-calculator",
    )
    parser.add_argument(
        "--device",
        action="append",
        metavar="NAME:WATTS[:HOURS]",
        help="a device, repeatable. Hours per day defaults to 24. Example: NAS:60:24",
    )
    parser.add_argument("--watts", type=float, help="quick mode: a single device wattage")
    parser.add_argument(
        "--hours", type=float, default=24.0, help="hours per day for --watts mode (default 24)"
    )
    parser.add_argument(
        "--rate", type=float, required=True, help="electricity price per kWh in your currency"
    )
    parser.add_argument(
        "--currency", default="USD", help="currency label for the report (default USD)"
    )
    args = parser.parse_args(argv)

    try:
        devices = build_devices(args)
        lines = [cost_for(d, args.rate) for d in devices]
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2

    print(format_report(lines, args.rate, args.currency))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
