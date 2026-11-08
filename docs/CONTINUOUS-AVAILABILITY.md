# Continuous Kubernetes Service probes during worker outage

The disposable Kind worker-outage experiment now starts a separate in-cluster Service probe thread as the worker pause begins. It records individual HTTP successes/failures with elapsed monotonic timestamps throughout the outage and recovery.

The resulting JSON artifact includes each sample, total failures, sample-level availability and the first recorded failure time. These samples complement the existing post-EndpointSlice-convergence checks: a service may have an availability dip *before* endpoints converge, even when its final steady-state probe is healthy.

**Limitations:** Sequential kubectl-exec probes are not a constant-rate external client, and their sampling/exec latency may hide brief interruptions. This is a controlled Kind experiment, not a certified recovery time objective or external customer availability measurement. CI remains a disposable cluster and restores the worker in a finally block.
