"""Run: python -m unittest -v test_algorithms.py"""
import itertools
import math
import random
import unittest
import optimization as o
import graphs as g
import cases as c


def brute_knapsack(items, capacity):
    return max(sum(x[2] for x in group)
               for n in range(len(items)+1) for group in itertools.combinations(items,n)
               if sum(x[1] for x in group)<=capacity)


def brute_tsp(cost):
    routes = [(sum(cost[u][v] for u,v in zip((0,)+p, p+(0,))), (0,)+p+(0,))
              for p in itertools.permutations(range(1,len(cost)))]
    return min(routes, default=(0,(0,0)))


def brute_assembly(a,t,e,x):
    values = []
    for route in itertools.product(range(2), repeat=len(a[0])):
        total = e[route[0]]+x[route[-1]]
        for j,line in enumerate(route):
            total += a[line][j]
            if j and route[j-1] != line:
                total += t[route[j-1]][j-1]
        values.append(total)
    return min(values)


class AlgorithmTests(unittest.TestCase):
    def test_word_wrap_widths_and_both_penalties(self):
        for power, costs in [(2,[10,20,4,1]),(3,[28,72,8,1])]:
            for width, expected in zip([6,7,8,10],costs):
                r=o.word_wrap("now we go again".split(),width,power)
                self.assertEqual(r["cost"],expected)
                self.assertEqual(sum(x["penalty"] for x in r["lines"]),expected)
                self.assertEqual(r["lines"][-1]["penalty"],0)

    def test_word_wrap_boundaries(self):
        self.assertEqual(o.word_wrap([],4)["cost"],0)
        self.assertEqual(o.word_wrap(["word"],4)["lines"][0]["unused"],0)
        with self.assertRaises(ValueError):o.word_wrap(["again"],4)
        with self.assertRaises(ValueError):o.word_wrap(["x"],0)
        with self.assertRaises(ValueError):o.word_wrap(["two words"],10)

    def test_word_wrap_exhaustive_breaks(self):
        rng=random.Random(401)
        for _ in range(80):
            words=["x"*rng.randrange(1,5) for _ in range(6)]
            width=rng.randrange(4,11)
            for power in (2,3):
                values=[]
                for cuts in itertools.product((False,True),repeat=5):
                    lines=[];start=0
                    for i,cut in enumerate(cuts):
                        if cut:lines.append(words[start:i+1]);start=i+1
                    lines.append(words[start:])
                    used=[sum(map(len,row))+len(row)-1 for row in lines]
                    if max(used)<=width:
                        values.append(sum((width-x)**power for x in used[:-1]))
                self.assertEqual(o.word_wrap(words,width,power)["cost"],min(values))

    def test_knapsack_normal(self):
        self.assertEqual(o.fractional_knapsack(c.NORMAL_ITEMS,5)["value"],27)
        self.assertEqual(o.knapsack_01(c.NORMAL_ITEMS,5)["selected"],["A","B"])

    def test_knapsack_counterexample(self):
        self.assertEqual(o.fractional_knapsack(c.ADVERSARIAL_ITEMS,50)["value"],240)
        self.assertEqual(o.greedy_01(c.ADVERSARIAL_ITEMS,50)["value"],160)
        r=o.knapsack_01(c.ADVERSARIAL_ITEMS,50)
        self.assertEqual((r["value"],r["selected"]),(220,["K2","K3"]))

    def test_knapsack_random_oracle(self):
        rng=random.Random(402)
        for _ in range(80):
            items=[(str(i),rng.randrange(1,12),rng.randrange(0,30)) for i in range(9)]
            cap=rng.randrange(0,30)
            self.assertEqual(o.knapsack_01(items,cap)["value"],brute_knapsack(items,cap))
            self.assertLessEqual(o.greedy_01(items,cap,True)["value"],brute_knapsack(items,cap))

    def test_knapsack_boundaries(self):
        self.assertEqual(o.knapsack_01([],0)["value"],0)
        self.assertEqual(o.fractional_knapsack([],0)["selected"],[])
        self.assertEqual(o.knapsack_01([("x",5,10)],2)["selected"],[])
        with self.assertRaises(ValueError):o.knapsack_01([("x",0,1)],2)
        with self.assertRaises(ValueError):o.fractional_knapsack([("x",1,-1)],2)

    def test_positive_routing_oracles(self):
        d=g.dijkstra(c.VERTICES,c.ROUTING,"A")
        b=g.bellman_ford(c.VERTICES,c.ROUTING,"A")
        f=g.floyd(c.VERTICES,c.ROUTING)["matrix"]
        self.assertEqual(d["distances"],b["distances"])
        self.assertEqual(list(d["distances"].values()),f[0])
        self.assertEqual(d["paths"]["H"],list("ABDEFGH"))

    def test_negative_edge_meaningful(self):
        with self.assertRaises(ValueError):g.dijkstra(c.VERTICES,c.NEGATIVE,"A")
        unsafe=g.dijkstra(c.VERTICES,c.NEGATIVE,"A",True)
        safe=g.bellman_ford(c.VERTICES,c.NEGATIVE,"A")
        self.assertEqual(unsafe["distances"]["B"],2)
        self.assertEqual(safe["distances"]["B"],1)
        self.assertEqual((unsafe["distances"]["H"],safe["distances"]["H"]),(12,11))

    def test_negative_cycles_and_unreachable_guard(self):
        with self.assertRaises(g.NegativeCycleError):g.bellman_ford(c.VERTICES,c.CYCLE,"A")
        with self.assertRaises(g.NegativeCycleError):g.floyd(c.VERTICES,c.CYCLE)
        r=g.bellman_ford(["A","X","Y"],[("X","Y",-2),("Y","X",1)],"A")
        self.assertEqual(r["distances"]["X"],math.inf)

    def test_warshall_bfs_and_floyd(self):
        reach=g.warshall(c.VERTICES,c.NEGATIVE)
        f=g.floyd(c.VERTICES,c.NEGATIVE)["matrix"]
        for i,source in enumerate(c.VERTICES):
            seen={source};todo=[source]
            while todo:
                u=todo.pop()
                for a,b,_ in c.NEGATIVE:
                    if a==u and b not in seen:seen.add(b);todo.append(b)
            self.assertEqual(reach[i],[v in seen for v in c.VERTICES])
            self.assertEqual(reach[i],[x != math.inf for x in f[i]])

    def test_all_pairs_costs_against_single_source(self):
        for edges in (c.ROUTING,c.NEGATIVE):
            matrix=g.floyd(c.VERTICES,edges)["matrix"]
            for i,source in enumerate(c.VERTICES):
                reference=g.bellman_ford(c.VERTICES,edges,source)["distances"]
                self.assertEqual(matrix[i],[reference[v] for v in c.VERTICES])

    def test_routing_unreachable_and_invalid(self):
        r=g.dijkstra(["A","B"],[],"A")
        self.assertIsNone(r["paths"]["B"])
        with self.assertRaises(ValueError):g.dijkstra(["A"],[("A","Z",1)],"A")
        with self.assertRaises(ValueError):g.dijkstra(["A"],[],"Z")

    def test_assembly_baseline_and_changes(self):
        base=o.assembly_schedule(c.PROCESSING,c.TRANSFER,c.ENTRY,c.EXIT)
        self.assertEqual((base["time"],base["route"]),(38,[1,2,1,2,2,1]))
        t=[r[:] for r in c.TRANSFER];t[1][1]=20
        modified=o.assembly_schedule(c.PROCESSING,t,c.ENTRY,c.EXIT)
        self.assertEqual(modified["time"],brute_assembly(c.PROCESSING,t,c.ENTRY,c.EXIT))
        self.assertEqual(modified["time"],39)
        a=[r[:] for r in c.PROCESSING];a[1][4]=50
        disrupted=o.assembly_schedule(a,c.TRANSFER,c.ENTRY,c.EXIT)
        self.assertEqual((disrupted["time"],disrupted["route"]),(39,[1,2,1,1,1,1]))

    def test_assembly_random_oracle(self):
        rng=random.Random(404)
        for _ in range(50):
            a=[[rng.randrange(1,10) for _ in range(5)] for _ in range(2)]
            t=[[rng.randrange(0,5) for _ in range(4)] for _ in range(2)]
            self.assertEqual(o.assembly_schedule(a,t,[1,2],[2,1])["time"],
                             brute_assembly(a,t,[1,2],[2,1]))

    def test_assembly_single_and_invalid(self):
        self.assertEqual(o.assembly_schedule([[3],[5]],[[],[]],[1,1],[1,1])["time"],5)
        with self.assertRaises(ValueError):o.assembly_schedule([[],[]],[[],[]],[1,1],[1,1])

    def test_mst_costs_and_ties(self):
        for edges in (c.MST,c.MST_TIED):
            results=[g.kruskal(c.VERTICES,edges),g.prim(c.VERTICES,edges,"C"),
                     g.boruvka(c.VERTICES,edges)]
            self.assertEqual([r["cost"] for r in results],[49,49,49])
            for r in results:
                self.assertEqual(len(r["edges"]),7)
                d=g.DSU(c.VERTICES)
                self.assertTrue(all(d.union(u,v) for u,v,w in r["edges"]))
        a=g.kruskal(c.VERTICES,c.MST_TIED)
        b=g.prim(c.VERTICES,c.MST_TIED,"C")
        self.assertNotEqual(set(a["edges"]),set(b["edges"]))

    def test_mst_exhaustive_reference(self):
        for edges,expected_count in [(c.MST,1),(c.MST_TIED,2)]:
            best=math.inf;count=0
            for subset in itertools.combinations(edges,7):
                d=g.DSU(c.VERTICES)
                if all(d.union(u,v) for u,v,w in subset):
                    value=sum(w for u,v,w in subset)
                    if value<best:best,count=value,1
                    elif value==best:count+=1
            self.assertEqual((best,count),(49,expected_count))

    def test_mst_disconnected(self):
        for fn in (g.kruskal,g.prim,g.boruvka):
            with self.assertRaises(ValueError):fn(["A","B","C"],[("A","B",1)])
            self.assertEqual(fn(["A"],[])["cost"],0)

    def test_tsp_four_and_six_delivery_oracles(self):
        for m in (4,6):
            matrix=c.travel_matrix(m);r=o.held_karp(matrix)
            self.assertEqual(r["cost"],brute_tsp(matrix)[0])
            self.assertEqual(sorted(r["route"][1:-1]),list(range(1,m+1)))
            self.assertEqual(sum(matrix[u][v] for u,v in zip(r["route"],r["route"][1:])),r["cost"])
            self.assertEqual(r["stats"]["states"],m*2**(m-1))

    def test_tsp_random_asymmetric(self):
        rng=random.Random(406)
        for _ in range(25):
            matrix=[[0 if i==j else rng.randrange(1,30) for j in range(5)] for i in range(5)]
            self.assertEqual(o.held_karp(matrix)["cost"],brute_tsp(matrix)[0])

    def test_tsp_empty_delivery_missing_tour_and_guard(self):
        self.assertEqual(o.held_karp([[0]])["cost"],0)
        self.assertIsNone(o.held_karp([[0,math.inf],[math.inf,0]])["route"])
        with self.assertRaises(ValueError):o.held_karp([[0]*201 for _ in range(201)])
        with self.assertRaises(ValueError):o.held_karp([[0,2]])


if __name__=="__main__":
    unittest.main(verbosity=2)


