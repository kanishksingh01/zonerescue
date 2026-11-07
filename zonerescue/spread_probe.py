"""Verify actual Kubernetes scheduling honors topology spread constraints in Kind."""
import json
import time
from datetime import datetime, timezone
from zonerescue.cluster_probe import kubectl, await_endpoints, probe

WORKERS = {
    "zonerescue-worker": "zone-a",
    "zonerescue-worker2": "zone-b",
    "zonerescue-worker3": "zone-c",
}

def placement_from_pods(document):
    counts = {"zone-a": 0, "zone-b": 0, "zone-c": 0}
    for pod in document.get("items", []):
        if pod.get("metadata", {}).get("deletionTimestamp"):
            continue
        node = pod.get("spec", {}).get("nodeName")
        if node not in WORKERS:
            raise AssertionError(f"unexpected node placement: {node}")
        conditions = pod.get("status", {}).get("conditions") or []
        if not any(c.get("type") == "Ready" and c.get("status") == "True"
                   for c in conditions):
            continue
        counts[WORKERS[node]] += 1
    return counts

def verify_spread(timeout=180):
    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        document = json.loads(kubectl("get", "pods", "-l", "app=zonerescue-spread",
                                      "-o", "json"))
        last = placement_from_pods(document)
        if last == {"zone-a": 2, "zone-b": 2, "zone-c": 2}:
            break
        time.sleep(2)
    else:
        raise AssertionError(f"topology spread did not reach 2 replicas per zone: {last}")
    await_endpoints("demo-spread", 6)
    test = probe("demo-spread", samples=20)
    if test["failed"]:
        raise AssertionError(f"spread Service did not serve requests: {test}")
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "replica_placement": last,
        "topology_spread_max_skew": 1,
        "service_probe": test,
        "scheduler_measured": True,
        "scope": "emulated Kind zone labels; not a physical multi-zone GKE cluster"
    }

def main():
    report = verify_spread()
    print(json.dumps(report, indent=2))
    with open("spread-placement-report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    main()
