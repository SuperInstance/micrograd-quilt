"""quilt/engine.py — micrograd's Value, quilted (float-first, twin-aware).

Design law 1, amended per critic ref M3-01 (MiniMax-M3 hostile review,
2026-09-21 ~01:10Z): float64 is the fast path; exact rational twins
(fractions.Fraction) are opt-in via engine mode 'exact' (the --exact flag of
Demo A). Fraction(x) of a float x is its EXACT binary expansion, so twin
arithmetic is real arithmetic on the same inputs: |float - twin| is
accumulated rounding error, measured — not approximated away.

Transcendental boundary (documented, honest): tanh/exp/cos pass through libm
(math.*) and freeze the result as an exact rational. All rational-skeleton
arithmetic (add/mul/pow-int/relu) and all derivative arithmetic is exact;
drift around transcendentals is drift of the skeleton that feeds them.

Pow boundary (documented): x**n for integer n is evaluated as the correctly
rounded exact power float(Fraction(x)**n) — NOT libm pow. Reason: libm pow
is not guaranteed correctly rounded in all cases; we observed a 1-ulp
deviation (0.2040816326530612 vs ...123) on this repo's own Demo A snippet
(10.0/f, f**-1) when routed through C pow. The engine's float path is the
correctly-rounded shadow of the exact path; the twin therefore agrees
bitwise on the rational skeleton.

Constants:
  U = 2**-52 = 2.220446049250313e-16: IEEE-754 binary64 unit roundoff (cited:
    IEEE Std 754-2019, Table 3.5).
  Local partials are stored at forward time (Karpathy's own microgpt note in
    this repo's README endorses storing local gradients at forward time over
    per-op backward closures).
"""

import math
from contextlib import contextmanager
from fractions import Fraction

U = 2.220446049250313e-16  # 2**-52, IEEE-754 binary64 unit roundoff

_MODE = "float"     # 'float' | 'exact'  (exact = every node promoted to twin)
_TAPE = None        # active quilt.tape.Tape, set via tape.attach()
_QUIET = 0          # replay depth: suppress tape appends


@contextmanager
def mode(m):
    """Set twin mode ('float' or 'exact') for Values built inside the block."""
    global _MODE
    old, _MODE = _MODE, m
    try:
        yield
    finally:
        _MODE = old


@contextmanager
def quiet():
    """Suppress tape emission (used by tape.replay while rebuilding)."""
    global _QUIET
    _QUIET += 1
    try:
        yield
    finally:
        _QUIET -= 1


def reduction_orders():
    """The two reduction orders of the float-native comb (amendment 4)."""
    return ("fwd", "rev")


def _freeze(fn):
    """Transcendental boundary: libm evaluates, Fraction freezes (see header)."""
    return lambda a: Fraction(fn(float(a)))


_xtanh, _xexp, _xcos, _xsin = (_freeze(math.tanh), _freeze(math.exp),
                               _freeze(math.cos), _freeze(math.sin))


class Value:
    """A scalar with float data, optional exact twin, and recorded lineage."""

    _next_id = 0

    @classmethod
    def reset_ids(cls):
        """Reset the id namespace so seeded runs produce comparable tapes."""
        cls._next_id = 0

    def __init__(self, data, _parents=(), _op="", _partials=(), _id=None,
                 _partials_twin=None):
        if isinstance(data, Fraction):
            data = float(data)
        self.id = Value._next_id if _id is None else _id
        if _id is None:
            Value._next_id += 1
        self.data = data
        self.twin = Fraction(data) if _MODE == "exact" else None
        self.grad = 0.0
        self.grad_twin = Fraction(0) if self.twin is not None else None
        self._parents = list(_parents)
        self._prev = set(_parents)
        self._op = _op
        self._partials = tuple(_partials)   # d(out)/d(parent_i), forward-time
        self._partials_twin = _partials_twin
        if _TAPE is not None and _QUIET == 0:
            _TAPE.bind(self)
            if _op:
                _TAPE.link(self)

    # -- forward ops ---------------------------------------------------------
    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        if self.twin is not None and other.twin is not None:
            twin = self.twin + other.twin
            pt = (Fraction(1), Fraction(1))
        else:
            twin = pt = None
        return Value(self.data + other.data, (self, other), "+", (1.0, 1.0),
                     _partials_twin=pt).__twin(twin)

    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        if self.twin is not None and other.twin is not None:
            twin = self.twin * other.twin
            pt = (other.twin, self.twin)
        else:
            twin = pt = None
        return Value(self.data * other.data, (self, other), "*",
                     (other.data, self.data),
                     _partials_twin=pt).__twin(twin)

    def __pow__(self, n):
        assert isinstance(n, (int, float)), "only int/float powers supported"
        if isinstance(n, float) and not n.is_integer():
            raise TypeError("quilt pow: integer exponents only (exact twin)")
        n = int(n)
        xq = Fraction(self.data) ** n  # exact power (see header: pow boundary)
        pq = n * Fraction(self.data) ** (n - 1)
        if self.twin is not None:
            twin = self.twin ** n
            pt = (n * self.twin ** (n - 1),)
        else:
            twin = pt = None
        return Value(float(xq), (self,), f"**{n}", (float(pq),),
                     _partials_twin=pt).__twin(twin)

    def relu(self):
        if self.twin is not None:
            twin = self.twin if self.twin > 0 else Fraction(0)
            pt = (Fraction(1) if self.twin > 0 else Fraction(0),)
        else:
            twin = pt = None
        return Value(self.data if self.data > 0 else 0.0, (self,), "relu",
                     (1.0 if self.data > 0 else 0.0,),
                     _partials_twin=pt).__twin(twin)

    def tanh(self):
        t = math.tanh(self.data)
        if self.twin is not None:
            twin = _xtanh(self.twin)
            pt = (1 - twin * twin,)
        else:
            twin = pt = None
        return Value(t, (self,), "tanh", (1 - t * t,),
                     _partials_twin=pt).__twin(twin)

    def exp(self):
        e = math.exp(self.data)
        if self.twin is not None:
            twin = _xexp(self.twin)
            pt = (twin,)
        else:
            twin = pt = None
        return Value(e, (self,), "exp", (e,), _partials_twin=pt).__twin(twin)

    def cos(self):
        c = math.cos(self.data)
        if self.twin is not None:
            twin = _xcos(self.twin)
            pt = (-_xsin(self.twin),)
        else:
            twin = pt = None
        return Value(c, (self,), "cos", (-math.sin(self.data),),
                     _partials_twin=pt).__twin(twin)

    def __twin(self, twin):
        """Attach the computed twin after construction (twin needs out-value
        first for tanh/exp; here it is simply set — kept for symmetry)."""
        self.twin = twin
        if twin is not None:
            self.grad_twin = Fraction(0)
        return self

    # -- autograd ------------------------------------------------------------
    def topo(self, order="fwd"):
        """Deterministic topo order. order='rev' reverses child iteration —
        the float-native comb's second reduction order (amendment 4)."""
        out, seen = [], set()

        def visit(v):
            if id(v) in seen:
                return
            seen.add(id(v))
            kids = v._parents if order == "fwd" else reversed(v._parents)
            for c in kids:
                visit(c)
            out.append(v)

        visit(self)
        return out

    def zero_grad(self, order="fwd"):
        for v in self.topo(order):
            v.grad = 0.0
            if v.grad_twin is not None:
                v.grad_twin = Fraction(0)

    def backward(self, order="fwd", zero=True):
        """Reverse-mode backward. Emits EFFECT rows (one per parent
        contribution) and TICK rows (one per topo step) onto the attached
        tape. Deterministic given (graph, order): a later replay of the tape
        reproduces these gradients bitwise (regression guard, DESIGN.md 2)."""
        assert order in reduction_orders()
        topo = self.topo(order)
        if zero:
            self.zero_grad(order)
        self.grad = 1.0
        if self.grad_twin is not None:
            self.grad_twin = Fraction(1)
        step = 0
        if _TAPE is not None and _QUIET == 0:
            _TAPE.begin_backward()
        for v in reversed(topo):
            idx = range(len(v._parents) - 1, -1, -1) if order == "rev" \
                else range(len(v._parents))
            for i in idx:
                p, part = v._parents[i], v._partials[i]
                c = v.grad * part
                p.grad += c
                ct = None
                if v.grad_twin is not None and v._partials_twin is not None:
                    ct = v.grad_twin * v._partials_twin[i]
                    p.grad_twin += ct
                if _TAPE is not None and _QUIET == 0:
                    _TAPE.effect(v, p, c, ct)
            step += 1
            if _TAPE is not None and _QUIET == 0:
                _TAPE.tick(step, v)
        return topo

    # -- dunder plumbing -----------------------------------------------------
    def __neg__(self):
        return self * -1

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return other + (-self)

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        return self * other ** -1

    def __rtruediv__(self, other):
        return other * self ** -1

    def __repr__(self):
        return f"Value(id={self.id}, data={self.data}, grad={self.grad})"
