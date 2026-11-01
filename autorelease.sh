#!/usr/bin/env bash
# Release every stage the training life has passed (run by the kid-a-release timer).
# All levels come from one lineage: one brain, trained stage after stage; each level is
# that brain frozen when it passed. A level from any other source is replaced.
cd "$(dirname "$0")"
PY=/home/archkris/organic-learning/.venv/bin/python
LIFE=kid_s3
for cand in /home/archkris/organic-learning/out/levels/${LIFE}_*.json; do
  [ -e "$cand" ] || continue
  stage=$(basename "$cand" .json); stage=${stage#${LIFE}_}
  id=$($PY -c "import release; print(release.LEVELS.get('$stage', ('',))[0])")
  [ -n "$id" ] || continue
  src=$($PY -c "import json; print(json.load(open('levels/$id.json')).get('source', ''))" 2>/dev/null)
  [ "$src" = "$(basename "${cand%.json}")" ] && continue
  $PY release.py "${cand%.json}" > /dev/null && echo "released $id ($stage) from $LIFE"
done
