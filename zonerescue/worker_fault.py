"""Simulate one *real Kind worker-node* outage by pausing the node container.

Scope is hardcoded to temporary CI cluster kind-zonerescue only. The worker
container is always unpaused in finally; no GKE/cloud APIs are used.
"""
import json
import subprocess
import time
from datetime import datetime, timezone
from zonerescue.cluster_probe import (CONTEXT, NAMESPACE, kubectl,
                                       count_endpoints, await_endpoints, probe)

WORKER = "zonerescue-worker2"

def run_command(*cmd, check=True, timeout=15):
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          timeout=timeout, check=False)
    if check and proc.returncode:
        raise RuntimeError(f"{cmd[0]} command failed: {proc.stderr[-300:]}")
    return proc

def node_ready():
    doc = json.loads(run_command(
        "kubectl", "--context", CONTEXT, "get", "node", WORKER,
        "-o", "json", "--request-timeout=5s").stdout)
    for c in (doc.get("status") or {}).get("conditions") or []:
        if c.get("type") == "Ready":
            return c.get("status")
    return "Unknown"

def wait_not_ready(timeout=160):
    end = time.monotonic()+timeout
    while time.monotonic()<end:
        if node_ready() != "True":
            return
        time.sleep(3)
    raise AssertionError("Kind worker never became NotReady or Unknown")

def wait_ready(timeout=160):
    end = time.monotonic()+timeout
    while time.monotonic()<end:
        if node_ready() == "True":
            return
        time.sleep(3)
    raise AssertionError("Kind worker did not recover Ready=True")

def main():
    current = run_command("kubectl", "config", "current-context").stdout.strip()
    if current != CONTEXT:
        raise RuntimeError("refusing node interruption outside disposable Kind context")
    if run_command("docker", "inspect", "--format={{.Name}}", WORKER).stdout.strip() != "/" + WORKER:
        raise RuntimeError("unexpected Docker worker container name")
    await_endpoints("demo", 3)
    await_endpoints("demo-b-only", 1)
    baseline = {"balanced": probe("demo", 8), "concentrated": probe("demo-b-only", 8)}
    if baseline["balanced"]["failed"] or baseline["concentrated"]["failed"]:
        raise AssertionError(f"unhealthy pre-fault baseline: {baseline}")
    started = time.monotonic()
    node_went_not_ready = False
    checkpoints = {}
    affected = None
    restored = None
    try:
        run_command("docker", "pause", WORKER)
        wait_not_ready(timeout=155)
        node_went_not_ready = True
        checkpoints["node_unavailable_detected_seconds"] = round(time.monotonic()-started, 3)
        await_endpoints("demo", 2, seconds=125)
        await_endpoints("demo-b-only", 0, seconds=125)
        checkpoints["service_endpoints_reconciled_seconds"] = round(time.monotonic()-started, 3)
        affected = {"balanced": probe("demo", 12), "concentrated": probe("demo-b-only", 12)}
        if affected["balanced"]["failed"]:
            raise AssertionError(f"balanced service unavailable after zone-b node failure: {affected}")
        if affected["concentrated"]["successful"]:
            raise AssertionError("zone-B-only service unexpectedly served requests")
    finally:
        run_command("docker", "unpause", WORKER, check=False)
        checkpoints["worker_unpaused_seconds"] = round(time.monotonic()-started, 3)
        wait_ready(timeout=170)
        checkpoints["node_ready_again_seconds"] = round(time.monotonic()-started, 3)
        await_endpoints("demo", 3, seconds=120)
        await_endpoints("demo-b-only", 1, seconds=120)
        checkpoints["service_endpoints_restored_seconds"] = round(time.monotonic()-started, 3)
        restored = {"balanced": probe("demo", 8), "concentrated": probe("demo-b-only", 8)}
    if any(v["failed"] for v in restored.values()):
        raise AssertionError(f"service did not restore: {restored}")
    checkpoints["full_restoration_verified_seconds"] = round(time.monotonic()-started, 3)
    report = {
        "at_utc": datetime.now(timezone.utc).isoformat(),
        "failure": "Docker pause of one Kind Kubernetes worker (zone-b)",
        "baseline": baseline,
        "kubernetes_node_not_ready_confirmed": node_went_not_ready,
        "during_worker_unavailable_after_endpoint_reconciliation": affected,
        "after_worker_recovery": restored,
        "time_to_worker_recovery_and_probe_seconds": round(time.monotonic()-started, 3),
        "cleanup_verified": True,
        "timing_checkpoints_from_pause_seconds": checkpoints,
        "service_endpoint_reconciliation_lag_seconds": round(
            checkpoints["service_endpoints_reconciled_seconds"] -
            checkpoints["node_unavailable_detected_seconds"], 3),
        "service_endpoint_restoration_lag_seconds": round(
            checkpoints["service_endpoints_restored_seconds"] -
            checkpoints["worker_unpaused_seconds"], 3),
        "scope": "ephemeral Kind node only; not a physical GKE zone outage"
    }
    print(json.dumps(report, indent=2))
    with open("worker-outage-report.json", "w", encoding="utf-8") as output:
        json.dump(report, output, indent=2)

if __name__ == "__main__":
    main()
