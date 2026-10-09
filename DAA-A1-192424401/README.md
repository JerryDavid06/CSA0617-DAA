# DAA Assignment 1 — 192424401

**Student:** Jerry David  
**Registration No.:** 192424401  
**Course:** B.Tech Artificial Intelligence & Data Science  
**Subject:** Design and Analysis of Algorithms  

## Selected algorithms
1. Linear Search — iterative brute-force/sequential strategy
2. Recursive Binary Search — divide-and-conquer strategy with sorting preprocessing
3. Hash Table Search — hashing/direct-access strategy with hash-table construction

## Personal assessment configuration
- Personal seed: **2401**
- Required found key: **192424401**
- Required not-found key: **192424402**
- Dataset sizes: **1,000 / 10,000 / 100,000 / 1,000,000**

## Important
The third strategy is **Hash Table** as the working Group A choice because no group was supplied. If the faculty later assigns a different group, replace the third algorithm before submission.

## Verified implementation
The supplied implementation has been executed successfully. Correctness tests passed for the required personal keys and additional first/middle/last cases. The benchmark produced `results/results.csv` and the graphs in `results/graphs/`.

## Main commands
```bash
python -m pip install -r requirements.txt
python src/dataset_generator.py
python src/correctness_test.py
python src/benchmark.py
python src/plot_results.py
```

## Main experimental result
For the original single-query experiments at 1,000,000 records:
- Linear Search total: 8.7834 ms (found key), 32.6264 ms (not found)
- Recursive Binary Search total: 220.6659 ms (found key), 227.2795 ms (not found)
- Hash Table Search total: 108.0468 ms (found key), 123.9583 ms (not found)

Therefore the baseline recommendation is Linear Search when only one isolated lookup is considered and preprocessing is included.

For Task 12, 50,000 searches on 1,000,000 records:
- Recursive Binary Search: 446.6929 ms including sorting
- Hash Table Search: 147.7883 ms including table construction

The adapted design is therefore Hash Table Search for the high-frequency, once-daily-update workload.

## Repository structure
```text
DAA-A1-192424401-JerryDavid/
├── README.md
├── requirements.txt
├── report/
│   └── DAA_A1_192424401.pdf
├── src/
├── data/
├── results/
│   ├── results.csv
│   ├── task12_results.csv
│   └── graphs/
├── screenshots/
└── docs/
```

## Academic integrity / final review
The final report and results must be reviewed by the student before submission. The student should be able to explain the algorithms, recurrence, graphs, benchmark methodology, and Task 12 decision during the viva.
