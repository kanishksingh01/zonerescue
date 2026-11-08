import unittest
from zonerescue.worker_fault import summarize_continuous

class ContinuousProbeTests(unittest.TestCase):
    def test_summary(self):
        rows = [{"seconds_from_pause_start": i, "ok": i != 2}
                for i in range(5)]
        report = summarize_continuous(rows)
        self.assertEqual(report["samples"], 5)
        self.assertEqual(report["failed"], 1)
        self.assertEqual(report["sampled_availability"], 0.8)
        self.assertEqual(report["first_failure_at_seconds"], 2)

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            summarize_continuous([])
