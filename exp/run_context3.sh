#!/bin/sh

home="../" # "../../.."
dataset="../data/baby_lm"
# kenlm="../../../../kenlm/build"

context=3
seed=0
config="context3"
# for seed in `seq 0 0`

for name in "aochildes" "switchboard" "cbt" "bnc_spoken" "gutenberg" "open_subtitles" "qed" "simple_wikipedia" "children_stories" "wikipedia"
do
  echo $name
  python -u $home/compose.py \
    --dataset lm \
    --lm_data_dir $dataset \
    --train_name $name \
    --seed $seed \
    --model_type retrieval \
    --wug_limit 20 \
    --wug_size 2 \
    --wug_count 1 \
    --variants 1 \
    --template_sim window \
    --sim_window_size $context \
    --compute_adjacency \
    --n_sample 500 \
    --write "$config/composed.$name.json" \
    --output_only \
    --max_comp_len 300 \
    > $config/compose.$name.out 2> $config/compose.$name.err

  python -u $home/fake_corpus.py \
    --dataset lm \
    --lm_data_dir $dataset \
    --train_name $name \
    --augment "$config/composed.$name.json" \
    --write "augment_$config/augmented.$name.train" \
    > $config/comb.$name.out \
    2> $config/comb.$name.err


done