# h5compare/logger.py
from queue import Queue

def log_writer(queue: Queue, report_file: str):
    with open(report_file, "a", encoding="utf-8") as f:
        while True:
            msg = queue.get()
            if msg == "__DONE__":
                break
            print(msg, flush=True)
            f.write(msg + "\n")
            queue.task_done()
