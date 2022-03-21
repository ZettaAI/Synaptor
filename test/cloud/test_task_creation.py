"""Tests for synaptor.cloud.task_creation."""
from typing import Iterable
from functools import partial

import pytest
from taskqueue import TaskQueue

from synaptor.cloud import task_creation


def run_insertion_test(it: Iterable, queue: TaskQueue) -> None:
    """Tests whether the tasks within an iterable can be inserted into a queue."""
    queue.insert_all(it)

    # cleaning up for other tests
    queue.purge()


def test_create_init_db(filequeue):
    """Checks whether create_init_db_task runs."""
    task = task_creation.create_init_db_task("storagestr")

    assert isinstance(task, partial)

    run_insertion_test([task], filequeue)


def test_create_ccs(filequeue):
    """Checks whether create_connected_components_tasks runs."""
    it = task_creation.create_connected_component_tasks(
        "descpath",
        "outpath",
        "storagestr",
        "storagedir",
        0.1,  # ccthresh
        1,  # szthresh
        (2, 2, 2),  # volshape
        (1, 1, 1),  # chunkshape
        (0, 0, 0),  # startcoord
    )

    assert isinstance(next(iter(it)), partial)
    assert len(it) == 8

    run_insertion_test(it, filequeue)


def test_create_merge_ccs(filequeue):
    """Checks whether create_merge_ccs_task runs."""
    task = task_creation.create_merge_ccs_task(
        "storagestr", "storagedir", (1, 1),  # max_face_shape
    )

    assert isinstance(task, partial)

    run_insertion_test([task], filequeue)


def test_create_match_contins(filequeue):
    """Checks whether create_match_contins_tasks runs."""
    it = task_creation.create_match_contins_tasks(
        "storagestr", "storagedir", 10, (100, 100),  # num_merge_tasks  # max_face_shape
    )

    assert isinstance(next(iter(it)), partial)
    assert len(it) == 10

    run_insertion_test(it, filequeue)


def test_create_seg_graph_cc(filequeue):
    """Checks whether create_seg_graph_cc_task runs."""
    task = task_creation.create_seg_graph_cc_task("storagestr", 10,)  # num_merge_tasks

    assert isinstance(task, partial)

    run_insertion_test([task], filequeue)


def test_create_index_seg_map(filequeue):
    """Checks whether create_index_seg_map_task runs."""
    task = task_creation.create_index_seg_map_task("storagestr")

    assert isinstance(task, partial)

    run_insertion_test([task], filequeue)


def test_create_chunk_seg_map(filequeue):
    """Checks whether create_chunk_seg_map_task runs."""
    task = task_creation.create_chunk_seg_map_task("storagestr")

    assert isinstance(task, partial)

    run_insertion_test([task], filequeue)


def test_create_chunk_seg_map(filequeue):
    """Checks whether create_index_seg_map runs."""
    task = task_creation.create_chunk_seg_map_task("storagestr")

    assert isinstance(task, partial)

    run_insertion_test([task], filequeue)


def test_create_index_chunked_seg_map(filequeue):
    """Checks whether create_index_seg_map runs."""
    task = task_creation.create_index_chunked_seg_map_task("storagestr")

    assert isinstance(task, partial)

    run_insertion_test([task], filequeue)


def test_create_merge_seginfo(filequeue):
    """Checks whether create_remap_tasks runs."""
    it = task_creation.create_merge_seginfo_tasks(
        "storagestr", 10, "aux_storagestr", 100,  # num_merge_tasks  # szthresh
    )

    assert isinstance(next(iter(it)), partial)
    assert len(it) == 10

    run_insertion_test(it, filequeue)


def test_create_chunk_edges(filequeue):
    """Checks whether create_chunk_edges_tasks runs."""
    it = task_creation.create_chunk_edges_tasks(
        "imgpath",
        "cleftpath",
        "segpath",
        "storagestr",
        10,  # num_merge_tasks
        "storagedir",
        (2, 2, 2),  # volshape
        (1, 1, 1),  # chunkshape
        (0, 0, 0),  # startcoord
        (1, 1, 1),  # patchsz
    )

    assert isinstance(next(iter(it)), partial)
    assert len(it) == 8

    run_insertion_test(it, filequeue)


def test_create_pick_edge(filequeue):
    """Checks whether create_pick_edge_tasks runs."""
    it = task_creation.create_pick_edge_tasks("storagestr", 10,)  # num_merge_tasks

    assert isinstance(next(iter(it)), partial)
    assert len(it) == 10

    run_insertion_test(it, filequeue)


def test_create_merge_dups(filequeue):
    """Checks whether create_self_destruct_tasks runs."""
    it = task_creation.create_merge_dups_tasks(
        "storagestr",
        10,  # num_merge_tasks
        100.0,  # dist_thresh
        100,  # size_thresh
        (1, 1, 1),  # resolution
        "output_storagestr",
    )

    assert isinstance(next(iter(it)), partial)
    assert len(it) == 10

    run_insertion_test(it, filequeue)


def test_create_remap(filequeue):
    """Checks whether create_remap_tasks runs."""
    it = task_creation.create_remap_tasks(
        "seg_in_path",
        "seg_out_path",
        "storagestr",
        (2, 2, 2),  # volshape
        (1, 1, 1),  # chunkshape
        (0, 0, 0),  # startcoord
    )

    assert isinstance(next(iter(it)), partial)
    assert len(it) == 8

    run_insertion_test(it, filequeue)


def test_create_self_destruct(filequeue):
    """Checks whether create_self_destruct_tasks runs."""
    it = task_creation.create_self_destruct_tasks(10)

    assert isinstance(next(iter(it)), partial)
    assert len(it) == 10

    run_insertion_test(it, filequeue)
