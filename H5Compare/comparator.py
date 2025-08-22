import os
from .utils import file_hash, run_h5diff, compare_h5
from .config import USE_H5DIFF
from H5Compare import abort_flag  # <-- shared abort flag

def compare_file_task(rel_path, f_local, f_remote):
    # Check abort flag at the very start
    if abort_flag.ABORT:
        return f"[ABORTED] {rel_path}"

    try:
        size_local  = os.path.getsize(f_local)
        size_remote = os.path.getsize(f_remote)
        if abort_flag.ABORT: return f"[ABORTED] {rel_path}"
        if size_local != size_remote:
            return f"[DIFFERENT SIZE] {rel_path}"

        hash_local  = file_hash(f_local)
        if abort_flag.ABORT: return f"[ABORTED] {rel_path}"
        hash_remote = file_hash(f_remote)
        if abort_flag.ABORT: return f"[ABORTED] {rel_path}"

        if hash_local == hash_remote:
            return f"[OK] {rel_path} (hash match)"

        if USE_H5DIFF:
            result = run_h5diff(f_local, f_remote)
            if abort_flag.ABORT: return f"[ABORTED] {rel_path}"
            if result is True:
                return f"[OK] {rel_path} (deep match via h5diff)"
            elif result is False or isinstance(result, str):
                return f"[DIFFERENT] {rel_path}\n{result if isinstance(result,str) else ''}"
            else:
                diff_msg = compare_h5(f_local, f_remote)
                if abort_flag.ABORT: return f"[ABORTED] {rel_path}"
                if diff_msg:
                    return f"[DIFFERENT] {rel_path}\n{diff_msg}"
                else:
                    return f"[OK] {rel_path} (deep match via Python)"
        else:
            diff_msg = compare_h5(f_local, f_remote)
            if abort_flag.ABORT: return f"[ABORTED] {rel_path}"
            if diff_msg:
                return f"[DIFFERENT] {rel_path}\n{diff_msg}"
            else:
                return f"[OK] {rel_path} (deep match via Python)"
    except Exception as e:
        return f"[ERROR] {rel_path}: {e}"
