"""
differ.py
---------
Core diffing logic untuk reqtrace.

Menyimpan snapshot response terakhir per endpoint (method + url),
lalu membandingkan jika endpoint yang sama dipanggil kembali.
"""

from typing import Any
from dataclasses import dataclass, field


# ------------------------------------------------------------------
# Data structures
# ------------------------------------------------------------------


@dataclass
class DiffEntry:
    """Satu baris hasil diff."""

    symbol: str  # "+" ditambah | "-" hilang | "~" berubah
    path: str  # lokasi field, e.g. "data[0].email"
    old_value: Any = None
    new_value: Any = None

    def __str__(self) -> str:
        if self.symbol == "+":
            return f"+ {self.path:<30} {self.new_value!r}"
        elif self.symbol == "-":
            return f"- {self.path:<30} {self.old_value!r}"
        else:
            return f"~ {self.path:<30} {self.old_value!r} → {self.new_value!r}"


@dataclass
class DiffResult:
    """Hasil lengkap perbandingan dua response."""

    method: str
    url: str
    entries: list[DiffEntry] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return len(self.entries) > 0

    @property
    def added(self) -> list[DiffEntry]:
        return [e for e in self.entries if e.symbol == "+"]

    @property
    def removed(self) -> list[DiffEntry]:
        return [e for e in self.entries if e.symbol == "-"]

    @property
    def changed(self) -> list[DiffEntry]:
        return [e for e in self.entries if e.symbol == "~"]


# ------------------------------------------------------------------
# Snapshot store
# ------------------------------------------------------------------


class SnapshotStore:
    """
    Menyimpan response body terakhir per endpoint.
    Key: "{METHOD} {url}", contoh: "GET /users"
    """

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    def _key(self, method: str, url: str) -> str:
        return f"{method} {url}"

    def has(self, method: str, url: str) -> bool:
        return self._key(method, url) in self._store

    def get(self, method: str, url: str) -> Any:
        return self._store.get(self._key(method, url))

    def set(self, method: str, url: str, response_body: Any) -> None:
        self._store[self._key(method, url)] = response_body

    def clear(self) -> None:
        self._store.clear()


# ------------------------------------------------------------------
# Diff engine
# ------------------------------------------------------------------


def compute_diff(
    method: str,
    url: str,
    old_body: Any,
    new_body: Any,
) -> DiffResult:
    """
    Bandingkan dua response body dan kembalikan DiffResult.
    Mendukung dict, list, dan nilai primitif.
    """
    result = DiffResult(method=method, url=url)
    _diff_values(old_body, new_body, path="", entries=result.entries)
    return result


def _diff_values(
    old: Any,
    new: Any,
    path: str,
    entries: list[DiffEntry],
    max_depth: int = 10,
    depth: int = 0,
) -> None:
    """Rekursif bandingkan dua nilai."""
    if depth > max_depth:
        return

    if type(old) != type(new):
        entries.append(DiffEntry("~", path or "root", old, new))
        return

    if isinstance(old, dict) and isinstance(new, dict):
        _diff_dicts(old, new, path, entries, max_depth, depth)
    elif isinstance(old, list) and isinstance(new, list):
        _diff_lists(old, new, path, entries, max_depth, depth)
    elif old != new:
        entries.append(DiffEntry("~", path or "root", old, new))


def _diff_dicts(
    old: dict,
    new: dict,
    path: str,
    entries: list[DiffEntry],
    max_depth: int,
    depth: int,
) -> None:
    all_keys = set(old) | set(new)
    for key in sorted(all_keys):
        child_path = f"{path}.{key}" if path else key
        if key not in old:
            entries.append(DiffEntry("+", child_path, new_value=new[key]))
        elif key not in new:
            entries.append(DiffEntry("-", child_path, old_value=old[key]))
        else:
            _diff_values(old[key], new[key], child_path, entries, max_depth, depth + 1)


def _diff_lists(
    old: list,
    new: list,
    path: str,
    entries: list[DiffEntry],
    max_depth: int,
    depth: int,
) -> None:
    max_len = max(len(old), len(new))
    for i in range(max_len):
        child_path = f"{path}[{i}]"
        if i >= len(old):
            entries.append(DiffEntry("+", child_path, new_value=new[i]))
        elif i >= len(new):
            entries.append(DiffEntry("-", child_path, old_value=old[i]))
        else:
            _diff_values(old[i], new[i], child_path, entries, max_depth, depth + 1)
