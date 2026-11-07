# ZoneRescue in-cluster routing comparison

The existing simple Kind test checked a port-forwarded Service; port-forward may choose a single Pod, so that test alone cannot establish full Kubernetes Service routing. This stronger test launches a BusyBox client Pod in synthetic zone A and performs HTTP requests against real ClusterIP DNS names.

Two Services share the same demonstration Pods: `demo` selects zones A, B and C, while `demo-b-only` selects only zone B.

The test checks EndpointSlice readiness before each phase:
- **Baseline:** all 3 balanced endpoints and 1 concentrated endpoint are ready. Both Services answer requests.
- **Failure:** scale only zone-B Deployment to zero; balanced Service still has 2 healthy endpoints and must answer; the concentrated Service has zero endpoints and must reject all requests.
- **Recovery:** restore zone B; both Services must answer again.

The report records HTTP success/failure and elapsed time to restore endpoints and verify requests. No real cloud zone, Kubernetes worker node, network path or shared data dependency is disrupted. This is controlled Pod availability/failure-domain testing on disposable Kind only.
