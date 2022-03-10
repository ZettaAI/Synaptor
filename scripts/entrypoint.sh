#!/bin/bash
# This script is designed to be a general entrypoint for the docker container.
# It will call the scripts in this directory based on the first few arguments
# passed to the container, and route the rest of the arguments to its 'target
# script'. There are 4 possible types of target scripts based on the
# first argument.
# (1) If $1 is a base task name, it will route the remaining arguments to a
# base task script.
# (2) $1 == 'worker' -> worker.py
# (3) $1 == 'generate' -> a generation script.
# (4) $1 == 'sanity_check' -> sanity_check.py 

case $1 in
    # base tasks
    chunk_ccs)        python3 -u chunk_ccs.py ${@:2} ;;
    merge_ccs)        python3 -u merge_ccs.py ${@:2} ;;
    match_contins)    python3 -u match_contins.py ${@:2} ;;
    seg_graph_ccs)    python3 -u seg_graph_ccs.py ${@:2} ;;
    chunk_seg_map)    python3 -u chunk_seg_map.py ${@:2} ;;
    merge_seginfo)    python3 -u merge_seginfo.py ${@:2} ;;
    chunk_edges)      python3 -u chunk_edges.py ${@:2} ;;
    pick_edge)        python3 -u pick_edge.py ${@:2} ;;
    merge_dups)       python3 -u merge_dups.py ${@:2} ;;
    remap_ids)        python3 -u remap_ids.py ${@:2} ;;
    chunk_overlaps)   python3 -u chunk_overlaps.py ${@:2} ;;
    merge_overlaps)   python3 -u merge_overlaps.py ${@:2} ;;
    chunk_anchors)    python3 -u chunk_anchors.py ${@:2} ;;
    create_index)     python3 -u create_index.py ${@:2} ;;
    dedup_chunk_segs) python3 -u dedup_chunk_segs.py ${@:2} ;;
    init_db)          python3 -u init_db.py ${@:2} ;;

    # worker
    worker)           python3 -u worker.py ${@:2} ;;

    # sanity_check
    sanity_check)     python3 -u sanity_check.py ${@:2} ;;

    # generate - branches again
    generate)
        case $2 in
            chunk_ccs)        python3 -u generation/chunk_ccs.py ${@:2} ;;
            merge_ccs)        python3 -u generation/merge_ccs.py ${@:2} ;;
            match_contins)    python3 -u generation/match_contins.py ${@:2} ;;
            seg_graph_ccs)    python3 -u generation/seg_graph_ccs.py ${@:2} ;;
            chunk_seg_map)    python3 -u generation/chunk_seg_map.py ${@:2} ;;
            merge_seginfo)    python3 -u generation/merge_seginfo.py ${@:2} ;;
            chunk_edges)      python3 -u generation/chunk_edges.py ${@:2} ;;
            pick_edge)        python3 -u generation/pick_edge.py ${@:2} ;;
            merge_dups)       python3 -u generation/merge_dups.py ${@:2} ;;
            remap_ids)        python3 -u generation/remap_ids.py ${@:2} ;;
            chunk_overlaps)   python3 -u generation/chunk_overlaps.py ${@:2} ;;
            merge_overlaps)   python3 -u generation/merge_overlaps.py ${@:2} ;;
            chunk_anchors)    python3 -u generation/chunk_anchors.py ${@:2} ;;
            create_index)     python3 -u generation/create_index.py ${@:2} ;;
            dedup_chunk_segs) python3 -u generation/dedup_chunk_segs.py ${@:2} ;;
            init_db)          python3 -u generation/init_db.py ${@:2} ;;
            self_destruct)    python3 -u generation/self_destruct.py ${@:2} ;;
            *)  echo "invalid task name: $2"; false
	esac
    ;;

    *)  echo "invalid task name: $1"; false
esac
