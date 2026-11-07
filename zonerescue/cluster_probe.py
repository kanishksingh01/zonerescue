"""Real in-cluster Kubernetes Service routing test, restricted to disposable Kind.

Only synthetic workload-scale actions; no physical zone or node shutdown.
"""
import json
import subprocess
import time
from datetime import datetime, timezone

CONTEXT = "kind-zonerescue"
NAMESPACE = "zonerescue-lab"
PREFIX = ["kubectl", "--context", CONTEXT, "-n", NAMESPACE]

def kubectl(*args, timeout=15):
    proc = subprocess.run(PREFIX + list(args), capture_output=True,
                          text=True, timeout=timeout)
    if proc.returncode:
        raise RuntimeError(f"kubectl {args[0]} failed: {proc.stderr[-300:]}")
    return proc.stdout

def count_endpoints(service):
    doc = json.loads(kubectl("get", "endpointslices.discovery.k8s.io",
                            "-l", f"kubernetes.io/service-name={service}", "-o", "json"))
    return sum(1 for item in doc.get("items", [])
               for endpoint in item.get("endpoints", [])
               if endpoint.get("conditions", {}).get("ready", True))

def await_endpoints(service, count, seconds=90):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if count_endpoints(service) == count:
            return
        time.sleep(1)
    raise AssertionError(f"{service}: expected {count} ready endpoints, got {count_endpoints(service)}")

def probe(service, samples=12):
    ok = 0
    for _ in range(samples):
        url = f"http://{service}.zonerescue-lab.svc.cluster.local/"
        proc = subprocess.run(
            PREFIX + ["exec", "zone-probe", "--", "wget", "-q", "-T", "2",
                      "-O", "/dev/null", url],
            capture_output=True, timeout=8)
        ok += proc.returncode == 0
    return {"requests": samples, "successful": ok, "failed": samples-ok,
            "availability": round(ok/samples, 4)}

def run():
    await_endpoints("demo", 3)
    await_endpoints("demo-b-only", 1)
    baseline = {"balanced": probe("demo"), "concentrated": probe("demo-b-only")}
    if any(v["failed"] for v in baseline.values()):
        raise AssertionError(f"healthy service baseline failed: {baseline}")
    started = time.monotonic()
    try:
        kubectl("scale", "deployment/demo-b", "--replicas=0")
        await_endpoints("demo", 2)
        await_endpoints("demo-b-only", 0)
        failure = {"balanced": probe("demo"), "concentrated": probe("demo-b-only")}
        if failure["balanced"]["failed"] != 0:
            raise AssertionError("balanced Service lost requests with two healthy replicas")
        if failure["concentrated"]["successful"] != 0:
            raise AssertionError("zone-B-only Service unexpectedly succeeded with no endpoints")
    finally:
        kubectl("scale", "deployment/demo-b", "--replicas=1")
    await_endpoints("demo", 3)
    await_endpoints("demo-b-only", 1)
    recovered = {"balanced": probe("demo"), "concentrated": probe("demo-b-only")}
    if any(v["failed"] for v in recovered.values()):
        raise AssertionError(f"Services were not restored: {recovered}")
    return {"measured_at_utc": datetime.now(timezone.utc).isoformat(),
            "baseline": baseline, "during_zone_b_workload_loss": failure,
            "after_restore": recovered,
            "time_to_restore_endpoints_and_verify_seconds": round(time.monotonic()-started, 3),
            "probe_path": "in-cluster Pod -> CoreDNS -> ClusterIP Service -> EndpointSlice -> Pod",
            "failure_class": "zone-b Deployment scaled to zero in isolated Kind, not node outage",
            "cleanup_verified": True}

def main():
    report = run()
    print(json.dumps(report, indent=2))
    with open("kind-routing-report.json", "w", encoding="utf-8") as output:
        json.dump(report, output, indent=2)

if __name__ == "__main__":
    main()
