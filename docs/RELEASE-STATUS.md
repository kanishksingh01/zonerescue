# ZoneRescue — Delivery and release gates

## Implemented
- Seeded three-zone topology simulation and unit-tested placement comparisons.
- Real disposable Kind cluster with three emulated, labeled zones, a Deployment in each, and explicit restoration of zone-B workload after a bounded failure.
- Earlier port-forward-only service test deprecated: it pinned a Pod and could not establish actual ClusterIP availability.
- In-cluster ClusterIP routing and concentrated-vs-balanced Service comparison **passed CI**.
- Actual disposable zone-B worker pause, Kubernetes Ready non-True status and EndpointSlice failover were verified; balanced Service succeeded during the outage; concentrated Service failed; both recovered.

## Still required before claiming completion
- Repeat verified worker-failure CI under varying workloads and add genuine network partition testing rather than only a paused local Kind worker.
- Measure real wall-clock availability, loss, recovery and cleanup across repeated trials, with clear baselines.
- Test topology spread constraints and zone-dependent storage/data dependencies.
- Optional GKE deployment requires an explicit cost boundary and nonproduction credentials.

## Verified worker-failure experiment
[Worker outage and Service restoration report](https://github.com/kanishksingh01/zonerescue/actions/runs/42425928204): Kubernetes worker NotReady; balanced Service 12/12 successful and zone-B-only Service 0/12 during outage; after unpause both 8/8 successful; 74.45 s entire test window. Synthetic emulated zone, not GKE.

## Current release classification
**Experimental Kubernetes workload-zone resilience lab**, not a verified GKE zonal recovery system. See [end-to-end walkthrough](END-TO-END.md).