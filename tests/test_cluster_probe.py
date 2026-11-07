import json
import unittest
from unittest.mock import patch
from zonerescue.cluster_probe import count_endpoints

class ClusterProbeTests(unittest.TestCase):
    def test_empty_endpointslice_is_zero(self):
        payload = {"kind": "EndpointSliceList", "items": [
            {"endpoints": None}, {"endpoints": []}]}
        with patch("zonerescue.cluster_probe.kubectl", return_value=json.dumps(payload)):
            self.assertEqual(count_endpoints("demo-b-only"), 0)

    def test_ready_endpoints_only(self):
        payload = {"items": [{"endpoints": [
            {"conditions": {"ready": True}}, {"conditions": {"ready": False}},
            {"conditions": {"ready": True}}]}]}
        with patch("zonerescue.cluster_probe.kubectl", return_value=json.dumps(payload)):
            self.assertEqual(count_endpoints("demo"), 2)

if __name__ == "__main__":
    unittest.main()
