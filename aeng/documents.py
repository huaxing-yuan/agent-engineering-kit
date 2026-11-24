from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

import yaml


def today() -> str:
    return date.today().isoformat()


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    if not value:
        raise ValueError("A non-empty ASCII name is required")
    return value


def parse_document(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8-sig")
    match = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)(.*)$", text, re.S)
    if not match:
        raise ValueError(f"{path}: missing YAML frontmatter")
    data = yaml.safe_load(match.group(1)) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: frontmatter must be a mapping")
    return data, match.group(2)


def dump_document(data: dict[str, Any], body: str) -> str:
    front = yaml.safe_dump(data, sort_keys=False, allow_unicode=True).rstrip()
    return f"---\n{front}\n---\n\n{body.lstrip()}"


def write_document(path: Path, data: dict[str, Any], body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_document(data, body), encoding="utf-8", newline="\n")


def read_h1(path: Path) -> str:
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def render_template(text: str, values: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in values:
            raise ValueError(f"Missing template value: {key}")
        return values[key]

    return re.sub(r"\{\{([A-Z0-9_]+)\}\}", replace, text)


def replace_marked_section(text: str, start: str, end: str, content: str) -> str:
    pattern = re.compile(rf"{re.escape(start)}.*?{re.escape(end)}", re.S)
    replacement = f"{start}\n{content.rstrip()}\n{end}"
    if pattern.search(text):
        return pattern.sub(lambda _: replacement, text, count=1)
    return text.rstrip() + f"\n\n{start}\n{content.rstrip()}\n{end}\n"


def _split_cells(line: str) -> list[str]:
    stripped = line.strip().strip("|")
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", stripped)]


def parse_table(text: str, heading: str) -> tuple[list[str], list[dict[str, str]]]:
    lines = text.splitlines()
    try:
        index = next(i for i, line in enumerate(lines) if line.strip() == f"## {heading}")
    except StopIteration:
        return [], []
    headers: list[str] = []
    rows: list[dict[str, str]] = []
    for line in lines[index + 1 :]:
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if not stripped.startswith("|"):
            continue
        cells = _split_cells(stripped)
        if all(re.fullmatch(r":?-{3,}:?", cell or " ") for cell in cells):
            continue
        if not headers:
            headers = [cell.lower() for cell in cells]
            continue
        if len(cells) != len(headers):
            continue
        rows.append(dict(zip(headers, cells)))
    return headers, rows


def set_table_row(text: str, heading: str, row_id: str, updates: dict[str, str]) -> str:
    lines = text.splitlines()
    try:
        index = next(i for i, line in enumerate(lines) if line.strip() == f"## {heading}")
    except StopIteration:
        raise ValueError(f"Missing table section: {heading}")
    headers: list[str] = []
    id_column = 0
    for i in range(index + 1, len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith("## "):
            break
        if not stripped.startswith("|"):
            continue
        cells = _split_cells(stripped)
        if all(re.fullmatch(r":?-{3,}:?", cell or " ") for cell in cells):
            continue
        if not headers:
            headers = [cell.lower() for cell in cells]
            id_column = headers.index("id")
            continue
        if len(cells) != len(headers):
            continue
        if cells[id_column] != row_id:
            continue
        for key, value in updates.items():
            if key not in headers:
                raise ValueError(f"Unknown slice column: {key}")
            cells[headers.index(key)] = str(value).replace("|", "\\|")
        lines[i] = "| " + " | ".join(cells) + " |"
        return "\n".join(lines) + "\n"
    raise ValueError(f"No row with id {row_id!r} in {heading}")


def append_table_row(text: str, heading: str, row: dict[str, str]) -> str:
    lines = text.splitlines()
    try:
        index = next(i for i, line in enumerate(lines) if line.strip() == f"## {heading}")
    except StopIteration:
        raise ValueError(f"Missing table section: {heading}")
    headers: list[str] = []
    insert_at = index + 1
    for i in range(index + 1, len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith("## "):
            insert_at = i
            break
        if not stripped.startswith("|"):
            continue
        cells = _split_cells(stripped)
        if all(re.fullmatch(r":?-{3,}:?", cell or " ") for cell in cells):
            continue
        if not headers:
            headers = [cell.lower() for cell in cells]
        insert_at = i + 1
    if not headers:
        raise ValueError(f"Missing table header in {heading}")
    missing = set(row) - set(headers)
    if missing:
        raise ValueError(f"Missing table columns: {sorted(missing)}")
    lines.insert(insert_at, "| " + " | ".join(row[key].replace("|", "\\|") for key in headers) + " |")
    return "\n".join(lines) + "\n"
