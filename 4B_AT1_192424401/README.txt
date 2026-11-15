DAA ASSIGNMENT 4B DELIVERY NOTES
Student: Jerry David R | Registration: 192424401

Report
- DAA_Assignment_4B_Detailed_Answers.docx: editable answer report covering all six tasks.
- DAA_Assignment_4B_Reading_Copy.pdf: 32-page independently generated reading copy from the same content, with seven diagrams/charts. It is not an export from Word.
- Times New Roman, black authored text, justified body paragraphs and 1.5 line spacing. The supplied institutional logos retain their original colours. Cover metadata is an editable table.

Run with Python 3.10 or later from this folder
    python -m unittest -v test_algorithms.py
    python run_all.py
No third-party dependencies are needed for these five delivered Python source files.
The runner overwrites results.json and evidence/*.txt with a fresh run. Preserve a copy if retaining the supplied benchmark record.

Contents
optimization.py: Word Wrap, fractional and 0/1 knapsack, fast 0/1 heuristic, assembly scheduling and Held-Karp TSP.
graphs.py: Dijkstra, Bellman-Ford, Floyd, Warshall, Kruskal, Prim and Boruvka.
cases.py: all reproducible inputs.
run_all.py: executes experiments, gathers intermediate evidence and records measurements.
test_algorithms.py: 22 passing unittest methods, including exhaustive and independent references.
predictions.json: predictions saved before changed-case execution.
results.json: full results, timing, memory, discrete counters and source SHA-256 values.
evidence/: seven actual execution logs, including intermediate states and tests.
figures/: the seven report diagrams/charts, provided separately for reuse.

Assumptions and measurement
The source PDF has a blank Word Wrap penalty equation. At the student's request both unused^2 and unused^3 are supported, with final-line penalty zero. A separate case demonstrates that the two powers can select different breaks.
Times use perf_counter. Selected timing tables use the median of three calls; the 100-case heuristic comparison reports aggregate time for each method. Memory uses a separate single-call tracemalloc peak, not total operating-system process memory. Input generation is excluded. Instrumentation is included. Results identify the local Python version and platform. Runtime varies by computer.
Task 4's third assembly line is explained, not implemented. Exact TSP is not run for 200 deliveries. A guard rejects more than 16 deliveries.

Verification and limits
All 22 test methods passed. Source hashes match the executed version. Every page of the independent PDF was visually inspected. DOCX fonts, colours, paragraph spacing, body alignment, cover fields and embedded images were structurally checked.
Direct DOCX rendering could not be completed: the required LibreOffice converter is unavailable, and background Word access was unavailable. Word pagination is therefore not visually verified and may differ from the independent PDF.
Execution-window screenshot capture was attempted but application access approval timed out. Authentic intermediate text logs are supplied; there are no fabricated console screenshots. To add screenshots, run the commands above in your terminal or IDE and capture intermediate states as well as results. This requested screenshot component remains outstanding.

Submission instructions
Review the document in Microsoft Word and check page breaks before submission. Upload the report and required source/evidence files to the course's prescribed location. If GitHub submission is required, review and commit the files to your repository, then push using your own account and submit the requested repository link. The supplied cover displays https://github.com/JerryDavid06/CSA0617-DAA.git as provided; repository access, push and Classroom submission have not been performed or claimed.
