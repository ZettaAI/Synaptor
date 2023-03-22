import os
import glob
import shutil

import pytest
from synaptor.io.backends import gcloud


@pytest.fixture
def dummy_dirs():
    src = "test/io/backends/gcloud_src"
    dst = "test/io/backends/gcloud_dst"


    os.makedirs(src, exist_ok=True)
    os.makedirs(dst, exist_ok=True)

    # Making dummy files
    for i in range(10):
        with open(os.path.join(src, str(i)), "w") as f:
            pass

    yield src, dst

    shutil.rmtree(src)
    shutil.rmtree(dst)


def test_pull_files_in_batches(dummy_dirs):
    src, dst = dummy_dirs

    srcfiles = glob.glob(os.path.join(src, "*"))
    gcloud.pull_files_in_batches(srcfiles, dst, batch_size=1)

    src_basenames = [os.path.basename(f) for f in srcfiles]

    assert all(os.path.exists(os.path.join(dst, b)) for b in src_basenames)
