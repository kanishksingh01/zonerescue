# ZoneRescue — End-to-end walkthrough

> **Status:** Reproducible *simulation only*. No live Kubernetes zonal fault injection yet. Independent, Google Cloud-aligned portfolio project; not affiliated with Google.

## 1. The problem

Multiple replicas do not guarantee zone resilience if they all live in one failure domain. And even a well-spread application may temporarily route traffic to failed endpoints until health detection catches up.

**What we built:** A deterministic model that compares two placement choices when one simulated zone disappears.

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

- Deploy actual sample services across labeled nodes in isolated Kind.
- Verify topology spread constraints and zone-specific endpoint selection in the Kubernetes API.
- Inject bounded pod/network failures with deterministic cleanup and continuous HTTP probing.
- Report real wall-clock detection/recovery times and compare spread strategies.
- Optionally validate on GKE after cost and blast-radius limits are established.

The current success demonstrates correct *simulation behavior*, not an actual GKE multi-zone recovery. See [P0 issue](https://github.com/kanishksingh01/zonerescue/issues/1) and [blueprint](https://github.com/kanishksingh01/zonerescue/issues/6).
