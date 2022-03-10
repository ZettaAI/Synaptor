"""Cloud worker script.

Accepts tasks from a queue until it receives a kill task signal.
"""
import argparse
from taskqueue import TaskQueue

import synaptor.proc.io.tasks_w_io  # "Registers" tasks for taskqueue


parser = argparse.ArgumentParser()

parser.add_argument("qurl", type=str)
parser.add_argument("lease_seconds", type=int, default=300)

args = parser.parse_args()
with TaskQueue(qurl=args.qurl, n_threads=0) as tq:
    tq.poll(lease_seconds=args.lease_seconds)
