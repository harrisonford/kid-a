#!/usr/bin/env bash
# Release every stage the training life has passed that is not released yet
# (run by the kid-a-release timer). A promotion in the curriculum is the release criterion.
cd "$(dirname "$0")"
PY=/home/archkris/organic-learning/.venv/bin/python
for cand in /home/archkris/organic-learning/out/levels/kid_s0_*.json; do
  [ -e "$cand" ] || continue
  stage=$(basename "$cand" .json); stage=${stage#kid_s0_}
  id=$($PY -c "import release; print(release.LEVELS.get('$stage', ('',))[0])")
  [ -n "$id" ] && [ ! -f "levels/$id.json" ] && $PY release.py "${cand%.json}" > /dev/null && echo "released $id ($stage)"
done
