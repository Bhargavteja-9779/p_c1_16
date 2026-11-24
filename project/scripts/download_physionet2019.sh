#!/usr/bin/env bash
# Download PhysioNet/CinC 2019 sepsis challenge training data (CC BY 4.0) in parallel. Idempotent.
# Uses PhysioNet's official open-data S3 mirror (physionet.org redirects there). Files that are
# empty or do not start with the expected header are re-downloaded.
cd "$(dirname "$0")/../data/raw/physionet2019" || exit 1
BASE=https://physionet-open.s3.amazonaws.com/challenge-2019/1.0.0/training
for s in A B; do
  mkdir -p training_set$s
  [ -s list_$s.txt ] || curl -sL "https://physionet.org/files/challenge-2019/1.0.0/training/training_set$s/" | grep -oE 'href="p[0-9]+\.psv"' | sed -E 's/href="(.*)"/\1/' > list_$s.txt
  cat list_$s.txt | xargs -P 32 -I{} sh -c "head -c 3 training_set$s/{} 2>/dev/null | grep -q '^HR|' || curl -sL --retry 5 -o training_set$s/{} $BASE/training_set$s/{}"
done
bad=0; for s in A B; do for f in $(cat list_$s.txt); do head -c 3 training_set$s/$f 2>/dev/null | grep -q '^HR|' || bad=$((bad+1)); done; done
echo "DONE bad=$bad"
