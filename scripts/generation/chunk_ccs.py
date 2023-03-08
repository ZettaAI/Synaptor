"""Task generation script for chunk connected components."""
from __future__ import annotations

from typing import Optional, Generator
from functools import partial

from synaptor import BBox3d
from synaptor.cloud import task_creation as tc
from synaptor.cloud.generator import generator, genparser, add_bbox_arg


@generator(bboxes=True)
def main(
    config: dict, bboxes: Optional[list[BBox3d]] = None
) -> Generator[partial, None, None]:
    return tc.create_connected_component_tasks(
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
        num_merge_tasks=config["nummergetasks"],
        bboxes=bboxes,
        configfilename=config["filename"],
        overlap_seg=config["overlap_seg"],
    )


if __name__ == "__main__":
    add_bbox_arg()

    args = genparser.parse_args()

    main(**vars(args))
