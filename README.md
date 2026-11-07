# ZoneRescue

**Multi-zone Kubernetes resilience engineering lab.** Independent project inspired by common cloud zonal-failure patterns; not affiliated with Google Cloud.

**Current scope:** A deterministic, synthetic three-zone failure simulator. No cloud credentials, Kubernetes cluster access, or destructive actions.

## P0 example

```bash
python3 -m zonerescue.cli --topology balanced --failed-zone zone-b --requests 300 --seed 42
python3 -m zonerescue.cli --topology concentrated --failed-zone zone-b --requests 300 --seed 42
python3 -m unittest discover -s tests -v
```

The experiment compares balanced workload placement with concentrated placement when one zone becomes unavailable. The simulator models request routing before and after a health-probe detection threshold.

**Important:** Results are measured in request steps, not seconds. This is not a real GKE outage, Kubernetes scheduling experiment, or test of production RTO.

## Milestones
- P0: deterministic topology and zone-loss simulation, measurable output, unit tests.
- P1: isolated Kind application with simulated zone labels and bounded failure injection.
- P2: continuous probes, cleanup safeguards, topology and dependency checks.
- P3: optional GKE validation, benchmark methodology, and portfolio case study.
- Later: AI-based topology risk review, deferred.

See [architecture](docs/ARCHITECTURE.md) and [P0 tracking](https://github.com/kanishksingh01/zonerescue/issues/1).
