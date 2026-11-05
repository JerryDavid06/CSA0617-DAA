# DAA Assignment 3 - Python source code

## Fidelity to the supplied PDF
The PDF is a 40-page report, not a complete source-code listing. Page 39 names
common.py and q1.py through q7.py, but those original files are not embedded.
The embedded attachments are equation XML files, not Python programs.

This package preserves the algorithms and function interfaces in the printed
excerpts and supplies reconstructed helpers, counters, baselines, wrappers and
small runnable demonstrations. It is not a byte-for-byte recovery of the original
scripts and does not claim to regenerate every table or exact random-data count.
Formatting and comments have been normalized. Added instrumentation is identified
in the code. No benchmark timings have been fabricated or copied into output.

## Files and source pages (PDF page numbers)
- common.py: reconstructed shared counters, seed 2401 and median timing helper.
- q1.py: max/min (page 2), binary search (page 5); power-of-two split reconstructed
  from page 4.
- q2.py: Quick Sort and Merge Sort (page 7). Pivot and input builders reconstructed
  from pages 6-10. Quick Sort deliberately retains the printed two list passes;
  its comparison counter uses the report's logical partition convention.
- q3.py: school and Karatsuba coefficient multiplication (page 12). Padding,
  final carry processing and counters added using pages 11-15. Core karatsuba
  expects equal power-of-two lengths; multiply() handles integers and padding.
- q4.py: Strassen (page 16). Conventional multiplication, block helpers, padding
  wrapper and optional NumPy variant reconstructed from pages 15-21. Core
  strassen expects power-of-two square matrices; multiply() pads arbitrary sizes.
- q5.py: closest_dc (page 22); brute force, merge and dataset helpers added.
  Pass x-sorted points to closest_dc. Returned distances are squared distances.
- q6.py: Median of Medians (page 26), MITM subset sum (page 28). Insertion sort,
  partition, QuickSelect and Gray-code brute force reconstructed. k is zero-based.
- q7.py: self-contained maximum subarray. MaxSub directly translates the
  pseudocode on page 33. Baselines reconstructed from pages 30-36. Student A's
  proposal is deliberately incorrect and retained for comparison, as in the PDF.

## Run
Use Python 3.12 or newer. Extract the ZIP, open this folder in a terminal, and run:

    python q1.py
    python q2.py
    python q3.py
    python q4.py
    python q5.py
    python q6.py
    python q7.py

The default demos use manageable inputs and print actual computed results.
Only numpy_strassen() needs NumPy; all default demos use the standard library.
Optional NumPy installation: python -m pip install numpy

For large sorted Quick Sort inputs the recursion limit must exceed the input
size; the default q2 demo raises it to 20000. The algorithm retains the report's
recursive implementation and can use considerable memory on degenerate inputs.
Max/min and maximum subarray algorithms require nonempty input. Karatsuba's
multiply() wrapper accepts non-negative integers and cutoff >= 1.

## Validation performed
All seven scripts completed successfully. Checks included randomized sorting,
selection and max/min against Python references; 300 random 40-digit integer
pairs at four Karatsuba cutoffs; Strassen against conventional multiplication
for sizes 1-13, 17, 31, 33 and 50 with cutoffs 1 and 2; optional NumPy comparison;
closest pair with duplicate points against brute force; 200 randomized subset
sum comparisons; and 3000 random maximum-subarray comparisons plus fixed cases.
Exact Karatsuba and Strassen operation-count formulas were also checked.
Timings and random-data tables from the original report are not reproduced.
