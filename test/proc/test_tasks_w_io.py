"""Tests for synaptor.proc.tasks_w_io."""
from functools import partial

import pytest

from synaptor.proc import tasks_w_io


def test_self_destruct(filequeue):
    """Tests whether the self_destruct task actually exits the poll."""
    task = partial(tasks_w_io.self_destruct)

    filequeue.insert(task)

    filequeue.poll(lease_seconds=10)
    filequeue.purge()
