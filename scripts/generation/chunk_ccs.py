"""Task generation script for chunk connected components."""
from __future__ import annotations

import argparse
from typing import Optional

from taskqueue import TaskQueue
from kombuworker import taskqueueworker as tqw

import synaptor.cloud.parser as parser
import synaptor.cloud.task_creation as tc
from synaptor import io


def main(
    configfilename: str,
    queueurl: Optional[str] = None,
    queuename: Optional[str] = None,
    tagfilename: Optional[str] = None,
) -> None:

    config = parser.parse(configfilename)

    if tagfilename is not None:
        bboxes = io.utils.read_bbox_tag_filename(tagfilename)
    else:
        bboxes = None

    iterator = tc.create_connected_component_tasks(
        config["descriptor"],
        config["tempoutput"],
        storagestr=config["storagestrs"][0],
        storagedir=config["storagestrs"][1],
        ccthresh=config["ccthresh"],
        szthresh=config["dustthresh"],
        volshape=config["volshape"],
        chunkshape=config["chunkshape"],
        startcoord=config["startcoord"],
        resolution=config["voxelres"],
        hashmax=config["nummergetasks"],
        bboxes=bboxes,
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
    ap.add_argument("--tagfilename", default=None)

    args = ap.parse_args()

    main(**vars(args))
