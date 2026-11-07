# ZoneRescue — Delivery and release gates

## Implemented
- Seeded three-zone topology simulation and unit-tested placement comparisons.
- Real disposable Kind cluster with three emulated, labeled zones, a Deployment in each, and explicit restoration of zone-B workload after a bounded failure.
- Port-forwarded workload availability test with JSON artifacts.
- In-cluster ClusterIP routing and concentrated-vs-balanced Service comparison **under CI validation**.

## Still required before claiming completion
- Complete verification of the stronger in-cluster routing test in CI.
- Inject actual isolated worker/node networking loss rather than solely scaling a zone's Deployment to zero.
- Measure real wall-clock availability, loss, recovery and cleanup across repeated trials, with clear baselines.
- Test topology spread constraints and zone-dependent storage/data dependencies.
- Optional GKE deployment requires an explicit cost boundary and nonproduction credentials.

## Current release classification
**Experimental Kubernetes workload-zone resilience lab**, not a verified GKE zonal recovery system. See [end-to-end walkthrough](END-TO-END.md).