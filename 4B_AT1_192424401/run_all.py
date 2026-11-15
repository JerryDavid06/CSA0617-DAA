"""Run all six reproducible assignment experiments: python run_all.py."""
from pathlib import Path
import copy
import hashlib
import itertools
import json
import math
import platform
import random
import statistics
import subprocess
import sys
import time
import tracemalloc
import cases as c
import graphs as g
import optimization as o

BASE = Path(__file__).resolve().parent
EVIDENCE = BASE/"evidence"


def safe(value):
    if isinstance(value, float) and not math.isfinite(value):
        return "INF" if value > 0 else "-INF"
    if isinstance(value, dict):
        return {str(k): safe(v) for k,v in value.items()}
    if isinstance(value, (list,tuple)):
        return [safe(v) for v in value]
    return value


def bench(fn):
    times=[]
    for _ in range(3):
        start=time.perf_counter()
        result=fn()
        times.append(time.perf_counter()-start)
    tracemalloc.start()
    measured=fn()
    _, peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, dict(seconds_median=statistics.median(times), peak_python_bytes=peak)


def compact_tsp(result):
    return {k:result[k] for k in ("cost","route","stats")}


def label_route(route):
    if route is None:return "NO TOUR"
    return " -> ".join("Hub" if x==0 else chr(64+x) for x in route)


def main():
    EVIDENCE.mkdir(exist_ok=True)
    predictions=json.loads((BASE/"predictions.json").read_text(encoding="utf-8-sig"))
    results=dict(metadata=dict(python=platform.python_version(),platform=platform.platform(),
                 repeats=3,timing="Median perf_counter; generation excluded; counters included",
                 memory="Separate single-call tracemalloc peak, not process RSS"),
                 predictions=predictions)
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
            for p in BASE.glob("*.py")}
    results["metadata"]["source_sha256"]=hashes
    logs={}
    # Task 1
    lines=["TASK 1 WORD WRAP - actual execution",
           "Text: now we go again | spaces between words count as one character",
           "Both u^2 and u^3 penalties; final line penalty is zero."]
    wraps=[]
    for power in (2,3):
        for width in (6,7,8,10):
            r=o.word_wrap("now we go again".split(),width,power)
            wraps.append(dict(power=power,width=width,**r))
            lines.append(f"\nWidth={width}, power={power}, optimum={r['cost']}")
            for i,row in enumerate(r["lines"],1):
                lines.append(f"Line {i}: {' '.join(row['words'])!r}, unused={row['unused']}, penalty={row['penalty']}")
            lines.append("Suffix DP: "+str(r["dp"]))
            lines.append("Best end indices: "+str([(x["start"],x["best_end"]) for x in r["trace"]]))
    try:o.word_wrap(["again"],4)
    except ValueError as error:lines.append("\nBoundary overlong word: "+str(error))
    rng=random.Random(407)
    sensitivity=None
    for _ in range(20000):
        words=["x"*rng.randrange(1,9) for _ in range(8)]
        width=rng.randrange(max(map(len,words)),21)
        squared=o.word_wrap(words,width,2);cubic=o.word_wrap(words,width,3)
        if [x["words"] for x in squared["lines"]] != [x["words"] for x in cubic["lines"]]:
            sensitivity=dict(words=words,width=width,squared=squared,cubic=cubic)
            break
    lines.append("\nPower-sensitive extra case: "+json.dumps(safe(sensitivity)))
    results["word_wrap"]=dict(cases=wraps,power_sensitive=sensitivity)
    logs["01_word_wrap.txt"]="\n".join(lines)
    # Task 2
    knapsack={}
    lines=["TASK 2 KNAPSACK - actual selections and work counters"]
    for name,items,cap in [("normal",c.NORMAL_ITEMS,5),("counterexample",c.ADVERSARIAL_ITEMS,50)]:
        row=dict(items=items,capacity=cap)
        for label,fn in [("fractional",o.fractional_knapsack),("greedy_01",o.greedy_01),
                         ("dp_01",o.knapsack_01)]:
            r,b=bench(lambda fn=fn:fn(items,cap))
            row[label]=dict(result=r,measurement=b)
            lines.append(f"\n{name} {label}: value={r['value']}, selected={r['selected']}")
            lines.append("Work: "+str(r["stats"])+" | "+str(b))
            lines.append("Decisions: "+str(r.get("trace",r.get("traceback"))))
        knapsack[name]=row
    rng=random.Random(408)
    ratios=[];fast_time=exact_time=0;worst=None
    for trial in range(100):
        items=[(str(i),rng.randrange(1,41),rng.randrange(1,101)) for i in range(40)]
        start=time.perf_counter();fast=o.greedy_01(items,100,True);fast_time+=time.perf_counter()-start
        start=time.perf_counter();exact=o.knapsack_01(items,100);exact_time+=time.perf_counter()-start
        ratio=fast["value"]/exact["value"] if exact["value"] else 1
        ratios.append(ratio)
        if worst is None or ratio<worst["ratio"]:
            worst=dict(trial=trial,items=items,ratio=ratio,fast=fast["value"],exact=exact["value"])
    knapsack["quick_response"]=dict(cases=100,n=40,capacity=100,seed=408,
        mean_ratio=statistics.mean(ratios),minimum_ratio=min(ratios),
        exact_matches=sum(x==1 for x in ratios),heuristic_seconds_total=fast_time,
        dp_seconds_total=exact_time,worst_case=worst)
    lines.append("\n100-case quick-response experiment: "+json.dumps(knapsack["quick_response"]))
    results["knapsack"]=knapsack;logs["02_knapsack.txt"]="\n".join(lines)
    # Task 3
    normal=g.dijkstra(c.VERTICES,c.ROUTING,"A")
    guarded=""
    try:g.dijkstra(c.VERTICES,c.NEGATIVE,"A")
    except ValueError as error:guarded=str(error)
    unsafe=g.dijkstra(c.VERTICES,c.NEGATIVE,"A",True)
    negative=g.bellman_ford(c.VERTICES,c.NEGATIVE,"A")
    cycle_messages={}
    for label,fn in [("bellman_ford",lambda:g.bellman_ford(c.VERTICES,c.CYCLE,"A")),
                     ("floyd",lambda:g.floyd(c.VERTICES,c.CYCLE))]:
        try:fn()
        except g.NegativeCycleError as error:cycle_messages[label]=str(error)
    allpairs=g.floyd(c.VERTICES,c.NEGATIVE)
    reach=g.warshall(c.VERTICES,c.NEGATIVE)
    routing=dict(vertices=c.VERTICES,normal_edges=c.ROUTING,negative_edges=c.NEGATIVE,
                 cycle_edges=c.CYCLE,normal=normal,guarded_rejection=guarded,unsafe_demo=unsafe,
                 bellman_ford=negative,negative_cycle_messages=cycle_messages,
                 floyd=allpairs,warshall=reach)
    lines=["TASK 3 ROUTING - eight vertices; fifteen baseline directed edges",
           "Baseline finalisation: "+str(normal["finalised"])]
    for v in c.VERTICES:
        lines.append(f"{v}: distance {normal['distances'][v]}, path {normal['paths'][v]}, predecessor {normal['predecessors'][v]}")
    lines.append("Relaxation trace: "+str(normal["trace"]))
    lines.append("\nPrediction is saved in predictions.json before changed-case execution.")
    lines.append("Negative edge C->B=-4; guarded rejection: "+guarded)
    lines.append("UNSAFE diagnostic distances: "+str(unsafe["distances"]))
    lines.append("Bellman-Ford distances: "+str(negative["distances"]))
    lines.append("Bellman-Ford passes: "+str(negative["passes"]))
    lines.append("Negative-cycle detection: "+str(cycle_messages))
    lines.append("\nFloyd on negative-edge graph WITHOUT the negative cycle:")
    lines.extend(str(row) for row in allpairs["matrix"])
    lines.append("Warshall (1 reachable, including diagonal):")
    lines.extend(str([int(x) for x in row]) for row in reach)
    results["routing"]=routing;logs["03_routing.txt"]="\n".join(lines)
    # Task 4
    base=o.assembly_schedule(c.PROCESSING,c.TRANSFER,c.ENTRY,c.EXIT)
    changed_transfer=copy.deepcopy(c.TRANSFER);changed_transfer[1][1]=20
    transfer_result=o.assembly_schedule(c.PROCESSING,changed_transfer,c.ENTRY,c.EXIT)
    changed_machine=copy.deepcopy(c.PROCESSING);changed_machine[1][4]=50
    machine_result=o.assembly_schedule(changed_machine,c.TRANSFER,c.ENTRY,c.EXIT)
    results["assembly"]=dict(processing=c.PROCESSING,transfer=c.TRANSFER,entry=c.ENTRY,
        exit=c.EXIT,baseline=base,transfer_changed=transfer_result,machine_changed=machine_result)
    lines=["TASK 4 ASSEMBLY LINE - actual execution",
           "Transfer indexing: transfer[line][j] leaves that line after station j+1."]
    for name,r in [("baseline",base),("one transfer 1 to 20",transfer_result),
                   ("Line 2 station 5 processing 5 to 50",machine_result)]:
        lines.append(f"\n{name}: total={r['time']}, route={r['route']}")
        for row in r["trace"]:lines.append(str(row))
        lines.append("Transfer points: "+str(r["transfers"]))
        lines.append("Exit totals: "+str(r["exit_totals"]))
    logs["04_assembly.txt"]="\n".join(lines)
    # Task 5
    mst={}
    lines=["TASK 5 MST - same undirected graph for all three methods"]
    for name,edges in [("unique",c.MST),("tied",c.MST_TIED)]:
        row=dict(edges=edges)
        for label,fn in [("kruskal",lambda:g.kruskal(c.VERTICES,edges)),
                         ("prim",lambda:g.prim(c.VERTICES,edges,"C")),
                         ("boruvka",lambda:g.boruvka(c.VERTICES,edges))]:
            r=fn();row[label]=r
            lines.append(f"\n{name} {label}: cost={r['cost']} edges={r['edges']}")
            lines.extend(str(step) for step in r["trace"])
        best=math.inf;count=0;trees=[]
        for subset in itertools.combinations(edges,7):
            sets=g.DSU(c.VERTICES)
            if all(sets.union(u,v) for u,v,w in subset):
                cost=sum(w for u,v,w in subset)
                if cost<best:best,count,trees=cost,1,[subset]
                elif cost==best:count+=1;trees.append(subset)
        row["exhaustive"]=dict(cost=best,optimal_trees=count,trees=trees)
        lines.append(f"Independent enumeration: optimum={best}, number of MSTs={count}")
        mst[name]=row
    results["mst"]=mst;logs["05_mst.txt"]="\n".join(lines)
    # Task 6
    matrix=c.travel_matrix(6);main_tsp=o.held_karp(matrix)
    sample_states=[dict(mask=mask,last=last+1,cost=main_tsp["dp"][mask,last],
                        predecessor=main_tsp["parent"][mask,last])
                   for mask,last in sorted(main_tsp["dp"])[:16]]
    small=c.travel_matrix(4)
    enumeration=[]
    for perm in itertools.permutations(range(1,5)):
        route=(0,)+perm+(0,)
        value=sum(small[u][v] for u,v in zip(route,route[1:]))
        enumeration.append(dict(route=list(route),cost=value))
    small_dp=o.held_karp(small)
    assert min(row["cost"] for row in enumeration)==small_dp["cost"]
    growth=[]
    for m in (4,5,6,7,8,10,12):
        mat=c.travel_matrix(m)
        r,measurement=bench(lambda:o.held_karp(mat))
        assert r["stats"]["states"]==m*2**(m-1)
        growth.append(dict(deliveries=m,total_vertices=m+1,**r["stats"],**measurement))
    results["tsp"]=dict(matrix=matrix,main=compact_tsp(main_tsp),sample_states=sample_states,
        small_matrix=small,enumeration=enumeration,small_dp=compact_tsp(small_dp),growth=growth)
    lines=["TASK 6 TSP - hub + six deliveries; Manhattan travel costs",
           "Input cost matrix:"]+[str(row) for row in matrix]
    lines.append("Complete route: "+label_route(main_tsp["route"]))
    lines.append("Minimum cost: "+str(main_tsp["cost"]))
    lines.append("States and transitions: "+str(main_tsp["stats"]))
    lines.append("Sample intermediate DP states:")
    lines.extend(str(row) for row in sample_states)
    lines.append("\nFour-delivery exhaustive comparison:")
    lines.extend(label_route(row["route"])+" = "+str(row["cost"]) for row in enumeration)
    lines.append("DP optimum: "+str(small_dp["cost"]))
    lines.append("\nState growth:")
    lines.extend(str(row) for row in growth)
    lines.append("No exact 200-delivery run was attempted.")
    logs["06_tsp.txt"]="\n".join(lines)
    for filename,text in logs.items():
        (EVIDENCE/filename).write_text(text+"\n",encoding="utf8")
    completed=subprocess.run([sys.executable,"-m","unittest","-v","test_algorithms.py"],
                             cwd=BASE,capture_output=True,text=True)
    (EVIDENCE/"07_tests.txt").write_text(completed.stdout+completed.stderr,encoding="utf8")
    assert completed.returncode==0
    (BASE/"results.json").write_text(json.dumps(safe(results),indent=2),encoding="utf8")
    print("All six experiments completed. Results, predictions and intermediate logs saved.")
    print("Wrap costs square:",[x["cost"] for x in wraps if x["power"]==2])
    print("Wrap costs cubic:",[x["cost"] for x in wraps if x["power"]==3])
    print("Assembly:",base["time"],base["route"],"modified",transfer_result["route"],machine_result["route"])
    print("TSP:",main_tsp["cost"],label_route(main_tsp["route"]))
    print("Power-sensitive case:",[len(w) for w in sensitivity["words"]],sensitivity["width"])
    print(completed.stderr.splitlines()[-1])


if __name__=="__main__":
    main()

