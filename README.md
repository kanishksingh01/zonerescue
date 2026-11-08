# ZoneRescue

**Kubernetes multi-zone workload resilience experiments and deterministic placement simulations.** Independent cloud project; not affiliated with Google Cloud. Private during development.

**Engineering case study:** [Problem, design, measured evidence and tradeoffs](docs/CASE-STUDY.md).

**Start:** [Full end-to-end guide](docs/END-TO-END.md) · [Release criteria](docs/RELEASE-STATUS.md).

The repository models placement and zonal failures, then tests a disposable Kind cluster with three emulated zones. The lab removes a zone-B workload, verifies remaining replicas and restores the workload. Stronger in-cluster routing tests and an actual disposable Kind worker interruption have passed.

**Worker interruption evidence:** [Kind zone-B worker NotReady, balanced Service 12/12, single-zone Service 0/12, both restored](https://github.com/kanishksingh01/zonerescue/actions/runs/42425928204). Entire test window 74.45 seconds; not GKE RTO.


**Continuous availability finding:** [Latest disposable worker outage](https://github.com/kanishksingh01/zonerescue/actions/runs/42427776481) recorded 42/52 successful HTTP probes (80.77%) during the outage transition. After EndpointSlice convergence, the balanced Service recovered; this is **not** uninterrupted availability. [Native six-replica topology-spread test](https://github.com/kanishksingh01/zonerescue/actions/runs/42426890690) also passed.

**Current status:** Simulation and Kubernetes workload-loss lab, **not** verified GKE or physical zonal recovery. AI deferred.

[Simulation CI](.github/workflows/ci.yml) · [Kind experiment](.github/workflows/kind-integration.yml) · [Architecture](docs/ARCHITECTURE.md)
