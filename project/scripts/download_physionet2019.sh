#!/usr/bin/env bash
# Download PhysioNet/CinC 2019 sepsis challenge training data (CC BY 4.0) in parallel. Idempotent.
cd "$(dirname "$0")/../data/raw/physionet2019" || exit 1
for s in A B; do
  mkdir -p training_set$s
  [ -s list_$s.txt ] || curl -s "https://physionet.org/files/challenge-2019/1.0.0/training/training_set$s/" | grep -oE 'href="p[0-9]+\.psv"' | sed -E 's/href="(.*)"/\1/' > list_$s.txt
  cat list_$s.txt | xargs -P 24 -I{} sh -c "[ -s training_set$s/{} ] || curl -s --retry 3 -o training_set$s/{} https://physionet.org/files/challenge-2019/1.0.0/training/training_set$s/{}"
done
echo DONE
