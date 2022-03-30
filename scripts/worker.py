"""Cloud worker script.

Accepts tasks from a queue until it receives a kill task signal.
"""
from __future__ import annotations

import argparse
from typing import Optional

from taskqueue import TaskQueue
from kombuworker import taskqueueworker as tqw

# Registers tasks for taskqueue
import synaptor.proc.tasks_w_io  # noqa
from synaptor.cloud import parser
from synaptor.cloud import boto


def main(
    configfilename: Optional[str] = None,
    queueurl: Optional[str] = None,
    queuename: Optional[str] = None,
    lease_seconds: int = 300,
) -> None:
    queueurl = parser.parse_opt_if_not_passed("queueurl", queueurl, configfilename)

    if queueurl.startswith("amqp://"):
        # also need a queue name within the amqp server
        queuename = parser.parse_opt_if_not_passed(
            "queuename", queuename, configfilename
        )

        print("Starting polling")
        tqw.poll(queueurl, queuename, max_num_retries=10_000, verbose=True)

    else:
        with TaskQueue(qurl=queueurl, n_threads=0) as tq:
            print("Starting polling")
            tq.poll(lease_seconds=lease_seconds)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()

    ap.add_argument("--queueurl", type=str, default=None, help="queue URL")
    ap.add_argument("--queuename", type=str, default=None, help="queue name (AMQP)")
    ap.add_argument(
        "--configfilename", type=str, default=None, help="configuration file"
    )
    ap.add_argument("--lease_seconds", type=int, default=300)

    args = ap.parse_args()

    if not boto.gcloud_configured():
        boto.writeboto()

    main(**vars(args))
