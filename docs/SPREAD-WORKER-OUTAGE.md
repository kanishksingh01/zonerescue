# Native Kubernetes topology-spread Service under an actual Kind worker outage

This experiment combines two verified foundations:

1. Kubernetes schedules six replicas of a **single Deployment** with `topologySpreadConstraints` across three Kind workers labeled as emulated zones (two ready replicas each).
2. The test pauses zone-B's worker container. After Kubernetes updates Node readiness and EndpointSlices, the spread Service must remain available through four healthy endpoints while the zone-B-only Service fails.
3. On worker recovery, all six spread endpoints must return and the Service must pass HTTP probes again.

The benchmark records initial scheduler placement and the spread Service's baseline, outage, and restoration results alongside the existing manually pinned Service controls.

The zones are emulated on one GitHub-hosted Kind cluster. This is not a real Google Cloud zonal outage, multi-region failover, or production RTO measurement.
