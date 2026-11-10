"""Wake a released brain without loading it whole.

A brain is mostly its clusters' input and output weights, and a reply only reads
those of the few clusters that take part. So every big array stays on disk,
mapped straight out of the .pkl (its pages come in as they are read), and only
what each reply reads whole is held in RAM: each cortex's identities (Z).
L3 runs in ~1 GB instead of 7.4 GB and is awake in under a second.

Mapped arrays are copy-on-write: nothing a brain does here reaches the file.
The .pkl must be replaced whole (os.replace), never rewritten in place, while a
server may have it mapped.
"""

import pickle
import struct

import numpy as np

BIG = 4 << 20  # arrays above this many bytes stay on disk (never under 64 KiB: pickle keeps smaller ones inside its frames)


class _OnDisk:
    """Where a big array's bytes are in the file."""

    def __init__(self, offset, size):
        self.offset, self.size = offset, size


class _Unpickler(pickle._Unpickler):  # the Python one: the C one cannot step over bytes
    def __init__(self, f, path):
        super().__init__(f)
        self.f, self.path = f, path

    def _step_over(self, n):
        self.append(_OnDisk(self.f.tell(), n))
        self.f.seek(n, 1)

    def load_binbytes8(self):
        (n,) = struct.unpack("<Q", self.read(8))
        self._step_over(n) if n > BIG else self.append(self.read(n))

    def load_bytearray8(self):
        (n,) = struct.unpack("<Q", self.read(8))
        if n > BIG:
            return self._step_over(n)
        b = bytearray(n)
        self.readinto(b)
        self.append(b)

    dispatch = dict(pickle._Unpickler.dispatch)
    dispatch[pickle.BINBYTES8[0]] = load_binbytes8
    dispatch[pickle.BYTEARRAY8[0]] = load_bytearray8

    def find_class(self, module, name):
        real = super().find_class(module, name)
        if name != "_frombuffer":  # how numpy rebuilds an array (pickle protocol 5)
            return real

        def frombuffer(buf, dtype, shape, order):
            if isinstance(buf, _OnDisk):
                return np.memmap(self.path, dtype=dtype, mode="c", offset=buf.offset, shape=shape, order=order)
            return real(buf, dtype, shape, order)

        return frombuffer


def load(path):
    """The brain, with every big array still on disk."""
    with open(path, "rb") as f:
        u = _Unpickler(f, path)
        brain = u.load()
    u.memo.clear()  # it still points at every array: let go, or the ones hold() replaces stay mapped
    return brain


def _on_disk(brain):
    from release import _parts

    return [c for c in _parts(brain) if type(c).__name__ == "Cortex" and isinstance(c.Z, np.memmap)]


def to_hold(brain):
    """Bytes hold() will bring into RAM."""
    return int(sum(c.Z.nbytes for c in _on_disk(brain)))


def hold(brain):
    """Bring into RAM what every reply reads whole: each cortex's identities."""
    for c in _on_disk(brain):
        c.Z = np.array(c.Z)  # also aligned, which the mapped bytes are not (the product is ~3x faster)
    return brain
