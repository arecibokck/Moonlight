# h5compare/main.py
import sys, os
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from queue import Queue
from threading import Thread

# Ensure parent folder is in sys.path so absolute imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from h5compare.config import LOCAL_ROOT, REMOTE_ROOT, NUM_WORKERS, REPORT_FILE, GUI_MODE
from h5compare.utils import collect_h5_files
from h5compare.comparator import compare_file_task
from h5compare.logger import log_writer

def run_comparison(local_root=LOCAL_ROOT, remote_root=REMOTE_ROOT):
    q = Queue()
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(f"HDF5 Comparison Report (Parallelized)\nGenerated: {datetime.now()}\n")
        f.write("="*60 + "\n")

    writer_thread = Thread(target=log_writer, args=(q, REPORT_FILE), daemon=True)
    writer_thread.start()

    local_files  = collect_h5_files(local_root)
    remote_files = collect_h5_files(remote_root)
    all_rel_paths = set(local_files.keys()) | set(remote_files.keys())

    tasks = []
    with ProcessPoolExecutor(max_workers=NUM_WORKERS) as executor:
        for rel_path in sorted(all_rel_paths):
            f_local  = local_files.get(rel_path)
            f_remote = remote_files.get(rel_path)

            if f_local and not f_remote:
                q.put(f"[MISSING on Remote] {rel_path}")
                continue
            if f_remote and not f_local:
                q.put(f"[MISSING on LOCAL] {rel_path}")
                continue

            tasks.append(executor.submit(compare_file_task, rel_path, f_local, f_remote))

        for future in as_completed(tasks):
            q.put(future.result())

    q.put("__DONE__")
    writer_thread.join()

    final_msg = f"\nComparison finished. Full report saved to: {REPORT_FILE}"
    if GUI_MODE:
        q.put(final_msg)
    else:
        print(final_msg, flush=True)

if __name__ == "__main__":
    run_comparison()
