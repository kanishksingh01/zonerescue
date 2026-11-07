# Native topology-spread scheduling evidence

In a disposable Kind cluster with three workers labeled `topology.kubernetes.io/zone` as `zone-a`, `zone-b` and `zone-c`, ZoneRescue now deploys a **single six-replica Deployment** using `topologySpreadConstraints` with `maxSkew: 1`, `minDomains: 3` and `DoNotSchedule`. The integration test verifies Kubernetes actually scheduled **two ready replicas in each zone** and that the six-endpoint ClusterIP Service served 20 of 20 synthetic HTTP probes.

This adds real scheduler-placement evidence beyond the earlier manually pinned Deployments. It is not GKE failure-domain isolation: all three zones are emulated on one GitHub runner. Persistent volumes and cross-zone dependencies are not included.

The result appears as `spread-placement-report.json` in the `Kind Zone Workload Integration` workflow artifact.
