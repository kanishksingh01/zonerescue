# ZoneRescue — Release status and evidence

## Lab-V1 acceptance
- [x] Deterministic multi-zone routing simulation
- [x] Three emulated Kind worker zones with actual `topology.kubernetes.io/zone` labels
- [x] Native scheduler topology-spread constrained single Deployment (six replicas; two per zone)
- [x] Verified real in-cluster ClusterIP Service requests to balanced vs concentrated placements
- [x] Real disposable worker pause, Node NotReady observation and EndpointSlice failover
- [x] Balanced Service survived endpoint-converged failure; concentrated zone-only Service failed
- [x] Worker unpause and Service restoration confirmed by real HTTP probes
- [x] Timestamped failure, endpoint-convergence and recovery checkpoints
- [x] New continuous HTTP probe samples across worker failure and recovery

## CI evidence
[Scheduler and service placement integration](https://github.com/kanishksingh01/zonerescue/actions/runs/42427776661), [worker outage and continuous probing](https://github.com/kanishksingh01/zonerescue/actions/runs/42427776481) passed. These are emulated zone labels in local Kind, not independent physical failure domains.

## Remaining before production consideration
Multiple statistically supported traffic loads, a genuine network partition scenario, external rather than exec-driven availability probes, replicated storage/data-dependency scenarios and explicit GKE cost/nonproduction permission boundaries. No cloud zone is ever shut down.

**Classification: experimental Kind zonal resilience lab; not verified GKE multi-zone disaster recovery.** [Walkthrough](END-TO-END.md).
