# ZoneRescue disposable Kind experiment (P1)

## Deployment
A control plane and three Kind workers are created. Each worker is labeled with an *emulated* `topology.kubernetes.io/zone` value. Three independent Deployments, each with a `nodeSelector`, place one nginx replica in each zone. A shared Kubernetes ClusterIP Service selects all three replicas.

## Experiment
1. Wait for three ready zone-specific Pods.
2. Probe 30 HTTP requests through the Service as a healthy baseline.
3. Scale **only** the zone-b Deployment to zero, removing its Service endpoints.
4. Confirm zones A and C remain ready and probe through the same shared Service.
5. In a finally block, scale zone-b back to one, verify all three Pods ready, and probe again.
6. Save timestamped JSON including success counts, latency max, restoration duration and cleanup verification.

The workload-scale action is constrained by hardcoded `kind-zonerescue` and `zonerescue-lab` identifiers, and the CI runner deletes the cluster afterward.

## What this does NOT prove
This is NOT an actual network partition, Kubernetes node outage, GKE zone outage, cross-zone data dependency test or validated production RTO. The test exercises Kubernetes scheduling labels, endpoint routing under Pod loss, and repeatable cleanup only. No fault is injected outside the disposable lab.
