#!/usr/bin/env python3

import os, glob
import h5py
import pandas as pd



def save_dframe(dframe, path):
    """ Simple for now """
    dframe.to_csv(path + ".csv", index_label="psd_segid")


def read_dframe(path):
    """ Simple for now """
    return pd.read_csv(path, index_col=0)


def open_h5(fname):
    f = h5py.File(fname)
    return f


def read_h5(fname, dset_name="/main"):
    assert os.path.isfile(fname)
    with h5py.File(fname) as f:
        return f[dset_name].value


def write_h5(data, fname, dset_name="/main", chunk_size=None):

    if os.path.exists(fname):
        os.remove(fname)

    with h5py.File(fname) as f:

        if chunk_size is None:
            f.create_dataset(dset_name, data=data)
        else:
            f.create_dataset(dset_name, data=data, chunks=chunk_size,
                             compression="gzip", compression_opts=4)


def pull_all_files(dirname):
    return glob.glob(os.path.join(dirname, "*"))