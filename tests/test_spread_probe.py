import unittest
from zonerescue.spread_probe import placement_from_pods

def pod(node, ready=True):
    return {
        "metadata": {"name": "unit-pod"},
        "spec": {"nodeName": node},
        "status": {"conditions": [{"type": "Ready", "status": "True" if ready else "False"}]}
    }

class SpreadPlacementTests(unittest.TestCase):
    def test_balanced_placement(self):
        nodes = ["zonerescue-worker"]*2 + ["zonerescue-worker2"]*2 + ["zonerescue-worker3"]*2
        counts = placement_from_pods({"items": [pod(n) for n in nodes]})
        self.assertEqual(counts, {"zone-a": 2, "zone-b": 2, "zone-c": 2})

    def test_ignore_not_ready_pods(self):
        counts = placement_from_pods({"items": [pod("zonerescue-worker", False)]})
        self.assertEqual(counts["zone-a"], 0)

    def test_reject_unknown_nodes(self):
        with self.assertRaises(AssertionError):
            placement_from_pods({"items": [pod("unrecognized-worker")]})
