# ZoneRescue P0 design

A synthetic topology is a mapping from zone name to replica count. A request router initially considers all replicas. On synthetic zone failure, the router continues trying stale endpoints until a configurable number of request steps elapses. Once the health-check window has elapsed it removes endpoints from the failed zone.

This deterministic simulation is intentionally simple. It does not represent real Kubernetes networking, zonal outage propagation, failover delays, traffic persistence, cloud load balancers, database dependencies, or cross-zone cost.

The P1 design will replace synthetic endpoints with isolated Kind workloads given simulated `topology.kubernetes.io/zone` node labels. Controlled pod/endpoint failures and continuous HTTP probes will measure real Kubernetes behavior. Cloud fault injection is explicitly out of scope until cleanup guarantees and blast-radius limits are verified.

No actual infrastructure mutations or cloud APIs are present in P0. The experiment's `recovery_step` is a request-index bound, never a wall-clock recovery time.
