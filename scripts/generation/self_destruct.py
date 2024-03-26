"""Generation script for self_destruct tasks."""
from __future__ import annotations

import argparse
from typing import Optional

from taskqueue import TaskQueue
from kombuworker import taskqueueworker as tqw

import synaptor.cloud.task_creation as tc
import synaptor.cloud.parser as parser


def main(
    configfilename: str,
    queueurl: Optional[str] = None,
    queuename: Optional[str] = None,
    workercount: Optional[str] = None,
) -> None:

    iterator = tc.create_self_destruct_tasks(int(workercount))

    queueurl = parser.parse_opt_if_not_passed("queueurl", queueurl, configfilename)
    queuename = parser.parse_opt_if_not_passed("queuename", queuename, configfilename)

    if queueurl.startswith("amqp://"):
        tqw.insert_tasks(queueurl, queuename, iterator)

    else:
        tq = TaskQueue(queueurl)
        tq.insert_all(iterator)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()

    ap.add_argument("configfilename", type=str, help="configuration file")
    ap.add_argument("--queueurl", type=str, default=None, help="queue URL")
    ap.add_argument("--queuename", type=str, default=None, help="queue name (AMQP)")
    ap.add_argument("--workercount", type=str, default=None, help="number of workers to destroy")

    args = ap.parse_args()

    main(args.configfilename, args.queueurl, args.queuename, args.workercount)
