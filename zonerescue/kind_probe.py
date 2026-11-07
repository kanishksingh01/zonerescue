"""Bounded zone-workload failure exercise using a disposable Kind context only.

This is a *workload replica loss* test, not a physical cloud zone outage.
No remote contexts are accepted and cleanup always attempts restoration.
"""
import argparse
import json
import subprocess
import time
from datetime import datetime, timezone
from urllib.error import URLError
from urllib.request import urlopen

CONTEXT = "kind-zonerescue"
NAMESPACE = "zonerescue-lab"

def kubectl(*args):
    cmd = ["kubectl", "--context", CONTEXT, "-n", NAMESPACE, *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if proc.returncode:
        raise RuntimeError(f"kubectl {args[0]} exit={proc.returncode}: {proc.stderr[-350:]}")
    return proc.stdout

def endpoint_zones():
    result = json.loads(kubectl("get", "pods", "-l", "app=zonerescue-demo",
                                "-o", "json"))
    return sorted((pod.get("metadata") or {}).get("labels", {}).get("zone")
                  for pod in result.get("items", [])
                  if (pod.get("status") or {}).get("phase") == "Running"
                  and any(c.get("type") == "Ready" and c.get("status") == "True"
                          for c in (pod.get("status") or {}).get("conditions", [])))

def wait_zones(expected, timeout=90):
    stop = time.monotonic() + timeout
    while time.monotonic() < stop:
        actual = endpoint_zones()
        if actual == sorted(expected):
            return actual
        time.sleep(2)
    raise AssertionError(f"expected ready zones {expected}, got {endpoint_zones()}")

def probe(url, samples=30):
    good = 0
    latencies = []
    for _ in range(samples):
        started = time.perf_counter()
        try:
            with urlopen(url, timeout=4) as response:
                good += int(response.status == 200)
        except (URLError, OSError, TimeoutError):
            pass
        latencies.append(round((time.perf_counter()-started)*1000, 3))
    return {"requests": samples, "successful": good,
            "failed": samples-good, "availability": round(good/samples, 4),
            "latency_ms_max": max(latencies)}

def run(url, samples=30):
    wait_zones(["zone-a", "zone-b", "zone-c"])
    baseline = probe(url, samples)
    if baseline["failed"]:
        raise AssertionError(f"unhealthy pre-fault baseline: {baseline}")
    start = time.perf_counter()
    try:
        kubectl("scale", "deployment/demo-b", "--replicas=0")
        wait_zones(["zone-a", "zone-c"])
        while_missing = probe(url, samples)
        if while_missing["failed"]:
            raise AssertionError(f"shared service unavailable despite two healthy zones: {while_missing}")
    finally:
        kubectl("scale", "deployment/demo-b", "--replicas=1")
    wait_zones(["zone-a", "zone-b", "zone-c"])
    restored = probe(url, samples)
    if restored["failed"]:
        raise AssertionError(f"service did not recover: {restored}")
    report = {
        "measured_at_utc": datetime.now(timezone.utc).isoformat(),
        "baseline": baseline,
        "zone_b_workload_missing": while_missing,
        "restored": restored,
        "time_to_restore_all_ready_replicas_seconds": round(time.perf_counter()-start, 3),
        "failure_class": "controlled zone-b workload replica loss; not actual zone outage",
        "zone_labels": ["zone-a", "zone-b", "zone-c"],
        "cleanup_verified": True,
    }
    return report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:18080")
    parser.add_argument("--samples", type=int, default=30)
    parser.add_argument("--output", default="kind-zone-report.json")
    args = parser.parse_args()
    if not 1 <= args.samples <= 500:
        parser.error("samples must be between 1 and 500")
    result = run(args.url, args.samples)
    print(json.dumps(result, indent=2))
    with open(args.output, "w", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)

if __name__ == "__main__":
    main()
