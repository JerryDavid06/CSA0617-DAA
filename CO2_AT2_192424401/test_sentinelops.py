"""Run with python -m unittest -v test_sentinelops.py (standard library only)."""
import math
import random
import unittest
import sentinelops as s


class TriageTests(unittest.TestCase):
    def test_sort_sample_and_identity(self):
        data = [('A1', 3), ('A2', 9), ('A3', 5), ('A4', 9), ('A5', 1)]
        expected = [('A2', 9), ('A4', 9), ('A3', 5), ('A1', 3), ('A5', 1)]
        for sort in (s.sort_alerts, s.insertion_sort_alerts):
            copy = data[:]
            self.assertIs(sort(copy), copy)
            self.assertEqual(copy, expected)

    def test_sort_boundaries(self):
        for data in ([], [('x', 1)], [('a', 2), ('b', 2)],
                     [('a', 1), ('b', 3), ('c', 2)]):
            self.assertEqual(s.insertion_sort_alerts(data[:]), s.sort_alerts(data[:]))

    def test_blocklist(self):
        addresses = ['10.0.0.5', '10.0.0.9', '172.16.4.2']
        lookup = s.build_blocklist(addresses)
        for fn, block in ((s.is_blocked_linear, addresses), (s.is_blocked, lookup)):
            for ip, expected in [('10.0.0.5', True), ('10.0.0.9', True),
                                 ('172.16.4.2', True), ('8.8.8.8', False)]:
                self.assertIs(fn(block, ip), expected)
            self.assertIs(fn([], 'x'), False)

    def test_signature_boundaries(self):
        cases = [('FAILFAIXFAIL', 'FAIL', [0, 8]), ('xxFAIL', 'FAIL', [2]),
                 ('FAIL', 'FAIL', [0]), ('FAIX', 'FAIL', []),
                 ('x', 'long', []), ('aaa', 'aa', [0, 1]),
                 ('abc', 'x', []), ('aaa', 'a', [0, 1, 2]),
                 ('', 'a', []), ('', '', [0]), ('ab', '', [0, 1, 2])]
        for log, pattern, expected in cases:
            with self.subTest(log=log, pattern=pattern):
                self.assertEqual(s.find_signature(log, pattern), expected)

    def test_closest_sample(self):
        data = [(2, 3), (12, 30), (40, 50), (5, 1), (12, 10), (3, 4)]
        for fn in (s.closest_logins, s.closest_logins_bruteforce):
            pair, distance = fn(data)
            self.assertEqual(pair, (0, 5))
            self.assertAlmostEqual(distance, math.sqrt(2))

    def test_closest_boundaries_and_ties(self):
        cases = [([], None, math.inf), ([(1, 2)], None, math.inf),
                 ([(3, 4), (3, 4)], (0, 1), 0),
                 ([(0, 0), (1, 0), (0, 1), (1, 1)], (0, 1), 1),
                 ([(9, 0), (0, 0), (8, 0), (1, 0)], (0, 2), 1),
                 ([(-3, -4), (0, 0)], (0, 1), 5)]
        for data, pair, distance in cases:
            for fn in (s.closest_logins, s.closest_logins_bruteforce):
                self.assertEqual(fn(data), (pair, distance))

    def test_invalid_locations(self):
        for bad in [[(math.nan, 0)], [(math.inf, 0)], [(1, 2, 3)],
                    [(10**1000, 0)], [('x', 0)], [(True, 0)]]:
            for fn in (s.closest_logins, s.closest_logins_bruteforce):
                with self.assertRaises(ValueError):
                    fn(bad)

    def test_rounded_float_distance_tie(self):
        # The slightly longer first pair and the shorter second pair both
        # round to distance 1.0; baseline retains the earlier index pair.
        points = [(0.0, 0.0), (1.0, 1e-8), (10.0, 0.0), (11.0, 0.0)]
        self.assertEqual(s.closest_logins(points),
                         s.closest_logins_bruteforce(points))
        rng = random.Random(607)
        for _ in range(200):
            points = [(rng.uniform(-10, 10), rng.uniform(-10, 10))
                      for _ in range(20)]
            self.assertEqual(s.closest_logins(points),
                             s.closest_logins_bruteforce(points))

    def test_randomised_oracles(self):
        rng = random.Random(606)
        for _ in range(200):
            data = [(rng.randrange(-10, 11), rng.randrange(-10, 11))
                    for _ in range(rng.randrange(30))]
            got, expected = s.closest_logins(data), s.closest_logins_bruteforce(data)
            self.assertEqual(got[0], expected[0])
            self.assertAlmostEqual(got[1], expected[1])
            alerts = [(str(i), rng.randrange(6)) for i in range(30)]
            self.assertEqual(s.insertion_sort_alerts(alerts[:]), s.sort_alerts(alerts[:]))
            log = ''.join(rng.choice('ab') for _ in range(20))
            pattern = ''.join(rng.choice('ab') for _ in range(rng.randrange(6)))
            expected_hits = [i for i in range(len(log) + 1)
                             if log.startswith(pattern, i)]
            self.assertEqual(s.find_signature(log, pattern), expected_hits)


if __name__ == '__main__':
    unittest.main(verbosity=2)
