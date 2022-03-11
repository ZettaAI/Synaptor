"""Cloud worker script.

Accepts tasks from a queue until it receives a kill task signal.
"""
import argparse
from taskqueue import TaskQueue

import synaptor.proc.io.tasks_w_io  # "Registers" tasks for taskqueue
from synaptor.cloud import parser


def main(queueurl, config, lease_seconds):

    if config is not None:
        queueurl = parser.parse(configfilename)["queueurl"]
    elif queueurl is not None:
        pass
    else:
        raise Exception("Need to define queueurl or configfilename")

    with TaskQueue(qurl=queueurl, n_threads=0) as tq:
        tq.poll(lease_seconds=lease_seconds)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()

    ap.add_argument("--queueurl", type=str, default=None, help="queue URL")
    ap.add_argument("--config", type=str, default=None, help="configuration file")
    ap.add_argument("--lease_seconds", type=int, default=300)

    args = ap.parse_args()

    main(**vars(args))
