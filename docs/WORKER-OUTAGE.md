# Actual Kubernetes worker interruption in a disposable Kind cluster

This test goes beyond scaling one Deployment to zero. It labels three temporary Kind workers as zones A/B/C, deploys one workload in each zone, and uses an in-cluster client to probe a balanced three-zone Service and a zone-B-only Service. It then **pauses the Docker container representing the zone-B worker node**. It waits for the real Kubernetes Node Ready condition to become non-True and for the EndpointSlice controller to remove unavailable Pod endpoints, and measures the Services again.

A finally block always unpauses that worker, waits until it returns Ready=True, verifies both Services regain ready endpoints, and probes recovery. No arbitrary node/container context is accepted by the test harness; it targets the GitHub runner's disposable Kind worker only.

This is genuine Kubernetes worker unavailability on a local multi-node test cluster, **not a cloud zone outage**. There are no dependent databases or cross-zone service mesh links. Detection latency can vary according to Kubernetes node monitoring and eviction settings, so the workflow must be validated against real CI runs before making timing claims.
