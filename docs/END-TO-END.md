# ZoneRescue — End-to-end walkthrough

> **Status:** Deterministic simulation plus a real disposable Kind worker-outage demonstration. No cloud/GKE zonal fault injection. Independent, Google Cloud-aligned portfolio project; not affiliated with Google.

## 1. The problem

Multiple replicas do not guarantee zone resilience if they all live in one failure domain. And even a well-spread application may temporarily route traffic to failed endpoints until health detection catches up.

**What we built:** A deterministic placement model, an actual Kubernetes three-worker placement lab, and a controlled Kind worker-outage test with real ClusterIP Service routing.

## 2. How the current simulation works

```text
Topology: 3 synthetic zones (A, B, C)
       |
       +--- balanced:     A=2, B=2, C=2
       |
       +--- concentrated: A=0, B=6, C=0
       |
       v
Simulated outage of zone B
       |
       v
Router still considers stale endpoints for N request steps
       |
       v
After simulated health-detection threshold, use survivors only
       |
       v
Output successful/failed requests, availability and survivors
```

The failure-detection period is measured in **number of requests**, not elapsed time. It is not a prediction of Kubernetes or GKE failover duration.

## 3. Complete example

1. Choose a topology (`balanced` or `concentrated`).
2. Supply a failed zone (default `zone-b`), synthetic request count, detection threshold and random seed.
3. The simulator routes each synthetic request to a modeled replica.
4. Before the detection threshold, it may select dead zone-B endpoints, causing failures.
5. After detection, zone B is excluded from routing. If no replicas survive, every request continues to fail.
6. The report gives total successes, failures, availability, surviving replicas and a simulated recovery step.

Expected comparison: balanced placement can retain healthy replicas in zones A and C, while an all-B placement has no surviving replicas. Exact percentages depend on the configured seed and detection steps; they are **not** production availability targets.

## Live Kubernetes worker-outage experiment

The stronger [Kind worker interruption workflow](https://github.com/kanishksingh01/zonerescue/actions/runs/42425928204) assigns three disposable workers emulated zones A/B/C, pauses the zone-B worker's actual Docker container and verifies Kubernetes marks it NotReady. After EndpointSlice reconciliation, a client Pod sends real HTTP traffic to two ClusterIP Services: the balanced Service (zones A/B/C) handles 12/12 successfully, while the zone-B-only Service handles 0/12; following node unpause both succeed 8/8. This is **real worker interruption inside Kind**, not a GKE zone failure. See [technical guide](WORKER-OUTAGE.md).

## 4. Reproduce or review automatically

- [CI model tests and comparison](../.github/workflows/ci.yml)
- [Successful CI example](https://github.com/kanishksingh01/zonerescue/actions/runs/42399013927)

Optional Python 3.10+ commands from the repository root:

```bash
python3 -m zonerescue.cli --topology balanced --failed-zone zone-b --requests 300 --seed 42
python3 -m zonerescue.cli --topology concentrated --failed-zone zone-b --requests 300 --seed 42
python3 -m unittest discover -s tests -v
```

CI saves `balanced-report.json` and `concentrated-report.json` as synthetic benchmark artifacts. No cloud infrastructure is provisioned.

## 5. Code map

| Component | Location |
| --- | --- |
| Topology, failure and routing model | [zonerescue/simulator.py](../zonerescue/simulator.py) |
| Experiment entry point | [zonerescue/cli.py](../zonerescue/cli.py) |
| Scenarios and assertions | [tests/test_simulator.py](../tests/test_simulator.py) |
| Continuous integration | [.github/workflows/ci.yml](../.github/workflows/ci.yml) |

## 6. What remains

- Extend the now-tested worker interruption with actual network partition tests and repeated measurements across changing loads.
- Validate topology spread constraints and stateful dependencies in Kubernetes.
- Independently measure time to recover end-user SLO rather than only a worker readiness-and-probe window.
- Optionally validate on GKE after cost and blast-radius limits are established.

The successful Kind runs demonstrate real Kubernetes Service routing and isolated worker-failure survival after endpoint reconciliation, **not** a GKE multi-zone recovery. See [P0 issue](https://github.com/kanishksingh01/zonerescue/issues/1) and [blueprint](https://github.com/kanishksingh01/zonerescue/issues/6).
