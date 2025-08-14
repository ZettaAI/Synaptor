""" Edge info DataFrame IO for processing tasks """


from sqlalchemy import select

import os
from ... import io
from .. import colnames as cn
from . import filenames as fn


FULL_INFO_COLUMNS = [cn.seg_id, cn.presyn_id, cn.postsyn_id, cn.size,
                     *cn.centroid_cols, *cn.bbox_cols,
                     *cn.presyn_coord_cols, *cn.postsyn_coord_cols,
                     cn.clefthash, cn.partnerhash, cn.presyn_basin, cn.postsyn_basin]


def read_full_info(proc_url):
    """
    Reads the info dataframe with clefts and edges combined
    from a processing directory
    """
    if io.is_db_url(proc_url):
        metadata = io.open_db_metadata(proc_url)

        final = metadata.tables["final"]
        columns = list(final.c[name] for name in FULL_INFO_COLUMNS)
        statement = select(columns)

        return io.read_db_dframe(proc_url, statement, index_col=cn.seg_id)

    else:
        return io.read_dframe(proc_url, fn.final_edgeinfo_fname)


def write_full_info(dframe, proc_url, tag=None):
    """
    Writes the info dataframe with clefts and edges combined
    to a processing directory
    """
    if io.is_db_url(proc_url):
        dframe = dframe.reset_index()
        io.write_db_dframe(dframe, proc_url, "final", index=False)

    else:
        if tag is None:
            io.write_dframe(dframe, proc_url, fn.final_edgeinfo_fname)
        else:
            io.write_dframe(dframe, proc_url,
                            fn.tagged_final_edgeinfo_fname.format(tag))


def pull_all_full_info(storagestr: str, num_merge_tasks: int) -> list[str]:
    """Downloads all of the info dataframe generated from parallel merge tasks."""
    if io.is_db_url(storagestr):
        raise Exception(
            "not implemented for DB io - you can read the full map directly"
        )

    else:
        remote_filenames = [
            os.path.join(storagestr, fn.tagged_final_edgeinfo_fname.format(i))
            for i in range(num_merge_tasks)
        ]

        return io.pull_files(remote_filenames)

def send_full_info(filename: str, storagestr: str) -> None:
    """Sends a duplicate map file to storage."""
    if io.is_db_url(storagestr):
        raise Exception(
            "not implemented for DB io - you can read the full map directly"
        )

    else:
        remote_filename = os.path.join(storagestr, fn.final_edgeinfo_fname)
        io.send_file(filename, remote_filename)
