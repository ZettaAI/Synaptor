"""Tests for synaptor.proc.tasks_w_io."""
import os
from functools import partial

import pytest

from synaptor.proc import tasks_w_io
from synaptor.proc import io as taskio
from synaptor.proc.io import filenames as fn


TEST_STORAGEDIR = "./test/test_storagedir"
NUM_DUMMY_MAPS = 5


@pytest.fixture
def dummy_dup_maps():
    """Writes a set of dup maps to disk.

    Returns the storagedir, the num maps written, and the total number of entries
    across all maps.
    """
    filenames = list()
    os.makedirs(TEST_STORAGEDIR, exist_ok=True)
    for i in range(NUM_DUMMY_MAPS):
        dummy_dup_map = {2*i: 2*i, 2*i+1: 2*i}

        basename = fn.tagged_dup_fname.format(i=i)
        taskio.write_dup_id_map(dummy_dup_map, TEST_STORAGEDIR, i)
        filenames.append(os.path.join(TEST_STORAGEDIR, basename))

    yield TEST_STORAGEDIR, NUM_DUMMY_MAPS, NUM_DUMMY_MAPS * 2

    for f in filenames:
        os.remove(f)
    os.rmdir(TEST_STORAGEDIR)


def test_merge_dup_maps_task(dummy_dup_maps):
    """Tests whether the merge_dup_maps task gives the correct # entries."""
    storagedir, num_merge_tasks, total_entries = dummy_dup_maps

    tasks_w_io.merge_dup_maps_task(storagedir, num_merge_tasks)

    dup_map = taskio.read_dup_id_map(storagedir)

    assert len(dup_map) == total_entries

    os.remove(os.path.join(storagedir, fn.dup_map_fname))


def test_self_destruct(filequeue):
    """Tests whether the self_destruct task actually exits the poll."""
    task = partial(tasks_w_io.self_destruct)

    filequeue.insert(task)

    filequeue.poll(lease_seconds=10)
    filequeue.purge()
