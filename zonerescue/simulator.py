"""Deterministic synthetic multi-zone routing and failure model."""
from dataclasses import dataclass, asdict
from random import Random

ZONES = ("zone-a", "zone-b", "zone-c")

@dataclass(frozen=True)
class Scenario:
    placement: dict[str, int]
    failed_zone: str | None = "zone-b"
    detection_requests: int = 15
    requests: int = 300
    seed: int = 42

    def __post_init__(self):
        if not self.placement or any(zone not in ZONES for zone in self.placement):
            raise ValueError("placement must use known synthetic zones")
        if any(type(n) is not int or n < 0 for n in self.placement.values()):
            raise ValueError("replicas must be non-negative integers")
        if sum(self.placement.values()) < 1:
            raise ValueError("at least one replica is required")
        if self.failed_zone is not None and self.failed_zone not in ZONES:
            raise ValueError("unknown simulated failed zone")
        if self.detection_requests < 0 or self.requests < 1:
            raise ValueError("invalid detection or request count")

def simulate(scenario: Scenario) -> dict:
    rng = Random(scenario.seed)
    endpoints = [zone for zone, count in scenario.placement.items() for _ in range(count)]
    healthy = [zone for zone in endpoints if zone != scenario.failed_zone]
    success = 0
    failures = 0
    before_detection_failed = 0
    for index in range(scenario.requests):
        # Until a hypothetical load-balancer health-check completes, failed-zone
        # endpoints remain eligible. Afterwards, only healthy endpoints remain.
        detected = (scenario.failed_zone is not None
                    and index >= scenario.detection_requests)
        eligible = healthy if detected else endpoints
        if not eligible or rng.choice(eligible) == scenario.failed_zone:
            failures += 1
            if not detected:
                before_detection_failed += 1
        else:
            success += 1
    surviving_capacity = len(healthy) if scenario.failed_zone else len(endpoints)
    recovery_step = (
        min(scenario.detection_requests, scenario.requests)
        if surviving_capacity > 0 and scenario.failed_zone is not None else None)
    return {
        "scenario": asdict(scenario),
        "requests": scenario.requests,
        "successful": success,
        "failed": failures,
        "availability": round(success / scenario.requests, 4),
        "failures_before_detection": before_detection_failed,
        "surviving_replicas": surviving_capacity,
        "recovery_step": recovery_step,
        "recovery_unit": "simulated request steps (not seconds)",
        "action_executed": False,
    }

def topology(kind: str) -> dict[str, int]:
    if kind == "balanced":
        return {"zone-a": 2, "zone-b": 2, "zone-c": 2}
    if kind == "concentrated":
        return {"zone-a": 0, "zone-b": 6, "zone-c": 0}
    raise ValueError("topology must be balanced or concentrated")
