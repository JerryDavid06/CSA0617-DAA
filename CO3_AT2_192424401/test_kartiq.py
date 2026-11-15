"""Regression and randomized oracle checks for the KartIQ reference module."""
import random
import unittest
import kartiq as k


class KartIQTests(unittest.TestCase):
    def test_stable_merge_sample(self):
        data = [(105, "O1"), (102, "O2"), (105, "O3"),
                (101, "O4"), (102, "O5"), (103, "O6")]
        stats = {}
        result = k.merge_sort_orders(data, stats)
        self.assertEqual(result, [(101, "O4"), (102, "O2"), (102, "O5"),
                                  (103, "O6"), (105, "O1"), (105, "O3")])
        self.assertEqual(stats["comparisons"], 9)
        self.assertEqual(data[0], (105, "O1"))

    def test_merge_boundaries_and_oracle(self):
        rng = random.Random(603)
        for n in range(100):
            data = [(rng.randrange(5), i) for i in range(n)]
            self.assertEqual(k.merge_sort_orders(data), sorted(data, key=lambda r: r[0]))

    def test_partition_sample(self):
        data = [42, 17, 63, 8, 55, 29]
        self.assertEqual(k.partition_first_desc(data), 2)
        self.assertEqual(data, [55, 63, 42, 8, 17, 29])
        with self.assertRaises(ValueError):
            k.partition_first_desc([])

    def test_score_sort_boundaries(self):
        for source in ([], [1], [7]*100, list(range(100)),
                       list(range(100, 0, -1)), [2, 1, 2, 4, 4, -1]):
            data = list(source)
            self.assertIs(k.sort_scores(data), data)
            self.assertEqual(data, sorted(source, reverse=True))

    def test_score_random_and_forced_fallback(self):
        rng = random.Random(604)
        for _ in range(100):
            source = [rng.randrange(-20, 21) for _ in range(rng.randrange(150))]
            self.assertEqual(k.sort_scores(source[:]), sorted(source, reverse=True))
            self.assertEqual(k.sort_scores(source[:], cutoff=1, depth_limit=0),
                             sorted(source, reverse=True))
        counts = {}
        k.sort_scores(list(range(50)), cutoff=1, depth_limit=0, stats=counts)
        self.assertEqual(counts["fallbacks"], 1)

    def test_lower_bound_boundaries(self):
        cases = [([], 1, None), ([(1, "a")], 1, 0),
                 ([(1, "a")], 0, None), ([(1, "a")], 2, None),
                 ([(2, "a"), (2, "b"), (2, "c")], 2, 0),
                 ([(1, "a"), (2, "b"), (2, "c"), (3, "d")], 2, 1)]
        for data, query, expected in cases:
            self.assertEqual(k.first_order_at_timestamp(data, query), expected)

    def test_lower_bound_oracle(self):
        rng = random.Random(605)
        for _ in range(100):
            data = sorted([(rng.randrange(20), i) for i in range(rng.randrange(100))])
            query = rng.randrange(22)
            expected = next((i for i, row in enumerate(data) if row[0] == query), None)
            self.assertEqual(k.first_order_at_timestamp(data, query), expected)

    def test_matrix_sample_and_counts(self):
        a, b = [[1, 7], [3, 5]], [[1, 3], [7, 5]]
        counts = {}
        self.assertEqual(k.strassen_multiply(a, b, 1, counts), [[50, 38], [38, 34]])
        self.assertEqual(counts["multiplications"], 7)
        self.assertEqual(counts["additions_subtractions"], 18)
        self.assertEqual(k.classical_multiply(a, b), [[50, 38], [38, 34]])

    def test_matrix_padding_and_oracle(self):
        rng = random.Random(606)
        for n in (1, 2, 3, 4, 5, 8, 9, 16):
            a = [[rng.randrange(-4, 5) for _ in range(n)] for _ in range(n)]
            b = [[rng.randrange(-4, 5) for _ in range(n)] for _ in range(n)]
            for cutoff in (1, 2, 4, 32):
                self.assertEqual(k.strassen_multiply(a, b, cutoff),
                                 k.classical_multiply(a, b))

    def test_matrix_float_and_invalid_inputs(self):
        a, b = [[0.1, 0.7], [0.3, 0.5]], [[0.1, 0.3], [0.7, 0.5]]
        for got, ref in zip(k.strassen_multiply(a, b, 1), k.classical_multiply(a, b)):
            for x, y in zip(got, ref):
                self.assertAlmostEqual(x, y, places=12)
        for a, b in (([], []), ([[1, 2]], [[1]]), ([[float("nan")]], [[1]])):
            with self.assertRaises(ValueError):
                k.strassen_multiply(a, b)
        with self.assertRaises(ValueError):
            k.strassen_multiply([[1]], [[2]], cutoff=0)


if __name__ == "__main__":
    unittest.main(verbosity=2)

