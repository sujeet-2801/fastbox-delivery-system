# FastBox Delivery System

Simulates one day of FastBox deliveries from a JSON file and writes `report.json`.

## Run

From this folder:

```bash
python delivery_system.py
```

That reads `data.json` and saves `report.json`.

Use another input file:

```bash
python delivery_system.py test_cases/test_case_1.json -o test_cases/report_test_1.json
```

## What it does

1. Reads and parses the JSON input.
2. Assigns each package to the nearest agent, using Euclidean distance from the agent to the package warehouse.
3. Simulates each delivery: the agent goes to the warehouse, then to the destination, and the distance is added to that agent's total.
4. Writes a report with `packages_delivered`, `total_distance`, `efficiency`, and `best_agent`.

Efficiency is total distance divided by packages delivered. The best agent has the lowest efficiency.

Python 3.9 or newer is required. No extra packages are needed.
