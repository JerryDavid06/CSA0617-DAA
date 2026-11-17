CSA06 CO3 KARTIQ CASE STUDY

CODE AND EVIDENCE
kartiq.py: stable Merge Sort, sample first-pivot partition, guarded descending
Quick Sort, first-timestamp Binary Search, conventional and hybrid Strassen.
test_kartiq.py: ten passing test methods including boundaries, randomized
references, heap fallback, matrix padding and floating-point tolerance.
benchmark_kartiq.py: reproducible smaller experiments and large-size arithmetic.
measurements.json: actual measurements, operation counters and calculations.
execution_results.txt: actual sample execution and complete test output.
diagrams/: seven high-resolution monochrome figures used in the report.

RUN IN THIS FOLDER WITH PYTHON 3.10 OR LATER
python kartiq.py
python -m unittest -v test_kartiq.py
python benchmark_kartiq.py

No third-party packages are needed by these three files. The benchmark writes
measurements.json in the working folder. Input seeds and counters reproduce;
wall-clock times depend on the computer and its current workload.

SCOPE OF VERIFICATION
The 10-million-order, 100,000-seller and 1,024-square production estimates in
the report are mathematical calculations, not claimed full-size timed runs.
Actual experiments use 256-2,048 ordered seller scores and square matrices of
size 16, 32, 64 and 128. Every measured result is checked against a reference.
The cutoff used by the matrix experiment is 16; the module default is 32.
Neither is claimed to be a universally optimal production threshold.

CONTRACTS
Input order expresses global arrival order; timestamp keys are comparable.
Binary Search requires ascending timestamp order and returns the first index,
or None. The leaderboard is descending and does not promise tie stability.
Matrix routines expect nonempty equal-size square numeric matrices. Strassen
pads non-power-of-two sizes and crops the result; floating results should be
compared with tolerances. The code is a transparent educational reference,
not a distributed ingestion system or a tuned native matrix library.

No GitHub upload, repository push or Classroom submission has been performed.
Fill in your student details and follow the institution's attribution rules.

