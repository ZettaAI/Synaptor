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
    chunk_ccs)        echo chunk_ccs.py ${@:2} ;;
    merge_ccs)        echo merge_ccs.py ${@:2} ;;
    match_contins)    echo match_contins.py ${@:2} ;;
    seg_graph_ccs)    echo seg_graph_ccs.py ${@:2} ;;
    chunk_seg_map)    echo chunk_seg_map.py ${@:2} ;;
    merge_seginfo)    echo merge_seginfo.py ${@:2} ;;
    chunk_edges)      echo chunk_edges.py ${@:2} ;;
    pick_edge)        echo pick_edge.py ${@:2} ;;
    merge_dups)       echo merge_dups.py ${@:2} ;;
    remap_ids)        echo remap_ids.py ${@:2} ;;
    chunk_overlaps)   echo chunk_overlaps.py ${@:2} ;;
    merge_overlaps)   echo merge_overlaps.py ${@:2} ;;
    chunk_anchors)    echo chunk_anchors.py ${@:2} ;;
    create_index)     echo create_index.py ${@:2} ;;
    dedup_chunk_segs) echo dedup_chunk_segs.py ${@:2} ;;
    init_db)          echo init_db.py ${@:2} ;;

    # worker
    worker)           echo worker.py ${@:2} ;;

    # sanity_check
    sanity_check)     echo sanity_check.py ${@:2} ;;

    # generate - branches again
    generate)
        case $2 in
            chunk_ccs)        echo generation/chunk_ccs.py ${@:2} ;;
            merge_ccs)        echo generation/merge_ccs.py ${@:2} ;;
            match_contins)    echo generation/match_contins.py ${@:2} ;;
            seg_graph_ccs)    echo generation/seg_graph_ccs.py ${@:2} ;;
            chunk_seg_map)    echo generation/chunk_seg_map.py ${@:2} ;;
            merge_seginfo)    echo generation/merge_seginfo.py ${@:2} ;;
            chunk_edges)      echo generation/chunk_edges.py ${@:2} ;;
            pick_edge)        echo generation/pick_edge.py ${@:2} ;;
            merge_dups)       echo generation/merge_dups.py ${@:2} ;;
            remap_ids)        echo generation/remap_ids.py ${@:2} ;;
            chunk_overlaps)   echo generation/chunk_overlaps.py ${@:2} ;;
            merge_overlaps)   echo generation/merge_overlaps.py ${@:2} ;;
            chunk_anchors)    echo generation/chunk_anchors.py ${@:2} ;;
            create_index)     echo generation/create_index.py ${@:2} ;;
            dedup_chunk_segs) echo generation/dedup_chunk_segs.py ${@:2} ;;
            init_db)          echo generation/init_db.py ${@:2} ;;
            *)  echo "invalid task name: $2"; false
	esac
    ;;

    *)  echo "invalid task name: $1"; false
esac
