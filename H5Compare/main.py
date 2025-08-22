# H5Compare/main.py
import sys, os
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from queue import Queue
from threading import Thread
import signal  # <-- for graceful abort

# Ensure parent folder is in sys.path so absolute imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from H5Compare import abort_flag  # <-- shared abort flag

def handle_sigterm(signum, frame):
    abort_flag.ABORT = True

signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)

from H5Compare.config import LOCAL_ROOT, REMOTE_ROOT, NUM_WORKERS, REPORT_FILE, GUI_MODE, SIZE_TOL_MB
from H5Compare.utils import collect_h5_files
from H5Compare.comparator import compare_file_task
from H5Compare.logger import log_writer

def run_comparison(local_root=LOCAL_ROOT, remote_root=REMOTE_ROOT):
    q = Queue()
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(f"HDF5 Comparison Report (Parallelized)\nGenerated: {datetime.now()}\n")
        f.write("="*60 + "\n")

    writer_thread = Thread(target=log_writer, args=(q, REPORT_FILE), daemon=True)
    writer_thread.start()

    local_files  = collect_h5_files(local_root)
    remote_files = collect_h5_files(remote_root)

    # --- Global pre-check: count and size ---
    local_count, remote_count = len(local_files), len(remote_files)
    local_size  = sum(os.path.getsize(p) for p in local_files.values())
    remote_size = sum(os.path.getsize(p) for p in remote_files.values())
    size_diff_mb = abs(local_size - remote_size) / (1024 * 1024)

    if local_count != remote_count:
        q.put(f"[ERROR] File count mismatch: Local={local_count}, Remote={remote_count}")
        q.put("__DONE__")
        writer_thread.join()
        return

    if size_diff_mb > SIZE_TOL_MB:
        q.put(f"[ERROR] Total size mismatch: Local={local_size/1e6:.2f} MB, "
              f"Remote={remote_size/1e6:.2f} MB (Δ={size_diff_mb:.2f} MB, "
              f"tolerance={SIZE_TOL_MB} MB)")
        q.put("__DONE__")
        writer_thread.join()
        return
    # --- End pre-check ---

    all_rel_paths = set(local_files.keys()) | set(remote_files.keys())

    executor = ProcessPoolExecutor(max_workers=NUM_WORKERS)
    try:
        tasks = []
        for rel_path in sorted(all_rel_paths):
            if abort_flag.ABORT:
                q.put("[ABORTED] Comparison stopped by user")
                break

            f_local  = local_files.get(rel_path)
            f_remote = remote_files.get(rel_path)

            if f_local and not f_remote:
                q.put(f"[MISSING on Remote] {rel_path}")
                continue
            if f_remote and not f_local:
                q.put(f"[MISSING on LOCAL] {rel_path}")
                continue

            tasks.append(executor.submit(compare_file_task, rel_path, f_local, f_remote))

        # Only iterate completed tasks if not aborted
        if not abort_flag.ABORT:
            for future in as_completed(tasks):
                if abort_flag.ABORT:
                    q.put("[ABORTED] Comparison stopped by user")
                    break
                q.put(future.result())

    finally:
        # Shutdown executor immediately if abort requested
        executor.shutdown(wait=False, cancel_futures=True)

    q.put("__DONE__")
    writer_thread.join()

    # --- Unified final message ---
    if not abort_flag.ABORT:
        final_msg = f"\nComparison finished. Full report saved to: {REPORT_FILE}"
        if GUI_MODE:
            q.put(final_msg)
        else:
            print(final_msg, flush=True)

if __name__ == "__main__":
    run_comparison()
