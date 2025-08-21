# h5compare/config.py
import os
import sys

LOCAL_ROOT  = r"D:\Data - Experiment\StructuralPhaseTransition"
REMOTE_ROOT = r"\\DyLabNAS\Data\StructuralPhaseTransition"

if len(sys.argv) >= 3:
    LOCAL_ROOT  = sys.argv[1]
    REMOTE_ROOT = sys.argv[2]

GUI_MODE = "--gui" in sys.argv

USE_H5DIFF = True
RTOL = 1e-6
ATOL = 1e-12
REPORT_FILE = "comparison_report.txt"
HASH_ALGO = "md5"
NUM_WORKERS = os.cpu_count() or 4
