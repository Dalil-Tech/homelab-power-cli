# homelab-power

A tiny command-line tool that estimates what your always-on hardware costs to run. Give it the wattage and hours per day of each device plus your electricity rate, and it prints daily, monthly, and yearly kWh and cost.

I built it because I kept doing this math in my head when deciding whether to leave a box running 24/7. One Python file, standard library only, no install.

## Use it

```
python power_cost.py --device "NAS:60:24" --device "Mini PC:15:24" --device "Switch:8:24" --rate 0.18
```

```
Device    kWh/mo   kWh/yr   USD/mo   USD/yr
-------------------------------------------
NAS         43.8    526.0     7.89     94.67
Mini PC     11.0    131.5     1.97     23.67
Switch       5.8     70.1     1.05     12.62
-------------------------------------------
Total       60.6    727.6    10.91    130.96
```

Each device is `NAME:WATTS` or `NAME:WATTS:HOURS`. Hours per day defaults to 24. `--rate` is the all-in price you pay per kilowatt-hour, in whatever currency you want; set the label with `--currency`.

Quick single-device check:

```
python power_cost.py --watts 12 --hours 24 --rate 0.22 --currency GBP
```

## How it works

kWh per day is `watts * hours / 1000`. Monthly uses an average month of 30.4375 days so that monthly times twelve equals the yearly figure. Cost is kWh times your rate. That is the whole model. It does not try to handle idle-versus-load swings or tiered tariffs.

If you want those, I keep a web version with idle-vs-load profiles, device presets, and shareable result URLs here: **[Homelab Power & Electricity Cost Calculator](https://dalil-tech.com/power-calculator)**. More homelab tools and guides are at [dalil-tech.com](https://dalil-tech.com).

## Tests

```
python -m unittest -v
```

## License

MIT. Do what you want with it.
