"""Task generation script for remapping tasks."""
from __future__ import annotations

import argparse
from typing import Optional

from taskqueue import TaskQueue
from kombuworker import taskqueueworker as tqw

import synaptor.cloud.task_creation as tc
from synaptor.cloud.generator import generator, genparser


@generator()
def main(config: dict) -> Generator[partial, None, None]:
    return tc.create_remap_tasks(
        config["tempoutput"],
        config["output"],
        storagestr=config["storagestrs"][0],
        volshape=config["volshape"],
        chunkshape=config["chunkshape"],
        startcoord=config["startcoord"],
        dup_map_storagestr=config["storagestrs"][1],
        resolution=config["voxelres"],
        configfilename=config["filename"],
    )


if __name__ == "__main__":
    args = genparser.parse_args()

    main(**vars(args))
