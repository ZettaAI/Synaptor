"""Task generation script for chunk connected components."""
from __future__ import annotations

import os
import argparse
from typing import Optional

from taskqueue import TaskQueue
from kombuworker import taskqueueworker as tqw

import synaptor.cloud.parser as parser
import synaptor.cloud.task_creation as tc
from synaptor import io


def main(configfilename: str, tagfilename: Optional[str] = None) -> None:

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

    if config["queueurl"].startswith("amqp://"):
        queueurl = config["queueurl"]
        queuename = config["queuename"]

        tqw.insert_tasks(queueurl, queuename, iterator)

    else:
        tq = TaskQueue(config["queueurl"])
        tq.insert_all(iterator)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()

    argparser.add_argument("configfilename")
    argparser.add_argument("--tagfilename", default=None)

    args = argparser.parse_args()

    main(args.configfilename, args.tagfilename)
