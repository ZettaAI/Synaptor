import copy
from functools import partial
from typing import Iterable

from cloudvolume.lib import Bbox
from synaptor.proc import tasks_w_io
from synaptor import io, chunk_bboxes


def tup2str(t):
    return " ".join(map(str, t))


def create_init_db_task(storagestr: str) -> partial:
    """Wraps an init_db task in a partial fn."""
    return partial(tasks_w_io.init_db, storagestr)


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
    hashmax: int = 1,
    bboxes: list[Bbox] = None,
) -> Iterable:
    """Returns a generator of partial cc_tasks."""
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
                    hashmax=hashmax,
                    parallel=parallel,
                    mip=resolution,
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
    storagestr: str, storagedir: str, hashmax: int, max_faceshape: tuple[int, int]
) -> Iterable:
    class MatchContinsTaskIterator(object):
        def __init__(self, hashmax):
            self.level_start = 0
            self.level_end = hashmax

        def __len__(self):
            return self.level_end - self.level_start

        def __iter__(self):
            max_faceshape_str = tup2str(max_faceshape)
            for i in range(self.level_start, self.level_end):
                cmd = (
                    f"match_contins {storagestr} {storagedir} {i} "
                    f" --max_face_shape {max_faceshape_str}"
                )

                yield SynaptorTask(cmd)

    return MatchContinsTaskIterator(hashmax)


def create_seg_graph_cc_task(storagestr, hashmax):
    return SynaptorTask(f"seg_graph_ccs {storagestr} {hashmax}")


def create_index_seg_map_task(storagestr):
    return SynaptorTask(f"create_index {storagestr}" " seg_merge_map dst_id_hash")


def create_chunk_seg_map_task(storagestr):
    return SynaptorTask(f"chunk_seg_map {storagestr}")


def create_index_chunked_seg_map_task(storagestr):
    return SynaptorTask(f"create_index {storagestr}" " chunked_seg_merge_map chunk_tag")


def create_merge_seginfo_tasks(
    storagestr, hashmax, aux_storagestr=None, szthresh=None, timingtag=None
):
    class MergeSeginfoTaskIterator(object):
        def __init__(self, storagestr, hashmax, aux_storagestr, szthresh):
            self.level_start = 0
            self.level_end = hashmax
            self.storagestr = storagestr
            self.aux_storagestr = aux_storagestr
            self.szthresh = szthresh

        def __len__(self):
            return self.level_end - self.level_start

        def __getitem__(self, slc):
            itr = copy.deepcopy(self)
            itr.level_start = self.level_start + slc.start
            itr.level_end = self.level_start + slc.stop
            return itr

        def __iter__(self):
            if self.aux_storagestr is None:
                aux_arg = ""
            else:
                aux_arg = f"--aux_storagestr {self.aux_storagestr}"

            if self.szthresh is not None:
                aux_arg += f" --szthresh {self.szthresh}"

            for i in range(self.level_start, self.level_end):
                cmd = f"merge_seginfo {self.storagestr} {i} {aux_arg}"

                yield SynaptorTask(cmd)

    return MergeSeginfoTaskIterator(storagestr, hashmax, aux_storagestr, szthresh)


def create_chunk_edges_tasks(
    imgpath,
    cleftpath,
    segpath,
    storagestr,
    hashmax,
    storagedir,
    volshape,
    chunkshape,
    startcoord,
    patchsz,
    normcloudpath=None,
    resolution=(4, 4, 40),
    aggscratchpath=None,
    aggchunksize=None,
    aggmaxmip=None,
    aggstartcoord=None,
    bboxes=None,
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
            patchsz_str = tup2str(patchsz)
            res_str = tup2str(resolution)

            for bbox in bboxes:
                chunk_begin = tup2str(bbox.min())
                chunk_end = tup2str(bbox.max())

                cmd = (
                    f"chunk_edges {imgpath} {cleftpath} {segpath}"
                    f" {storagestr} {hashmax} --storagedir {storagedir}"
                    f" --chunk_begin {chunk_begin} --chunk_end {chunk_end}"
                    f" --normcloudpath {normcloudpath} "
                    f" --patchsz {patchsz_str} --resolution {res_str}"
                )

                if normcloudpath is not None:
                    cmd += f" --normcloudpath {normcloudpath}"

                if aggscratchpath is not None:
                    aggchunksize_str = tup2str(aggchunksize)
                    aggstartcoord_str = tup2str(aggstartcoord)
                    cmd += (
                        f" --aggscratchpath {aggscratchpath}"
                        f" --aggchunksize {aggchunksize_str}"
                        f" --aggstartcoord {aggstartcoord_str}"
                        f" --aggmaxmip {aggmaxmip}"
                    )

                yield SynaptorTask(cmd)

    return ChunkEdgesTaskIterator()


def create_pick_edge_tasks(storagestr, hashmax):
    class PickEdgeTaskIterator(object):
        def __init__(self, storagestr, hashmax):
            self.level_start = 0
            self.level_end = hashmax
            self.storagestr = storagestr

        def __len__(self):
            return self.level_end - self.level_start

        def __getitem__(self, slc):
            itr = copy.deepcopy(self)
            itr.level_start = self.level_start + slc.start
            itr.level_end = self.level_start + slc.stop
            return itr

        def __iter__(self):
            for i in range(self.level_start, self.level_end):
                cmd = f"pick_edge {self.storagestr} {i}"

                yield SynaptorTask(cmd)

    return PickEdgeTaskIterator(storagestr, hashmax)


def create_merge_dup_tasks(
    storagestr,
    hashmax,
    dist_thresh,
    size_thresh,
    resolution=(4, 4, 40),
    output_storagestr=None,
):

    output_storagestr = storagestr if output_storagestr is None else output_storagestr

    class MergeDupsTaskIterator(object):
        def __init__(self, storagestr, hashmax):
            self.level_start = 0
            self.level_end = hashmax
            self.storagestr = storagestr

        def __len__(self):
            return self.level_end - self.level_start

        def __getitem__(self, slc):
            itr = copy.deepcopy(self)
            itr.level_start = self.level_start + slc.start
            itr.level_end = self.level_start + slc.stop
            return itr

        def __iter__(self):
            res_str = tup2str(resolution)
            for i in range(self.level_start, self.level_end):
                cmd = (
                    f"merge_dups {self.storagestr} {i} {dist_thresh}"
                    f" {size_thresh} --voxel_res {res_str}"
                    f" --dst_storagestr {output_storagestr}"
                )

                yield SynaptorTask(cmd)

    return MergeDupsTaskIterator(storagestr, hashmax)


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
    """Returns a generator of partial remap_ids_tasks."""
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
                    storagestr=storagestr,
                    chunk_begin=chunk_begin,
                    chunk_end=chunk_end,
                    dup_map_storagestr=dup_map_storagestr,
                    mip=resolution,
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
