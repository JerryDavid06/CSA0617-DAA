SENTINELOPS CSA06 CO2 ANSWER PACKAGE

CSA06_CO2_AnswersReport.docx: detailed answers to parts (a)-(e).
sentinelops.py: final module and sample demonstration.
test_sentinelops.py: nine unittest methods; boundaries and 400 randomized
nearest-pair oracle trials (200 integer and 200 floating-point).
benchmark_sentinelops.py: measured 1000, 2000, 4000 and 8000 login events;
nearly sorted and random insertion-sort inputs; three timing repeats.
benchmark_results.json: actual final measurements and counters.
execution_results.txt: actual original, incremental, final and test output.
original_reproduction.py: intentionally faulty original algorithms, with PDF
wrapped comment lines normalised so the original behaviour can be executed.
reproduce_defects.py: execute all intermediate repairs and insertion trace.

RUN IN THIS FOLDER WITH PYTHON 3.10 OR LATER
python sentinelops.py
python reproduce_defects.py
python -m unittest -v test_sentinelops.py
python benchmark_sentinelops.py

No external packages are required. Timings depend on the machine; counts and
seeded inputs are reproducible. The benchmark writes benchmark_results.json.

INPUTS
Alert entries contain an identifier and comparable severity. The stable
production sort changes and returns the supplied list. For blocklist queries,
build a frozenset once and refresh it whenever the source blocklist changes.
IP membership uses exact strings. Signature matching includes overlaps and
defines empty patterns as matching all boundaries.

Login locations are indexable pairs of int/float planar kilometre coordinates,
finite and within +/-10**12, excluding Boolean values. No pair is (None, inf).
Ties use the lexicographically earliest original index pair, including ties
caused by rounding a square root. The optimised method uses conservative
squared bounds and roots only for viable candidates. It remains quadratic in
the worst case. Locations and their arrival order are not modified.

EVIDENCE LIMITATION
All code and measurements were actually executed. Authentic execution
screenshots could not be captured because computer control stopped when it
could not verify the browser address. The included records are actual text
transcripts and measured JSON, not fabricated screen captures.
