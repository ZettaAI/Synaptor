from __future__ import annotations

import copy
from functools import partial
from typing import Iterable, Generator, Optional

from cloudvolume.lib import Bbox
from synaptor.proc import tasks_w_io, io as procio
from synaptor import io, chunk_bboxes


def tup2str(t):
    return " ".join(map(str, t))


def create_init_db_task(storagestr: str) -> partial:
    """Wraps an init_db task in a partial fn."""
    return partial(procio.init_db, storagestr)


def create_connected_component_tasks(
    descpath: str,
    outpath: str,
    storagestr: str,
    storagedir: str,
    ccthresh: float,
    szthresh: int,
    volshape: tuple[int, int, int],
    chunkshape: tuple[int, int, int],
    startcoord: tuple[int, int, int],
    resolution: tuple[int, int, int] = (8, 8, 40),
    parallel: int = 1,
    num_merge_tasks: int = 1,
    bboxes: list[Bbox] = None,
) -> Iterable:
    """Returns a iterator of partial cc_tasks."""
    print(bboxes)
    if bboxes is None:
        bboxes = chunk_bboxes(volshape, chunkshape, offset=startcoord)

    class ConnectedComponentsTaskIterator(object):
        def __init__(self):
            pass

        def __len__(self):
            return len(bboxes)

        def __iter__(self):
            for bbox in bboxes:
                chunk_begin = tuple(bbox.min())
                chunk_end = tuple(bbox.max())

                yield partial(
                    tasks_w_io.cc_task,
                    descpath,
                    outpath,
                    storagestr,
                    ccthresh,
                    szthresh,
                    chunk_begin=chunk_begin,
                    chunk_end=chunk_end,
                    num_merge_tasks=num_merge_tasks,
                    parallel=parallel,
                    resolution=resolution,
                    storagedir=storagedir,
                )

    return ConnectedComponentsTaskIterator()


def create_merge_ccs_task(
    storagestr: str, size_thr: int, max_face_shape: tuple[int, int],
) -> partial:
    """Wraps a merge_ccs task in a partial fn."""
    return partial(
        tasks_w_io.merge_ccs_task, storagestr, size_thr, max_face_shape=max_face_shape
    )


def create_match_contins_tasks(
    storagestr: str,
    storagedir: str,
    num_merge_tasks: int,
    max_face_shape: tuple[int, int],
) -> Iterable:
    class MatchContinsTaskIterator(object):
        def __init__(self):
            pass

        def __len__(self):
            return num_merge_tasks

        def __iter__(self):
            for i in range(num_merge_tasks):
                yield partial(
                    tasks_w_io.match_continuations_task,
                    storagestr,
                    storagedir,
                    i,
                    max_face_shape,
                )

    return MatchContinsTaskIterator()


def create_seg_graph_cc_task(storagestr: str, num_merge_tasks: int) -> partial:
    return partial(tasks_w_io.seg_graph_cc_task, storagestr, num_merge_tasks)


def create_index_seg_map_task(storagestr: str) -> partial:
    return partial(io.create_index, storagestr, "seg_merge_map", "dst_id_hash")


def create_chunk_seg_map_task(storagestr: str) -> partial:
    return partial(tasks_w_io.chunk_seg_merge_map, storagestr)


def create_index_chunked_seg_map_task(storagestr: str) -> partial:
    return partial(io.create_index, storagestr, "chunked_seg_merge_map", "chunk_tag")


def create_merge_seginfo_tasks(
    storagestr: str,
    num_merge_tasks: int,
    aux_storagestr: Optional[str] = None,
    szthresh: Optional[int] = None,
) -> Generator[partial, None, None]:
    class MergeSeginfoTaskIterator(object):
        def __init__(self):
            pass

        def __len__(self):
            return num_merge_tasks

        def __iter__(self):
            for i in range(num_merge_tasks):
                yield partial(
                    tasks_w_io.merge_seginfo_task,
                    storagestr,
                    i,
                    szthresh=szthresh,
                    aux_storagestr=aux_storagestr,
                )

    return MergeSeginfoTaskIterator()


def create_chunk_edges_tasks(
    imgpath: str,
    cleftpath: str,
    segpath: str,
    storagestr: str,
    num_merge_tasks: int,
    volshape: tuple[int, int, int],
    chunkshape: tuple[int, int, int],
    startcoord: tuple[int, int, int],
    patchsz: tuple[int, int, int,],
    storagedir: Optional[str] = None,
    resolution: Optional[tuple[int, int, int]] = (4, 4, 40),
    normcloudpath: Optional[str] = None,
    aggscratchpath: Optional[str] = None,
    aggchunksize: Optional[tuple[int, int, int]] = None,
    aggstartcoord: Optional[tuple[int, int, int]] = None,
    aggmaxmip: Optional[int] = 11,
    bboxes: Optional[list[Bbox]] = None,
):
    """ Only passing the required arguments for now """

    if bboxes is None:
        bboxes = chunk_bboxes(volshape, chunkshape, offset=startcoord)

    class ChunkEdgesTaskIterator(object):
        def __init__(self):
            pass

        def __len__(self):
            return len(bboxes)

        def __iter__(self):
            for bbox in bboxes:
                chunk_begin = tuple(bbox.min())
                chunk_end = tuple(bbox.max())

                yield partial(
                    tasks_w_io.edge_task,
                    imgpath,
                    cleftpath,
                    segpath,
                    chunk_begin,
                    chunk_end,
                    patchsz,
                    storagestr,
                    storagedir=storagedir,
                    resolution=resolution,
                    normcloudpath=normcloudpath,
                    aggscratchpath=aggscratchpath,
                    aggchunksize=aggchunksize,
                    aggmaxmip=aggmaxmip,
                    aggstartcoord=aggstartcoord,
                    num_merge_tasks=num_merge_tasks,
                )

    return ChunkEdgesTaskIterator()


def create_pick_edge_tasks(
    storagestr: str, num_merge_tasks: int
) -> Generator[partial, None, None]:
    class PickEdgeTaskIterator(object):
        def __init__(self):
            pass

        def __len__(self):
            return num_merge_tasks

        def __iter__(self):
            for i in range(num_merge_tasks):
                yield partial(tasks_w_io.pick_largest_edges_task, storagestr, i)

    return PickEdgeTaskIterator()


def create_merge_dups_tasks(
    storagestr: str,
    num_merge_tasks: int,
    dist_thresh: float,
    size_thresh: int,
    resolution: tuple[int, int, int] = (4, 4, 40),
    output_storagestr: str = None,
) -> Generator[partial, None, None]:

    output_storagestr = storagestr if output_storagestr is None else output_storagestr

    class MergeDupsTaskIterator(object):
        def __init__(self):
            pass

        def __len__(self):
            return num_merge_tasks

        def __iter__(self):
            for i in range(num_merge_tasks):
                yield partial(
                    tasks_w_io.merge_duplicates_task,
                    resolution,
                    dist_thresh,
                    size_thresh,
                    storagestr,
                    i,
                )

    return MergeDupsTaskIterator()


def create_remap_tasks(
    seg_in_path: str,
    seg_out_path: str,
    storagestr: str,
    volshape: tuple[int, int, int],
    chunkshape: tuple[int, int, int],
    startcoord: tuple[int, int, int],
    dup_map_storagestr: str = None,
    resolution: tuple[int, int, int] = (8, 8, 40),
    parallel: int = 1,
) -> Iterable:
    """Returns a iterator of partial remap_ids_tasks."""
    dup_map_storagestr = (
        storagestr if dup_map_storagestr is None else dup_map_storagestr
    )

    bboxes = chunk_bboxes(volshape, chunkshape, offset=startcoord)

    class RemapTaskIterator(object):
        def __init__(self):
            pass

        def __len__(self):
            return len(bboxes)

        def __iter__(self):
            for bbox in bboxes:
                chunk_begin = tuple(bbox.min())
                chunk_end = tuple(bbox.max())

                yield partial(
                    tasks_w_io.remap_ids_task,
                    seg_in_path,
                    seg_out_path,
                    chunk_begin=chunk_begin,
                    chunk_end=chunk_end,
                    storagestr=storagestr,
                    dup_map_storagestr=dup_map_storagestr,
                    resolution=resolution,
                )

    return RemapTaskIterator()


def create_overlap_tasks(
    segpath,
    base_segpath,
    storagestr,
    volshape,
    chunkshape,
    startcoord,
    resolution=(8, 8, 40),
    parallel=1,
):

    bboxes = chunk_bboxes(volshape, chunkshape, offset=startcoord)

    class OverlapTaskIterator(object):
        def __init__(self):
            pass

        def __len__(self):
            return len(bboxes)

        def __iter__(self):
            for bbox in bboxes:
                chunk_begin = tup2str(bbox.min())
                chunk_end = tup2str(bbox.max())
                res_str = tup2str(resolution)

                cmd = (
                    f"chunk_overlaps {segpath} {base_segpath} {storagestr}"
                    f" --chunk_begin {chunk_begin} --chunk_end {chunk_end}"
                    f" --parallel {parallel} --mip {res_str}"
                )

                yield SynaptorTask(cmd)

    return OverlapTaskIterator()


def create_merge_overlaps_task(storagestr):
    return SynaptorTask(f"merge_overlaps {storagestr}")


def create_cloudvols(
    output_path, temp_output_path, voxelres, vol_shape, startcoord, block_shape
):

    io.init_seg_volume(
        output_path,
        voxelres,
        vol_shape,
        "",
        [],
        offset=startcoord,
        chunk_size=block_shape,
    )

    if temp_output_path != output_path:
        io.init_seg_volume(
            temp_output_path,
            voxelres,
            vol_shape,
            "",
            [],
            offset=startcoord,
            chunk_size=block_shape,
        )


def create_self_destruct_tasks(numworkers: int) -> Iterable:
    """Returns an iterator of self_destruct tasks."""

    class SelfDestructIterator:
        def __init__(self):
            pass

        def __len__(self):
            return numworkers

        def __iter__(self):
            for i in range(numworkers):
                yield partial(tasks_w_io.self_destruct)

    return SelfDestructIterator()
