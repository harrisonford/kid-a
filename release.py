"""Release a level: freeze a brain that passed a curriculum stage and describe it.

    python release.py ~/organic-learning/out/levels/kid_s2_W1
    python release.py --count L0         # add parameters and memory to an older card

Copies the brain (as it was when it passed the stage) to models/<level>.pkl
(not in git: large) and writes levels/<level>.json, the level's card: what it
is like, its human-age equivalent, what it can and cannot do, and its scores on
held-out items of every stage at the moment it passed.
"""

import datetime
import json
import os
import pickle
import shutil
import subprocess
import sys

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
ORGANIC = os.path.expanduser(os.environ.get("ORGANIC_PATH", "~/organic-learning"))

# one level per curriculum stage (organic-learning docs/CURRICULUM.md); ages are the human reference
LEVELS = {
    "BB": ("L1", "babbler", "8-month-old", "babbles in the sounds of the language it hears",
           "Talk to it: it babbles back in fragments that sound like what it has heard (\"is this\", \"a books\"). No words yet.",
           "say real words on purpose, repeat you, answer anything"),
    "B": ("L2", "echo", "12-month-old", "repeats words it hears, babbles when unsure",
          "Say a word (\"ball!\", \"say doggy\") and it says it back. It knows ~60 first words well and tries to copy any word you say.",
          "answer questions, name things in pictures, make sentences"),
    "W1": ("L3", "first words", "18-month-old", "names familiar things it sees and hears",
           "Show it a dog, a cat, a car, a cup, a banana... and ask \"what is this?\". Animal sounds, hi, bye, more.",
           "colours, counting, yes/no questions, sentences"),
    "W2": ("L4", "two words", "2-year-old", "colours, yes/no, counting to three, two-word phrases",
           "\"what colour is the car?\", \"is there a dog?\", \"how many people?\" (up to three).",
           "where things are, feelings, short stories"),
    "P": ("L5", "preschool", "4-year-old", "where things are, feelings, short replies, one-sentence stories",
          "\"where is the person?\", \"thank you!\", \"sam dropped his ice cream. how does he feel?\"",
          "reading, rhymes, arithmetic"),
    "K": ("L6", "kindergarten", "5-year-old", "letters, rhymes, opposites, reading signs, counting to twenty",
          "Show it a sign and ask what it says; \"what rhymes with cat?\"; \"what is the opposite of hot?\"",
          "sentences about stories, arithmetic"),
    "G1": ("L7", "first grade", "6-to-7-year-old", "sentences, addition within 20, questions about a short story, describing a picture",
           "\"what is 7 plus 5?\", a two-sentence story and a question, \"what is happening in the picture?\"",
           "multi-step problems, explaining why"),
}


def _parts(brain):
    """Every cortex and every array in the brain, each once."""
    seen, stack = set(), [brain]
    while stack:
        o = stack.pop()
        if id(o) in seen or o is None or isinstance(o, (str, bytes, int, float, bool)):
            continue
        seen.add(id(o))
        if isinstance(o, np.ndarray) or type(o).__name__ == "Cortex":
            yield o
        if isinstance(o, dict):
            stack.extend(o.values())
        elif isinstance(o, (list, tuple, set, frozenset)):
            stack.extend(o)
        elif hasattr(o, "__dict__"):
            stack.extend(vars(o).values())


def parameters(brain):
    """How many learned numbers the brain holds.

    A cortex preallocates room for clusters it has not grown yet, so only living
    clusters count, and each one only over the inputs it reaches: identity and
    input weights per reached input, output weights per output neuron, plus
    myelin, stability and patience, plus its associations. Any other float array
    in the brain (outside a cortex) counts whole.
    """
    parts = list(_parts(brain))
    inside = {id(v) for c in parts if type(c).__name__ == "Cortex" for v in vars(c).values() if isinstance(v, np.ndarray)}
    total = 0
    for o in parts:
        if type(o).__name__ == "Cortex":
            C, reach = o.C, int(o.reach[: o.C].sum())
            total += reach * (1 + o.n) + C * o.n * len(o.outputs) + 3 * C + sum(len(v) for v in o.assoc.values())
        elif o.dtype.kind == "f" and id(o) not in inside:
            total += o.size
    return int(total)


def memory(brain):
    """Bytes the brain takes in RAM to run: all its arrays, preallocated room included (within ~1% of the measured RSS)."""
    return int(sum(o.nbytes for o in _parts(brain) if isinstance(o, np.ndarray)))


def size(card, brain):
    card["parameters"], card["memory_bytes"] = parameters(brain), memory(brain)


def count(lid):
    """Measure a released level's brain and write its size into its card (cards from before sizes were measured)."""
    sys.path.insert(0, ORGANIC)
    path = os.path.join(ROOT, "levels", lid + ".json")
    card = json.load(open(path))
    size(card, pickle.load(open(os.path.join(ROOT, "models", lid + ".pkl"), "rb")))
    json.dump(card, open(path, "w"), indent=1)
    return card["parameters"], card["memory_bytes"]


def main(stem):
    card_in = json.load(open(stem + ".json"))
    stage = card_in["stage"]
    lid, name, age, summary, can, cannot = LEVELS[stage]
    sys.path.insert(0, ORGANIC)  # to unpickle the brain and count its parameters
    os.makedirs(os.path.join(ROOT, "models"), exist_ok=True)
    brain = pickle.load(open(stem + ".pkl", "rb"))
    if hasattr(brain, "babble"):  # a served level babbles when it has nothing to say
        brain.babble_when_silent = True
    with open(os.path.join(ROOT, "models", lid + ".pkl"), "wb") as f:
        pickle.dump(brain, f)
    commit = subprocess.run(["git", "-C", ORGANIC, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    card = {
        "id": lid, "name": name, "human_age": age, "summary": summary, "can": can, "cannot": cannot,
        "stage": stage, "brain": card_in.get("brain"), "moments_lived": card_in["age"], "clusters": card_in["clusters"],
        "scores": {s: {"lenient": round(v["score"], 3), "exact": round(v["exact"], 3), "ticks": round(v["tick"], 1)} for s, v in card_in["measure"].items()},
        "passed": {s: round(v, 3) for s, v in card_in["passed"].items()},
        "released": datetime.date.today().isoformat(), "organic_learning_commit": commit, "source": os.path.basename(stem),
    }
    size(card, brain)
    os.makedirs(os.path.join(ROOT, "levels"), exist_ok=True)
    json.dump(card, open(os.path.join(ROOT, "levels", lid + ".json"), "w"), indent=1)
    print(json.dumps(card, indent=1))


if __name__ == "__main__":
    if sys.argv[1] == "--count":  # python release.py --count L0 [L1 ...]
        for lid in sys.argv[2:]:
            print(lid, count(lid))
    else:
        main(os.path.expanduser(sys.argv[1]))
