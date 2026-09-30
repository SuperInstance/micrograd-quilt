"""qcell.stepper — incremental statevector walking (O(gates) sims).

emit v1 re-ran micromoth.simulate on every per-gate prefix, so a
ledger of G gates cost G statevector simulations — O(G * 2^n) each,
O(G^2 * 2^n) total.  n=4+ circuits need the subset, not full prefixes.

The stepper applies ONE gate to an existing statevector, in the same
operation order as micromoth.simulate, so every intermediate vector is
BIT-IDENTICAL to the prefix-simulation form.  That identity is the
whole contract: tests/test_tick_witness.py pins it against simulate
over random circuits before any ledger trusts the walk.
"""
from __future__ import annotations

R2 = 0.70710678118  # same constant micromoth uses


def _superpose(x, y):
    return ([R2 * (x[j] + y[j]) for j in range(2)],
            [R2 * (x[j] - y[j]) for j in range(2)])


def _turn(x, y, theta):
    theta = float(theta)
    return ([x[0] * __import__('math').cos(theta / 2) + y[1] * __import__('math').sin(theta / 2),
             x[1] * __import__('math').cos(theta / 2) - y[0] * __import__('math').sin(theta / 2)],
            [y[0] * __import__('math').cos(theta / 2) + x[1] * __import__('math').sin(theta / 2),
             y[1] * __import__('math').cos(theta / 2) - x[0] * __import__('math').sin(theta / 2)])


def _phaseturn(x, y, theta):
    from math import cos, sin
    theta = float(theta)
    return ([[x[0] * cos(theta / 2) - x[1] * sin(-theta / 2),
              x[1] * cos(theta / 2) + x[0] * sin(-theta / 2)],
             [y[0] * cos(theta / 2) - y[1] * sin(+theta / 2),
              y[1] * cos(theta / 2) + y[0] * sin(+theta / 2)]])


def apply_gate(sv, gate, n):
    """Apply one simulator-executable gate tuple to statevector sv in
    place, mirroring micromoth.simulate's gate loop exactly.  'init'
    replaces the vector; 'm' is a no-op on the state (it only names the
    output map in simulate)."""
    name = gate[0]

    if name == 'init':
        k = gate[1]
        if isinstance(k[0], list):
            sv[:] = [list(e) for e in k]
        else:
            sv[:] = [[e, 0.0] for e in k]
        return

    if name == 'm':
        return  # measurement names outputs; statevector unchanged

    if name in ('x', 'h', 'rx', 'rz'):
        j = gate[-1]
        for i0 in range(2 ** j):
            for i1 in range(2 ** (n - j - 1)):
                b0 = i0 + 2 ** (j + 1) * i1
                b1 = b0 + 2 ** j
                if name == 'x':
                    sv[b0], sv[b1] = sv[b1], sv[b0]
                elif name == 'h':
                    sv[b0], sv[b1] = _superpose(sv[b0], sv[b1])
                elif name == 'rx':
                    sv[b0], sv[b1] = _turn(sv[b0], sv[b1], gate[1])
                elif name == 'rz':
                    sv[b0], sv[b1] = _phaseturn(sv[b0], sv[b1], gate[1])
        return

    if name in ('cx', 'crx', 'swap'):
        if name in ('cx', 'swap'):
            s, t = gate[1:]
        else:
            theta = gate[1]
            s, t = gate[2:]
        l, h = sorted((s, t))
        for i0 in range(2 ** l):
            for i1 in range(2 ** (h - l - 1)):
                for i2 in range(2 ** (n - h - 1)):
                    b00 = i0 + 2 ** (l + 1) * i1 + 2 ** (h + 1) * i2
                    b01 = b00 + 2 ** t
                    b10 = b00 + 2 ** s
                    b11 = b10 + 2 ** t
                    if name == 'cx':
                        sv[b10], sv[b11] = sv[b11], sv[b10]
                    elif name == 'crx':
                        sv[b10], sv[b11] = _turn(sv[b10], sv[b11], theta)
                    elif name == 'swap':
                        sv[b01], sv[b10] = sv[b10], sv[b01]
        return

    raise ValueError(f"stepper: unsupported gate {name!r}")


def zero_state(n):
    sv = [[0.0, 0.0] for _ in range(2 ** n)]
    sv[0] = [1.0, 0.0]
    return sv


def walk(prog, n):
    """Yield the statevector AFTER each gate of prog, starting from
    |0...0>.  One simulation total, not one per prefix."""
    sv = zero_state(n)
    for gate in prog:
        apply_gate(sv, gate, n)
        yield sv
