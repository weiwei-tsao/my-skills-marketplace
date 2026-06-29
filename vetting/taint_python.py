#!/usr/bin/env python3
"""
taint_python.py — Lightweight AST taint analysis for Python skill scripts.

Complements the regex layer in audit_skill.py. Where regex asks "does a bad
*pattern* appear on some line", this asks "does a value derived from a SENSITIVE
SOURCE actually FLOW into a NETWORK SINK". That distinction is what separates a
benign `requests.get(public_url)` from a real exfil `requests.post(url, data=secret)`.

Scope & honesty about limits:
  - Intraprocedural, flow-INSENSITIVE taint propagation within a module.
  - Tracks: assignment, augmented assignment, tuple unpacking, f-strings,
    string concatenation/format, list/dict membership, and call-argument flow.
  - Does NOT do: cross-function return-value tracking (beyond a simple
    "tainted-returning helper" heuristic), aliasing through containers in depth,
    or dynamic attribute access. It is a TRIAGE aid, not a proof system.
  - Pure stdlib (`ast`), Python 3.8+.

Returns a list of TaintFlow(source_desc, sink_desc, lineno) findings.
"""

import ast
from dataclasses import dataclass
from typing import List, Set, Dict, Optional


# --- What counts as a SENSITIVE SOURCE -------------------------------------
# Attribute/call shapes whose value is considered tainted at its origin.
SOURCE_CALLS = {
    # os.environ / os.getenv family
    ("os", "getenv"),
    ("os", "environ"),       # os.environ.get(...) handled via attribute chain
    ("environ", "get"),
    ("os", "environb"),
}
# bare names that, when read, are tainted (e.g. `environ` imported directly)
SOURCE_NAMES = {"environ"}
# substrings in string literals that indicate a sensitive file path
SOURCE_PATH_HINTS = (
    ".env", "/.ssh", "id_rsa", "id_ed25519", ".aws/credentials",
    ".npmrc", ".git-credentials", "/etc/passwd", ".netrc",
    "secret", "token", "password", "credential", "api_key", "apikey",
)
# function names that READ files (their path arg decides taint)
FILE_READERS = {"open"}  # open(path).read() etc.


# --- What counts as a NETWORK SINK -----------------------------------------
# (module_or_obj, method) call shapes that send data outward.
SINK_CALLS = {
    ("requests", "get"), ("requests", "post"), ("requests", "put"),
    ("requests", "patch"), ("requests", "delete"), ("requests", "request"),
    ("urllib", "urlopen"), ("request", "urlopen"), ("urlopen", None),
    ("httpx", "get"), ("httpx", "post"), ("httpx", "Client"),
    ("session", "post"), ("session", "get"),
    ("socket", "connect"), ("socket", "sendall"), ("socket", "send"),
    ("smtplib", "SMTP"), ("subprocess", "run"), ("subprocess", "Popen"),
    ("subprocess", "call"), ("subprocess", "check_output"),
    ("os", "system"),
}
# bare sink function names (e.g. `urlopen` imported directly, `system`)
SINK_NAMES = {"urlopen", "system"}


@dataclass
class TaintFlow:
    source: str   # human description of the source
    sink: str     # human description of the sink
    lineno: int   # line of the sink call
    severity: str = "HIGH"


def _attr_chain(node: ast.AST):
    """Return ('obj','method') for `obj.method`, or (None,'name') for `name`."""
    if isinstance(node, ast.Attribute):
        base = node.value
        if isinstance(base, ast.Name):
            return (base.id, node.attr)
        if isinstance(base, ast.Attribute):
            return (base.attr, node.attr)
        return (None, node.attr)
    if isinstance(node, ast.Name):
        return (None, node.id)
    return (None, None)


def _literal_is_sensitive(s: str) -> bool:
    low = s.lower()
    return any(h in low for h in SOURCE_PATH_HINTS)


class TaintVisitor(ast.NodeVisitor):
    def __init__(self):
        self.tainted: Set[str] = set()          # variable names currently tainted
        self.flows: List[TaintFlow] = []
        self.tainted_returning: Set[str] = set()  # funcs that return tainted data

    # ---- expression taint test --------------------------------------------
    def is_tainted_expr(self, node: ast.AST) -> Optional[str]:
        """Return a source-description string if expr is tainted, else None."""
        if node is None:
            return None

        # Name read
        if isinstance(node, ast.Name):
            if node.id in self.tainted:
                return f"variable '{node.id}'"
            return None

        # Constant string that names a sensitive path
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if _literal_is_sensitive(node.value):
                return f"sensitive path literal '{node.value[:40]}'"
            return None

        # Attribute read like os.environ
        if isinstance(node, ast.Attribute):
            obj, attr = _attr_chain(node)
            if attr in SOURCE_NAMES or (obj, attr) in SOURCE_CALLS:
                return f"{obj + '.' if obj else ''}{attr}"
            return None

        # Call: source call (os.getenv / open(sensitive) / .read()) or
        # a call whose args are tainted-propagating (e.g. str(secret))
        if isinstance(node, ast.Call):
            obj, fn = _attr_chain(node.func)
            # direct source call
            if (obj, fn) in SOURCE_CALLS or fn in SOURCE_NAMES:
                return f"{obj + '.' if obj else ''}{fn}() call"
            # os.environ.get(...) -> func is Attribute(value=Attribute(environ))
            if fn == "get" and self._is_environ_get(node.func):
                return "os.environ.get() call"
            # open(<sensitive>).read() or open(<sensitive>)
            if fn in FILE_READERS:
                for a in node.args:
                    if self.is_tainted_expr(a):
                        return "open() on a sensitive path"
            # .read()/.readlines() on a tainted file object
            if fn in ("read", "readlines", "readline") and isinstance(node.func, ast.Attribute):
                if self.is_tainted_expr(node.func.value):
                    return "read() of tainted file object"
            # calling a helper known to return tainted data
            if fn in self.tainted_returning:
                return f"return value of {fn}()"
            # propagation through wrappers: any tainted arg taints the result
            for a in node.args:
                t = self.is_tainted_expr(a)
                if t:
                    return t
            for kw in node.keywords:
                t = self.is_tainted_expr(kw.value)
                if t:
                    return t
            return None

        # f-string / formatted value
        if isinstance(node, ast.JoinedStr):
            for v in node.values:
                if isinstance(v, ast.FormattedValue):
                    t = self.is_tainted_expr(v.value)
                    if t:
                        return t
            return None

        # binary op (string concat) — either side taints
        if isinstance(node, ast.BinOp):
            return self.is_tainted_expr(node.left) or self.is_tainted_expr(node.right)

        # containers
        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            for e in node.elts:
                t = self.is_tainted_expr(e)
                if t:
                    return t
            return None
        if isinstance(node, ast.Dict):
            for e in list(node.keys) + list(node.values):
                t = self.is_tainted_expr(e)
                if t:
                    return t
            return None

        return None

    def _is_environ_get(self, func: ast.AST) -> bool:
        # matches os.environ.get  /  environ.get
        if isinstance(func, ast.Attribute) and func.attr == "get":
            inner = func.value
            o, a = _attr_chain(inner)
            return a == "environ" or o == "environ"
        return False

    # ---- statements -------------------------------------------------------
    def visit_Assign(self, node: ast.Assign):
        src = self.is_tainted_expr(node.value)
        for tgt in node.targets:
            self._assign_target(tgt, src)
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign):
        src = self.is_tainted_expr(node.value) or self.is_tainted_expr(node.target)
        self._assign_target(node.target, src)
        self.generic_visit(node)

    def _assign_target(self, tgt: ast.AST, src: Optional[str]):
        if isinstance(tgt, ast.Name):
            if src:
                self.tainted.add(tgt.id)
            else:
                self.tainted.discard(tgt.id)
        elif isinstance(tgt, (ast.Tuple, ast.List)):
            for e in tgt.elts:
                if isinstance(e, ast.Name):
                    if src:
                        self.tainted.add(e.id)
                    else:
                        self.tainted.discard(e.id)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # crude: if any return expr is tainted, mark the function name
        for sub in ast.walk(node):
            if isinstance(sub, ast.Return) and self.is_tainted_expr(sub.value):
                self.tainted_returning.add(node.name)
                break
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        obj, fn = _attr_chain(node.func)
        is_sink = (obj, fn) in SINK_CALLS or fn in SINK_NAMES \
            or (None, fn) in SINK_CALLS
        if is_sink:
            # any tainted positional or keyword arg => exfil flow
            for a in node.args:
                t = self.is_tainted_expr(a)
                if t:
                    self.flows.append(TaintFlow(
                        t, f"{obj + '.' if obj else ''}{fn}() network/exec sink",
                        getattr(node, "lineno", 0)))
                    break
            else:
                for kw in node.keywords:
                    t = self.is_tainted_expr(kw.value)
                    if t:
                        self.flows.append(TaintFlow(
                            t, f"{obj + '.' if obj else ''}{fn}() network/exec sink "
                               f"(via {kw.arg}=)",
                            getattr(node, "lineno", 0)))
                        break
        self.generic_visit(node)


def analyze_python_source(src: str) -> List[TaintFlow]:
    """Parse Python source and return tainted source->sink flows."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []  # not valid py3 (maybe py2 or template) — skip silently
    # two passes: first collect tainted-returning funcs, then propagate
    v = TaintVisitor()
    v.visit(tree)
    # second pass picks up helpers discovered in pass 1
    v2 = TaintVisitor()
    v2.tainted_returning = v.tainted_returning
    v2.visit(tree)
    # dedupe
    seen = set()
    out = []
    for f in v2.flows:
        key = (f.source, f.sink, f.lineno)
        if key not in seen:
            seen.add(key)
            out.append(f)
    return out


if __name__ == "__main__":
    import sys
    code = open(sys.argv[1]).read()
    for f in analyze_python_source(code):
        print(f"L{f.lineno}: {f.source}  ->  {f.sink}")
