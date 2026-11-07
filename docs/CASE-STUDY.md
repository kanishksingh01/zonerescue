# Engineering case study — ZoneRescue

## Problem
Replicas alone don't guarantee availability. If an application's replicas all live in a single fault domain, a zonal failure removes every endpoint; spreading replicas can preserve serving capacity.

## Approach
I implemented a reproducible three-zone simulation and a stronger isolated Kubernetes experiment. A disposable Kind cluster labels three worker Nodes as emulated zones A, B and C, places one web workload in each and exposes two Services: a balanced Service selecting all three zones and a concentrated Service selecting only zone B. A client Pod in zone A sends real HTTP requests via ClusterIP and EndpointSlices. Zone B's workload is temporarily scaled to zero, then restored.

## Reproducible evidence
In one successful in-cluster test:
- Baseline: both balanced and zone-B-only Services answered 12/12 requests.
- While zone-B workloads were absent: balanced Service answered **12/12**; concentrated Service answered **0/12**.
- Following restoration: both Services answered **12/12**.
- The test verified endpoint readiness and cleanup; the reported restoration-plus-probe window was ~20.84 seconds.

**Proof:** [Kind in-cluster routing experiment](https://github.com/kanishksingh01/zonerescue/actions/runs/42424288207).

## Genuine Kind worker interruption (stronger follow-up)
[Successful worker-outage CI run](https://github.com/kanishksingh01/zonerescue/actions/runs/42425928204): a temporary Kind worker assigned to emulated zone B was paused until Kubernetes marked it NotReady and reconciled Service endpoints. The balanced Service served 12/12 requests through zones A and C; the zone-B-only Service served 0/12. Following worker unpause, both Services passed 8/8 requests. Outage/restoration experiment window was ~74.45 seconds; it is not a cloud GKE zone-outage RTO. [Technical lab guide](WORKER-OUTAGE.md).

## Engineering decisions
- Hardcode the disposable Kind context and namespace for fault actions.
- Use EndpointSlice readiness rather than mistaking a port-forwarded Pod for a load-balanced Service.
- Make restoration unconditional in a finally block.
- Keep synthetic simulation recovery steps separate from wall-clock Kind observations.

## Important limitations
The earlier experiment simulates **zone-specific workload loss**; the newer workflow pauses a real Kind worker. Neither is a physical GKE zone outage, full network partition or stateful failover. The time reported includes endpoint restoration and verification probes; it is not a guaranteed production RTO. No GKE credential or paid resource has been used.

## What would make this complete
Expand the proven isolated worker outage with network-partition and topology-spread tests, stateful dependencies and repeated measured failover under cleanup safeguards; validate optional GKE behavior only with approved cost limits. See [release gates](RELEASE-STATUS.md) and [full walkthrough](END-TO-END.md).
