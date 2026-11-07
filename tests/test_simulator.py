import unittest
from zonerescue.simulator import Scenario, simulate, topology

class SimulationTests(unittest.TestCase):
    def test_balanced_survives_zone_loss(self):
        result = simulate(Scenario(topology("balanced"), requests=200, seed=42))
        self.assertGreater(result["availability"], 0.80)
        self.assertEqual(result["surviving_replicas"], 4)
        self.assertEqual(result["recovery_step"], 15)
        self.assertFalse(result["action_executed"])

    def test_single_zone_concentration_loses_all_replicas(self):
        result = simulate(Scenario(topology("concentrated"), requests=200))
        self.assertEqual(result["availability"], 0)
        self.assertEqual(result["surviving_replicas"], 0)
        self.assertIsNone(result["recovery_step"])

    def test_no_failure_is_healthy(self):
        result = simulate(Scenario(topology("balanced"), failed_zone=None, requests=100))
        self.assertEqual(result["availability"], 1)
        self.assertEqual(result["failed"], 0)

    def test_seed_reproducibility(self):
        scenario = Scenario(topology("balanced"), seed=71)
        self.assertEqual(simulate(scenario), simulate(scenario))

    def test_invalid_config(self):
        with self.assertRaises(ValueError):
            Scenario({"zone-d": 1})
        with self.assertRaises(ValueError):
            Scenario({"zone-a": 0})
        with self.assertRaises(ValueError):
            Scenario({"zone-a": 1}, requests=0)

    def test_detection_zero_has_no_routing_to_failed_zone(self):
        result = simulate(Scenario(topology("balanced"), detection_requests=0))
        self.assertEqual(result["failed"], 0)

if __name__ == "__main__":
    unittest.main()
