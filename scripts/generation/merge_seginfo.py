"""Task generation script for remapping tasks."""
from __future__ import annotations

import argparse
from typing import Optional

from taskqueue import TaskQueue
from kombuworker import taskqueueworker as tqw

import synaptor.cloud.parser as parser
import synaptor.cloud.task_creation as tc


def main(
    configfilename: str,
    queueurl: Optional[str] = None,
    queuename: Optional[str] = None,
) -> None:

    config = parser.parse(configfilename)

    enforce_szthresh = config["workflowtype"] == "Segmentation"
    szthresh = config["szthresh"] if enforce_szthresh else None

    iterator = tc.create_merge_seginfo_tasks(
        config["storagestrs"][0],
        config["nummergetasks"],
        aux_storagestr=config["storagestrs"][1],
        szthresh=szthresh,
    )

    queueurl = parser.parse_opt_if_not_passed("queueurl", queueurl, configfilename)
    queuename = parser.parse_opt_if_not_passed("queuename", queuename, configfilename)

    if queueurl.startswith("amqp://"):
        tqw.insert_tasks(queueurl, queuename, iterator)

    else:
        tq = TaskQueue(queueurl)
        tq.insert_all(iterator)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()

    ap.add_argument("configfilename", type=str, help="Path to the configuration file")
    ap.add_argument("--queueurl", type=str, default=None, help="queue URL")
    ap.add_argument("--queuename", type=str, default=None, help="queue name (AMQP)")

    args = ap.parse_args()

    main(**vars(args))
