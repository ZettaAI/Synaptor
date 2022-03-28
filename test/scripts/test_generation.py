"""Tests for the task generation scripts."""
import os
import importlib
import subprocess
from types import ModuleType

from taskqueue import TaskQueue


TESTCFG = "./test/test.cfg"
GENERATIONDIR = "./scripts/generation"


# Helper functions
def filequeuepath(filequeue: TaskQueue) -> str:
    return f"{filequeue.path.protocol}://{filequeue.path.path}"


def load_source(filename: str, module_name: str = "importedmodule") -> ModuleType:
    """Import a module using its source file."""
    loader = importlib.machinery.SourceFileLoader(module_name, filename)
    module = ModuleType(loader.name)
    loader.exec_module(module)

    return module


def check_main(filename: str, *args, **kwargs) -> None:
    """Runs the main function within a module file to make sure it runs."""
    module = load_source(filename)
    module.main(*args, **kwargs)


def check_cmd(filename: str, *args: list[str]) -> None:
    """Runs a script within a subprocess to make sure that argparsing works."""
    subprocess.check_call(["python", filename, *args])


def check_script(filename: str, filequeue: TaskQueue, rabbitMQurl: str) -> None:
    """Combines the check_main and check_cmd tests using the FileQueue and RabbitMQ."""
    check_main(filename, TESTCFG)
    check_cmd(filename, TESTCFG, "--queueurl", filequeuepath(filequeue))
    check_cmd(filename, TESTCFG, "--queueurl", rabbitMQurl, "--queuename", "synaptor")


# Actual tests
def test_init_db(filequeue, rabbitMQurl):
    filename = os.path.join(GENERATIONDIR, "init_db.py")

    check_script(filename, filequeue, rabbitMQurl)

    filequeue.purge()


def test_chunk_ccs(filequeue, rabbitMQurl):
    filename = os.path.join(GENERATIONDIR, "chunk_ccs.py")

    check_script(filename, filequeue, rabbitMQurl)

    filequeue.purge()


def test_match_contins(filequeue, rabbitMQurl):
    filename = os.path.join(GENERATIONDIR, "match_contins.py")

    check_script(filename, filequeue, rabbitMQurl)

    filequeue.purge()


def test_seg_graph_ccs(filequeue, rabbitMQurl):
    filename = os.path.join(GENERATIONDIR, "seg_graph_ccs.py")

    check_script(filename, filequeue, rabbitMQurl)

    filequeue.purge()


def test_merge_ccs(filequeue, rabbitMQurl):
    filename = os.path.join(GENERATIONDIR, "merge_ccs.py")

    check_script(filename, filequeue, rabbitMQurl)

    filequeue.purge()


def test_index_seg_map(filequeue, rabbitMQurl):
    filename = os.path.join(GENERATIONDIR, "index_seg_map.py")

    check_script(filename, filequeue, rabbitMQurl)

    filequeue.purge()


def test_chunk_seg_map(filequeue, rabbitMQurl):
    filename = os.path.join(GENERATIONDIR, "chunk_seg_map.py")

    check_script(filename, filequeue, rabbitMQurl)

    filequeue.purge()


def test_index_chunked_seg_map(filequeue, rabbitMQurl):
    filename = os.path.join(GENERATIONDIR, "index_chunked_seg_map.py")

    check_script(filename, filequeue, rabbitMQurl)

    filequeue.purge()


def test_merge_seginfo(filequeue, rabbitMQurl):
    filename = os.path.join(GENERATIONDIR, "merge_seginfo.py")

    check_script(filename, filequeue, rabbitMQurl)

    filequeue.purge()


def test_chunk_edges(filequeue, rabbitMQurl):
    filename = os.path.join(GENERATIONDIR, "chunk_edges.py")

    check_script(filename, filequeue, rabbitMQurl)

    filequeue.purge()


def test_pick_edge(filequeue, rabbitMQurl):
    filename = os.path.join(GENERATIONDIR, "pick_edge.py")

    check_script(filename, filequeue, rabbitMQurl)

    filequeue.purge()


def test_merge_dups(filequeue, rabbitMQurl):
    filename = os.path.join(GENERATIONDIR, "merge_dups.py")

    check_script(filename, filequeue, rabbitMQurl)

    filequeue.purge()


def test_merge_dup_maps(filequeue, rabbitMQurl):
    filename = os.path.join(GENERATIONDIR, "merge_dup_maps.py")

    check_script(filename, filequeue, rabbitMQurl)

    filequeue.purge()


def test_remap(filequeue, rabbitMQurl):
    filename = os.path.join(GENERATIONDIR, "remap.py")

    check_script(filename, filequeue, rabbitMQurl)

    filequeue.purge()


def test_self_destruct(filequeue, rabbitMQurl):
    filename = os.path.join(GENERATIONDIR, "self_destruct.py")

    check_script(filename, filequeue, rabbitMQurl)

    filequeue.purge()
