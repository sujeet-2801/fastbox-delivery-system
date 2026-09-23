import argparse
import json
import math
from pathlib import Path
from typing import Any


Point = list[float]


def load_data(path: Path) -> dict[str, Any]:
    """Read and parse the delivery JSON file."""
    with path.open(encoding="utf-8-sig") as file:
        return json.load(file)


def normalize_locations(locations: dict[str, Any]) -> dict[str, Point]:
    """Accept either {"W1": [x, y]} or [{"id": "W1", "location": [x, y]}]."""
    if isinstance(locations, list):
        locations = {location["id"]: location["location"] for location in locations}
    return {identifier: [float(point[0]), float(point[1])] for identifier, point in locations.items()}


def normalize_packages(packages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Accept warehouse or warehouse_id, and keep destinations as [x, y]."""
    normalized = []
    for package in packages:
        warehouse_id = package.get("warehouse", package.get("warehouse_id"))
        if warehouse_id is None:
            raise ValueError(f"Package {package.get('id', '<unknown>')} has no warehouse")
        normalized.append(
            {
                "id": package["id"],
                "warehouse": warehouse_id,
                "destination": [float(package["destination"][0]), float(package["destination"][1])],
            }
        )
    return normalized


def distance(first: Point, second: Point) -> float:
    """Straight-line Euclidean distance between two points."""
    return math.hypot(first[0] - second[0], first[1] - second[1])


def assign_packages(
    warehouses: dict[str, Point], agents: dict[str, Point], packages: list[dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    """Assign each package to the agent closest to its warehouse."""
    deliveries = {agent_id: [] for agent_id in agents}
    for package in packages:
        warehouse_location = warehouses[package["warehouse"]]
        assigned_agent = min(
            agents,
            key=lambda agent_id: distance(agents[agent_id], warehouse_location),
        )
        deliveries[assigned_agent].append(package)
    return deliveries


def simulate_routes(
    agents: dict[str, Point], warehouses: dict[str, Point], assignments: dict[str, list[dict[str, Any]]]
) -> dict[str, dict[str, Any]]:
    """Move each agent warehouse-to-destination and total the distance."""
    report = {}
    for agent_id, packages in assignments.items():
        current_location = agents[agent_id]
        total_distance = 0.0

        for package in packages:
            warehouse_location = warehouses[package["warehouse"]]
            destination = package["destination"]
            # Pick up at the warehouse, then finish this delivery at the destination.
            total_distance += distance(current_location, warehouse_location)
            total_distance += distance(warehouse_location, destination)
            current_location = destination

        package_count = len(packages)
        report[agent_id] = {
            "packages_delivered": package_count,
            "total_distance": round(total_distance, 2),
            # Distance per package. Agents with no deliveries have no efficiency.
            "efficiency": round(total_distance / package_count, 2) if package_count else None,
        }
    return report


def create_report(data: dict[str, Any]) -> dict[str, Any]:
    """Build the assignment report, including best_agent."""
    warehouses = normalize_locations(data["warehouses"])
    agents = normalize_locations(data["agents"])
    packages = normalize_packages(data["packages"])
    assignments = assign_packages(warehouses, agents, packages)
    report: dict[str, Any] = simulate_routes(agents, warehouses, assignments)

    delivering_agents = [
        agent_id for agent_id, stats in report.items() if stats["packages_delivered"]
    ]
    # The best agent travels the least distance per delivered package.
    report["best_agent"] = (
        min(delivering_agents, key=lambda agent_id: report[agent_id]["efficiency"])
        if delivering_agents
        else None
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate FastBox deliveries from a JSON input file.")
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=Path("data.json"),
        help="Path to the delivery input JSON file (default: data.json)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("report.json"),
        help="Path for the JSON report (default: report.json)",
    )
    arguments = parser.parse_args()

    report = create_report(load_data(arguments.input))
    rendered_report = json.dumps(report, indent=2) + "\n"
    arguments.output.write_text(rendered_report, encoding="utf-8")
    print(rendered_report, end="")


if __name__ == "__main__":
    main()
