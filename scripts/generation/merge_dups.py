"""Task generation script for merging duplicate edges across chunks."""
from __future__ import annotations

import argparse
from typing import Optional

from taskqueue import TaskQueue
from kombuworker import taskqueueworker as tqw

from synaptor.cloud import task_creation as tc
from synaptor.cloud.generator import generator, genparser


@generator()
def main(config: ConfigParser) -> Generator[partial, None, None]:
    return tc.create_merge_dups_tasks(
        config["storagestrs"][0],
        config["nummergetasks"],
        config["mergethresh"],
        config["szthresh"],
        config["voxelres"],
        output_storagestr=config["storagestrs"][1],
    )


if __name__ == "__main__":
    args = genparser.parse_args()

    main(**vars(args))
