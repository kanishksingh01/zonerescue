# Worker failure timing methodology

The disposable-Kind worker-outage experiment now records elapsed time from the worker pause to five observable checkpoints: Node NotReady detection, ClusterIP EndpointSlice convergence, worker unpause, Node Ready restoration, and service EndpointSlice restoration, followed by successful HTTP probes. This differentiates detection lag, endpoint reconciliation lag, and recovery time from the previous single whole-experiment duration.

**These are timings in a GitHub-hosted, synthetic Kind cluster, not GKE SLAs or production RTO.** Probe samples remain limited; repeat trials and always-on sampling are outstanding.

Evidence artifacts: `worker-outage-report.json`, uploaded by `.github/workflows/worker-outage.yml`.
