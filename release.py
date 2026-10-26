"""Release a level: freeze a brain that passed a curriculum stage and describe it.

    python release.py ~/organic-learning/out/levels/kid_s0_B

Copies the brain (as it was when it passed the stage) to models/<level>.pkl
(not in git: large) and writes levels/<level>.json, the level's card: what it
is like, its human-age equivalent, what it can and cannot do, and its scores on
held-out items of every stage at the moment it passed.
"""

import datetime
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
ORGANIC = os.path.expanduser(os.environ.get("ORGANIC_PATH", "~/organic-learning"))

# one level per curriculum stage (organic-learning docs/CURRICULUM.md); ages are the human reference
LEVELS = {
    "B": ("L0", "echo", "12-month-old", "repeats words it hears, babbles when unsure",
          "Say a word (\"ball!\", \"say doggy\") and it says it back. It knows ~60 first words well and tries to copy any word you say.",
          "answer questions, name things in pictures, make sentences"),
    "W1": ("L1", "first words", "18-month-old", "names familiar things it sees and hears",
           "Show it a dog, a cat, a car, a cup, a banana... and ask \"what is this?\". Animal sounds, hi, bye, more.",
           "colours, counting, yes/no questions, sentences"),
    "W2": ("L2", "two words", "2-year-old", "colours, yes/no, counting to three, two-word phrases",
           "\"what colour is the car?\", \"is there a dog?\", \"how many people?\" (up to three).",
           "where things are, feelings, short stories"),
    "P": ("L3", "preschool", "4-year-old", "where things are, feelings, short replies, one-sentence stories",
          "\"where is the person?\", \"thank you!\", \"sam dropped his ice cream. how does he feel?\"",
          "reading, rhymes, arithmetic"),
    "K": ("L4", "kindergarten", "5-year-old", "letters, rhymes, opposites, reading signs, counting to twenty",
          "Show it a sign and ask what it says; \"what rhymes with cat?\"; \"what is the opposite of hot?\"",
          "sentences about stories, arithmetic"),
    "G1": ("L5", "first grade", "6-to-7-year-old", "sentences, addition within 20, questions about a short story, describing a picture",
           "\"what is 7 plus 5?\", a two-sentence story and a question, \"what is happening in the picture?\"",
           "multi-step problems, explaining why"),
}


def main(stem):
    card_in = json.load(open(stem + ".json"))
    stage = card_in["stage"]
    lid, name, age, summary, can, cannot = LEVELS[stage]
    os.makedirs(os.path.join(ROOT, "models"), exist_ok=True)
    shutil.copy(stem + ".pkl", os.path.join(ROOT, "models", lid + ".pkl"))
    commit = subprocess.run(["git", "-C", ORGANIC, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    card = {
        "id": lid, "name": name, "human_age": age, "summary": summary, "can": can, "cannot": cannot,
        "stage": stage, "brain": card_in.get("brain"), "moments_lived": card_in["age"], "clusters": card_in["clusters"],
        "scores": {s: {"lenient": round(v["score"], 3), "exact": round(v["exact"], 3), "ticks": round(v["tick"], 1)} for s, v in card_in["measure"].items()},
        "passed": {s: round(v, 3) for s, v in card_in["passed"].items()},
        "released": datetime.date.today().isoformat(), "organic_learning_commit": commit, "source": os.path.basename(stem),
    }
    os.makedirs(os.path.join(ROOT, "levels"), exist_ok=True)
    json.dump(card, open(os.path.join(ROOT, "levels", lid + ".json"), "w"), indent=1)
    print(json.dumps(card, indent=1))


if __name__ == "__main__":
    main(os.path.expanduser(sys.argv[1]))
