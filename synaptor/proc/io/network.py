""" PyTorch Neural Network Model IO for processing tasks """


import os

from ... import io
from . import filenames as fn
from functools import cache


@cache
def read_network_from_proc(proc_dir_path, modelpath=None):
    if modelpath is None:
        model_fname = os.path.join(proc_dir_path,
                                   fn.network_dirname, fn.network_fname)
        chkpt_fname = os.path.join(proc_dir_path,
                                   fn.network_dirname, fn.network_chkpt)

        return io.read_network(model_fname, chkpt_fname)

    else:  # external path
        if modelpath.endswith(".py"):
            model_fname = modelpath
            chkpt_fname = modelpath.replace(".py", ".chkpt")

            return io.read_network(model_fname, chkpt_fname)

        elif modelpath.endswith(".onnx"):
            return io.read_network(modelpath)

        else:  # assume a directory with model.py & model.chkpt
            model_fname = os.path.join(modelpath, fn.network_fname)
            chkpt_fname = os.path.join(modelpath, fn.network_chkpt)

            return io.read_network(model_fname, chkpt_fname)


def write_network_to_proc(net_fname, chkpt_fname, proc_dir_path):

    dest_net_fname = os.path.join(proc_dir_path,
                                  fn.network_dirname, fn.network_fname)
    dest_chkpt_fname = os.path.join(proc_dir_path,
                                    fn.network_dirname, fn.network_chkpt)

    io.send_file(net_fname, dest_net_fname)
    io.send_file(chkpt_fname, dest_chkpt_fname)
