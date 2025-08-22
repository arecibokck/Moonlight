# H5Compare/utils.py
import hashlib
import os
import subprocess
import h5py
import numpy as np
from .config import HASH_ALGO, RTOL, ATOL, USE_H5DIFF

def file_hash(path, algo=HASH_ALGO, block_size=4*1024*1024):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        while chunk := f.read(block_size):
            h.update(chunk)
    return h.hexdigest()

def run_h5diff(file1, file2):
    try:
        result = subprocess.run(["h5diff", file1, file2], capture_output=True, text=True)
        if result.returncode == 0:
            return True
        else:
            return f"[DIFF] {file1} vs {file2}\n{result.stdout}{result.stderr}"
    except FileNotFoundError:
        return None

def compare_h5(file1, file2, rtol=RTOL, atol=ATOL):
    with h5py.File(file1, 'r') as f1, h5py.File(file2, 'r') as f2:
        def compare_groups(g1, g2, path=""):
            for key in g1.keys():
                if key not in g2:
                    return f"Missing in {file2}: {path}/{key}"
                if isinstance(g1[key], h5py.Dataset):
                    d1, d2 = g1[key][()], g2[key][()]
                    if not np.allclose(d1, d2, rtol=rtol, atol=atol, equal_nan=True):
                        return f"Dataset differs: {path}/{key}"
                else:
                    msg = compare_groups(g1[key], g2[key], path + "/" + key)
                    if msg:
                        return msg
            for key in g2.keys():
                if key not in g1:
                    return f"Extra in {file2}: {path}/{key}"
            return None
        return compare_groups(f1, f2)

def collect_h5_files(root):
    h5_files = {}
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if f.endswith(".h5"):
                rel_path = os.path.relpath(os.path.join(dirpath, f), root)
                h5_files[rel_path] = os.path.join(dirpath, f)
    return h5_files
