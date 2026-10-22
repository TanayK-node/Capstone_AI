"""Static scanner for a cloned paper repository (M7). STANDALONE: standard library plus
optional pyyaml / tomli, no app imports, because it runs inside the sandbox container:

    docker run --rm --network none --read-only -v <repo>:/repo:ro \\
        -v scanner.py:/work/scan.py:ro paperlens-sandbox /work/scan.py /repo

It NEVER executes repository code (CLAUDE.md rule 6): Python files are read with ast.parse,
values with ast.literal_eval (literals only), configs with yaml.safe_load / json / tomllib.
Prints one JSON object: {"params": [...], "files_scanned": n, "errors": [...]}.
"""

from __future__ import annotations

import ast
import json
import os
import re
import sys
import time

MAX_FILE_BYTES = 1_000_000
MAX_CONFIG_BYTES = 200_000
MAX_FILES = 5_000
MAX_PARAMS = 5_000
TIME_BUDGET_S = 45.0
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env", "build", "dist",
    "site-packages", ".tox", ".mypy_cache", ".pytest_cache", "docs", "doc", "test", "tests",
}  # fmt: skip
CONFIG_EXT = {".yaml", ".yml", ".json", ".toml", ".gin", ".cfg"}
# Names worth keeping when they are plain assignments (argparse / flags / configs keep all).
HP_NAME = re.compile(
    r"(^|_)(lr|learning_rate|batch|epoch|step|warmup|decay|dropout|drop|seed|momentum|beta|"
    r"eps|epsilon|smoothing|hidden|layers?|heads?|d_model|dim|rank|alpha|temperature|tau|"
    r"clip|grad|accum|max_len|seq_len|max_seq|iterations?|updates?|optimizer|schedule)"
    r"(_|$|s$)",
    re.I,
)
FLAG_FUNCS = {
    "DEFINE_integer", "DEFINE_float", "DEFINE_string", "DEFINE_bool", "DEFINE_boolean",
    "DEFINE_enum", "DEFINE_list", "DEFINE_multi_integer", "DEFINE_multi_float",
}  # fmt: skip
README_FLAG = re.compile(r"--([A-Za-z][\w.-]*)(?:[ =]+)([^\s\\'\"]+)")


def literal(node: ast.AST | None) -> object:
    """A literal value or raise ValueError; never evaluates anything else."""
    if node is None:
        raise ValueError("no value")
    value = ast.literal_eval(node)
    if isinstance(value, (int, float, str, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)) and len(value) <= 8:
        return list(value)
    raise ValueError("not a scalar")


class Collector:
    def __init__(self, root: str) -> None:
        self.root = root
        self.params: list[dict[str, object]] = []
        self.errors: list[str] = []
        self.files = 0

    def add(self, name: str, value: object, path: str, line: int | None, kind: str) -> None:
        if len(self.params) >= MAX_PARAMS or value is None or name == "":
            return
        if isinstance(value, str) and (len(value) > 120 or "\n" in value):
            return  # help texts, file contents
        self.params.append(
            {
                "name": name,
                "value": value if isinstance(value, str) else repr(value),  # True -> "True"
                "file": os.path.relpath(path, self.root),
                "line": line,
                "kind": kind,
            }
        )


# ------------------------------------------------------------------ python


# An assignment under "if not is_training:" / "if eval_mode:" switches something off for
# inference (BERT sets dropout to 0.0 there); it is not a training hyperparameter.
EVAL_BRANCH = re.compile(r"\bnot\s+\w*train|\beval|\binference|\bpredict", re.I)


def scan_python(path: str, source: str, out: Collector) -> None:
    try:
        tree = ast.parse(source, filename=path)
    except (SyntaxError, ValueError) as exc:  # Python 2 code is common in old repos
        out.errors.append(f"{os.path.relpath(path, out.root)}: {type(exc).__name__}")
        return
    _Visitor(path, out).visit(tree)


class _Visitor(ast.NodeVisitor):
    def __init__(self, path: str, out: Collector) -> None:
        self.path, self.out = path, out
        self.eval_depth = 0  # inside an inference-only branch

    def visit_If(self, node: ast.If) -> None:
        try:
            test = ast.unparse(node.test)
        except Exception:  # unparse of exotic nodes: treat as an ordinary branch
            test = ""
        evaluation = bool(EVAL_BRANCH.search(test))
        self.eval_depth += evaluation
        for child in node.body:
            self.visit(child)
        self.eval_depth -= evaluation
        for child in node.orelse:  # the else of "if not training" is the training path
            self.visit(child)

    def visit_Call(self, node: ast.Call) -> None:
        _call(node, self.path, self.out)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        if not self.eval_depth:
            _assign(node, self.path, self.out)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if not self.eval_depth:
            _assign(node, self.path, self.out)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        _signature(node, self.path, self.out)  # def __init__(..., hidden_dropout_prob=0.1)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef


def _signature(node: ast.FunctionDef | ast.AsyncFunctionDef, path: str, out: Collector) -> None:
    args = node.args
    positional = args.posonlyargs + args.args
    # Defaults belong to the last positional arguments; same lengths by construction.
    pairs = list(
        zip(positional[len(positional) - len(args.defaults) :], args.defaults, strict=True)
    )
    kw = zip(args.kwonlyargs, args.kw_defaults, strict=True)
    pairs += [(a, d) for a, d in kw if d is not None]
    for arg, default in pairs:
        if HP_NAME.search(arg.arg):
            try:
                out.add(
                    arg.arg, literal(default), path, getattr(default, "lineno", None), "default"
                )
            except ValueError:
                continue


def _func_name(call: ast.Call) -> str:
    f = call.func
    if isinstance(f, ast.Attribute):
        return f.attr
    if isinstance(f, ast.Name):
        return f.id
    return ""


def _kw(call: ast.Call, name: str) -> ast.AST | None:
    return next((k.value for k in call.keywords if k.arg == name), None)


def _call(call: ast.Call, path: str, out: Collector) -> None:
    fn = _func_name(call)
    line = getattr(call, "lineno", None)
    try:
        if fn in ("add_argument", "option"):  # argparse / click
            flags = [
                a.value
                for a in call.args
                if isinstance(a, ast.Constant) and isinstance(a.value, str)
            ]
            flags = [f for f in flags if f.startswith("-")]
            if flags and _kw(call, "default") is not None:
                name = max(flags, key=len).lstrip("-")
                out.add(
                    name,
                    literal(_kw(call, "default")),
                    path,
                    line,
                    "argparse" if fn == "add_argument" else "click",
                )
        elif fn in FLAG_FUNCS and call.args:  # absl / tf.flags: DEFINE_float("lr", 3e-4, ...)
            flag = literal(call.args[0])
            default = call.args[1] if len(call.args) > 1 else _kw(call, "default")
            if isinstance(flag, str):
                out.add(flag, literal(default), path, line, "flags")
        elif fn == "add_hparam" and len(call.args) >= 2:  # tensor2tensor HParams
            hparam = literal(call.args[0])
            if isinstance(hparam, str):
                out.add(hparam, literal(call.args[1]), path, line, "hparams")
        else:  # Optimizer(..., weight_decay_rate=0.01), HParams(lr=...), dict(epochs=...)
            for k in call.keywords:
                if k.arg and HP_NAME.search(k.arg):
                    try:
                        out.add(k.arg, literal(k.value), path, line, "kwarg")
                    except ValueError:
                        continue
    except ValueError:
        return


def _assign(node: ast.Assign | ast.AnnAssign, path: str, out: Collector) -> None:
    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
    value: ast.AST | None = node.value
    if value is None:
        return
    if isinstance(value, ast.Call) and _func_name(value) == "field":  # dataclass field(default=)
        value = _kw(value, "default")
    for target in targets:
        if isinstance(target, ast.Name):
            name, kind = target.id, "constant"
        elif isinstance(target, ast.Attribute):  # hparams.learning_rate = 0.2
            name, kind = target.attr, "attr"
        else:
            continue
        if not HP_NAME.search(name):
            continue
        try:
            out.add(name, literal(value), path, getattr(node, "lineno", None), kind)
        except ValueError:
            continue


# ------------------------------------------------------------------ configs / README


def _flatten(data: object, prefix: str, path: str, out: Collector, depth: int = 0) -> None:
    if depth > 8 or len(out.params) >= MAX_PARAMS:
        return
    if isinstance(data, dict):
        for k, v in list(data.items())[:500]:
            _flatten(v, f"{prefix}.{k}" if prefix else str(k), path, out, depth + 1)
    elif isinstance(data, list):
        if data and all(isinstance(x, (int, float)) for x in data) and len(data) <= 8:
            out.add(prefix, data, path, None, "config")
    elif isinstance(data, (int, float, str, bool)) and prefix:
        out.add(prefix, data, path, None, "config")


def scan_config(path: str, text: str, out: Collector) -> None:
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext in (".yaml", ".yml"):
            import yaml

            for doc in yaml.safe_load_all(text):
                _flatten(doc, "", path, out)
        elif ext == ".json":
            _flatten(json.loads(text), "", path, out)
        elif ext == ".toml":
            try:
                import tomllib
            except ImportError:  # Python < 3.11 in the sandbox image
                import tomli as tomllib  # type: ignore[no-redef,import-not-found,unused-ignore]
            _flatten(tomllib.loads(text), "", path, out)
        else:  # .gin / .cfg: "name = value" lines
            for n, line in enumerate(text.splitlines(), 1):
                m = re.match(r"^\s*([\w.]+(?:/[\w.]+)?)\s*[=:]\s*([^#\s][^#]*?)\s*$", line)
                if m and HP_NAME.search(m.group(1).split(".")[-1]):
                    out.add(m.group(1), m.group(2), path, n, "config")
    except Exception as exc:  # malformed configs are common; never fail the scan
        out.errors.append(f"{os.path.relpath(path, out.root)}: {type(exc).__name__}")


def scan_readme(path: str, text: str, out: Collector) -> None:
    in_code = False
    for n, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code or line.startswith(("    ", "\t", "$ ", "python", "bash")):
            for m in README_FLAG.finditer(line):
                out.add(m.group(1), m.group(2).rstrip(";,"), path, n, "readme")


# ------------------------------------------------------------------ walk


def scan(root: str) -> dict[str, object]:
    out = Collector(root)
    started = time.monotonic()
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fname in filenames:
            if out.files >= MAX_FILES or time.monotonic() - started > TIME_BUDGET_S:
                out.errors.append("scan stopped early (file or time budget)")
                return _result(out)
            path = os.path.join(dirpath, fname)
            if os.path.islink(path):
                continue  # a symlink can point outside the repository
            if re.match(r"(test_.*|.*_test)\.py$", fname):
                continue  # unit tests set arbitrary values
            ext = os.path.splitext(fname)[1].lower()
            is_readme = fname.lower().startswith("readme")
            if ext != ".py" and ext not in CONFIG_EXT and not is_readme:
                continue
            try:
                size = os.path.getsize(path)
                limit = MAX_FILE_BYTES if ext == ".py" or is_readme else MAX_CONFIG_BYTES
                if size > limit:
                    continue
                with open(path, encoding="utf-8", errors="replace") as f:
                    text = f.read()
            except OSError:
                continue
            out.files += 1
            if ext == ".py":
                scan_python(path, text, out)
            elif is_readme:
                scan_readme(path, text, out)
            else:
                scan_config(path, text, out)
    return _result(out)


def _result(out: Collector) -> dict[str, object]:
    return {"params": out.params, "files_scanned": out.files, "errors": out.errors[:50]}


if __name__ == "__main__":
    print(json.dumps(scan(sys.argv[1])))
