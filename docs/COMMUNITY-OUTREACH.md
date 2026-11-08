# ZoneRescue — Community outreach kit (draft, not posted)

**Target communities:** [Kubernetes SIG Scheduling](https://www.kubernetes.dev/community/community-groups/sigs/scheduling/) #sig-scheduling for topology placement questions; [GKE community support options](https://docs.cloud.google.com/kubernetes-engine/docs/getting-support) #kubernetes-engine for GKE-specific general discussion; [CNCF TAG Operational Resilience](https://contribute.cncf.io/community/tags/operational-resilience/) for operational takeaways.

## Draft title
Topology spread survived a worker outage — but we still lost 10/52 HTTP probes during convergence

## Draft
I'm running a small Kubernetes zonal-resilience lab called ZoneRescue. It creates three **emulated** zones using Kind node labels, schedules six replicas with topologySpreadConstraints, pauses a zone-B worker, and samples actual HTTP traffic through a ClusterIP Service during Kubernetes endpoint convergence and recovery.

The post-convergence balanced Service probes passed, but continuous sampling exposed a more interesting limitation: only **42 of 52** probes succeeded during the transition. The lab therefore does **not** support a zero-downtime claim, despite healthy replicas surviving in other emulated zones.

I'm looking for feedback on how best to distinguish pod readiness, EndpointSlice convergence and kube-proxy/connection routing effects in this setup, and how to design a stronger fixed-rate probe without overstating its precision. Are there known SIG Scheduling or networking test patterns that would make the experiment more faithful?

Happy to share a synthetic reproduction or give a short technical walkthrough once a public-safe version is available. This is not a physical GKE-zone outage.

## Etiquette
SIG Scheduling is best for placement policy and skew; use SIG Network/CNCF resilience discussions for connection behavior. Don't file an upstream bug without an independently reproducible Kubernetes defect.

See [end-to-end lab guide](END-TO-END.md) and [continuous availability results](CONTINUOUS-AVAILABILITY.md).
