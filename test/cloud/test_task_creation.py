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


def test_create_ccs(filequeue: pytest.fixture) -> None:
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
