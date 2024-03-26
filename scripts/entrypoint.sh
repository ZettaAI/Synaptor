#!/bin/bash
# This script is designed to be a general entrypoint for the docker container.
# It will call the scripts in this directory based on the first few arguments
# passed to the container, and route the rest of the arguments to its 'target
# script'. There are 3 possible types of target scripts based on the
# first argument.
# (1) If $1 is a base task name, it will route the remaining arguments to a
# base task script.
# (2) $1 == 'worker' -> worker.py
# (3) $1 == 'generate' -> a generation script.


case $1 in
    # base tasks
    chunk_ccs)        /usr/bin/env python -u base/chunk_ccs.py ${@:2} ;;
    merge_ccs)        /usr/bin/env python -u base/merge_ccs.py ${@:2} ;;
    match_contins)    /usr/bin/env python -u base/match_contins.py ${@:2} ;;
    seg_graph_ccs)    /usr/bin/env python -u base/seg_graph_ccs.py ${@:2} ;;
    chunk_seg_map)    /usr/bin/env python -u base/chunk_seg_map.py ${@:2} ;;
    merge_seginfo)    /usr/bin/env python -u base/merge_seginfo.py ${@:2} ;;
    chunk_edges)      /usr/bin/env python -u base/chunk_edges.py ${@:2} ;;
    merge_edges)      /usr/bin/env python -u base/merge_edges.py ${@:2} ;;
    pick_edge)        /usr/bin/env python -u base/pick_edge.py ${@:2} ;;
    merge_dups)       /usr/bin/env python -u base/merge_dups.py ${@:2} ;;
    remap)            /usr/bin/env python -u base/remap.py ${@:2} ;;
    chunk_overlaps)   /usr/bin/env python -u base/chunk_overlaps.py ${@:2} ;;
    merge_overlaps)   /usr/bin/env python -u base/merge_overlaps.py ${@:2} ;;
    chunk_anchors)    /usr/bin/env python -u base/chunk_anchors.py ${@:2} ;;
    create_index)     /usr/bin/env python -u base/create_index.py ${@:2} ;;
    dedup_chunk_segs) /usr/bin/env python -u base/dedup_chunk_segs.py ${@:2} ;;
    init_db)          /usr/bin/env python -u base/init_db.py ${@:2} ;;
    init_cloudvols)   /usr/bin/env python -u base/init_cloudvols.py ${@:2} ;;
    sanity_check)     /usr/bin/env python -u base/sanity_check.py ${@:2} ;;

    # worker
    worker)           /usr/bin/env python -u worker.py ${@:2} ;;

    # generate - branches again
    generate)
        case $2 in
            chunk_ccs)             /usr/bin/env python -u generation/chunk_ccs.py ${@:3} ;;
            merge_ccs)             /usr/bin/env python -u generation/merge_ccs.py ${@:3} ;;
            match_contins)         /usr/bin/env python -u generation/match_contins.py ${@:3} ;;
            seg_graph_ccs)         /usr/bin/env python -u generation/seg_graph_ccs.py ${@:3} ;;
            chunk_seg_map)         /usr/bin/env python -u generation/chunk_seg_map.py ${@:3} ;;
            merge_seginfo)         /usr/bin/env python -u generation/merge_seginfo.py ${@:3} ;;
            chunk_edges)           /usr/bin/env python -u generation/chunk_edges.py ${@:3} ;;
            merge_edges)           /usr/bin/env python -u generation/merge_edges.py ${@:3} ;;
            pick_edge)             /usr/bin/env python -u generation/pick_edge.py ${@:3} ;;
            merge_dups)            /usr/bin/env python -u generation/merge_dups.py ${@:3} ;;
            merge_dup_maps)        /usr/bin/env python -u generation/merge_dup_maps.py ${@:3} ;;
            remap)                 /usr/bin/env python -u generation/remap.py ${@:3} ;;
            chunk_overlaps)        /usr/bin/env python -u generation/chunk_overlaps.py ${@:3} ;;
            merge_overlaps)        /usr/bin/env python -u generation/merge_overlaps.py ${@:3} ;;
            chunk_anchors)         /usr/bin/env python -u generation/chunk_anchors.py ${@:3} ;;
            create_index)          /usr/bin/env python -u generation/create_index.py ${@:3} ;;
            dedup_chunk_segs)      /usr/bin/env python -u generation/dedup_chunk_segs.py ${@:3} ;;
            init_db)               /usr/bin/env python -u generation/init_db.py ${@:3} ;;
            index_seg_map)         /usr/bin/env python -u generation/index_seg_map.py ${@:3} ;;
            index_chunked_seg_map) /usr/bin/env python -u generation/index_chunked_seg_map.py ${@:3} ;;
            self_destruct)         /usr/bin/env python -u generation/self_destruct.py ${@:3} ;;
            *)  echo "invalid task name: $2"; false
	esac
    ;;

    *)  echo "invalid task name: $1"; false
esac
