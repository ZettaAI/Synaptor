"""Task generation script to index a segmentation id map."""
from __future__ import annotations

from functools import partial
from configparser import ConfigParser

from synaptor.cloud import task_creation as tc
from synaptor.cloud.generator import generator, genparser


@generator()
def main(config: ConfigParser) -> partial:
    return tc.create_index_seg_map_task(config["storagestrs"][0])


if __name__ == "__main__":
    args = genparser.parse_args()

    main(args.configfilename)
