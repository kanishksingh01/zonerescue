"""Synthetic zonal-outage experiment; no infrastructure actions."""
import argparse
import json
import sys
from zonerescue.simulator import Scenario, simulate, topology, ZONES

def main():
    parser = argparse.ArgumentParser(description="Run synthetic zonal failure experiment")
    parser.add_argument("--topology", choices=("balanced", "concentrated"), default="balanced")
    parser.add_argument("--failed-zone", choices=ZONES, default="zone-b")
    parser.add_argument("--requests", type=int, default=300)
    parser.add_argument("--detection-requests", type=int, default=15)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        report = simulate(Scenario(topology(args.topology), args.failed_zone,
                                   args.detection_requests, args.requests, args.seed))
    except ValueError as exc:
        parser.error(str(exc))
    rendered = json.dumps(report, indent=2)
    print(rendered)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as file:
            file.write(rendered)
    return 0

if __name__ == "__main__":
    sys.exit(main())
