# ZoneRescue

**Kubernetes multi-zone workload resilience experiments and deterministic placement simulations.** Independent cloud project; not affiliated with Google Cloud. Private during development.

**Engineering case study:** [Problem, design, measured evidence and tradeoffs](docs/CASE-STUDY.md).\n\n**Start:** [Full end-to-end guide](docs/END-TO-END.md) · [Release criteria](docs/RELEASE-STATUS.md).

The repository models placement and zonal failures, then tests a disposable Kind cluster with three emulated zones. The lab removes a zone-B workload, verifies remaining replicas and restores the workload. A stronger in-cluster Service routing test is under validation.

**Current status:** Simulation and Kubernetes workload-loss lab, **not** verified GKE or physical zonal recovery. AI deferred.

[Simulation CI](.github/workflows/ci.yml) · [Kind experiment](.github/workflows/kind-integration.yml) · [Architecture](docs/ARCHITECTURE.md)
