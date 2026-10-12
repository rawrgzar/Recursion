#!/usr/bin/env python3
"""Compile the small Recursion report description into a standalone HTML report."""

from __future__ import annotations

import html
import math
import re
import sys
from pathlib import Path


TASK_DIR = Path(__file__).resolve().parent.parent / "abstract-report-interface"
DEFAULT_INPUT = TASK_DIR / "source" / "field-notes.rec"
DEFAULT_OUTPUT = TASK_DIR / "output" / "field-notes.html"
BOOTSTRAP_CSS = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css"


def fail(path: Path, line: int, message: str) -> ValueError:
    return ValueError(f"{path}:{line}: {message}")


def unquote(value: str, path: Path, line: int) -> str:
    match = re.fullmatch(r'"((?:[^"\\]|\\["\\])*)"', value)
    if not match:
        raise fail(path, line, 'expected quoted text (escape " and \\ with \\)')
    return match.group(1).replace(r'\"', '"').replace(r'\\', '\\')


def parse(path: Path) -> dict:
    report: dict = {"nav": [], "metrics": [], "columns": [], "rows": [], "details": {}, "activity": [], "profession_tabs": [], "chart": {"series": [], "points": []}, "callout": {}, "table": {"filters": []}, "heading": {}, "feature": {}, "footer": {}}
    seen: set[str] = set()
    block = ""
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        if "\t" in raw:
            raise fail(path, number, "tabs are not allowed for indentation")
        indent = len(raw) - len(raw.lstrip(" "))
        text = raw.strip()
        if indent == 0:
            m = re.fullmatch(r"report (.+)", text)
            if not m or "title" in seen:
                raise fail(path, number, 'expected one report declaration: report "Name"')
            report["title"] = unquote(m.group(1), path, number)
            seen.add("title")
        elif indent == 2:
            m = re.fullmatch(r'(nav|heading|feature|metrics|table|activity|footer|callout|chart|professions)(?: (.+))?', text)
            if not m:
                raise fail(path, number, "expected nav, heading, feature, metrics, table, activity, callout, chart, professions, or footer block")
            block, arg = m.groups()
            if block in {"heading", "feature", "metrics", "table", "activity", "footer", "callout", "chart", "professions"}:
                if block in seen:
                    raise fail(path, number, f"duplicate {block} block")
                seen.add(block)
            if block == "nav" and arg:
                report["brand"] = unquote(arg, path, number)
            elif arg:
                raise fail(path, number, f"{block} does not take a title")
        elif indent == 4:
            if block == "nav":
                m = re.fullmatch(r'link (.+?) -> (.+)', text)
                if not m:
                    raise fail(path, number, 'expected link "Label" -> "#section"')
                label, href = (unquote(v, path, number) for v in m.groups())
                if not re.fullmatch(r"#[A-Za-z][\w-]*", href):
                    raise fail(path, number, "navigation links must target an in-page section")
                report["nav"].append((label, href))
            elif block in {"heading", "feature", "footer", "callout"}:
                m = re.fullmatch(r"([a-z_]+): (.+)", text)
                if not m:
                    raise fail(path, number, "expected a named quoted value")
                key, val = m.groups()
                allowed = {"heading": {"eyebrow", "title", "subtitle", "meta"}, "feature": {"label", "title", "text", "status", "tooltip"}, "footer": {"text"}, "callout": {"title", "text"}}[block]
                if key not in allowed or key in report[block]:
                    raise fail(path, number, f"unknown or duplicate {block} field '{key}'")
                report[block][key] = unquote(val, path, number)
            elif block == "metrics":
                m = re.fullmatch(r'metric (.+?) \| (.+?) \| (.+)', text)
                if not m:
                    raise fail(path, number, 'expected metric "Label" | "Value" | "Note"')
                report["metrics"].append(tuple(unquote(v, path, number) for v in m.groups()))
            elif block == "table":
                m = re.fullmatch(r'([a-z_]+): (.+)', text)
                if m:
                    key, val = m.groups()
                    if key == "filter":
                        report["table"]["filters"].append(unquote(val, path, number))
                        continue
                    if key not in {"title", "search", "page_size"} or key in report["table"]:
                        raise fail(path, number, f"unknown or duplicate table setting '{key}'")
                    setting = unquote(val, path, number) if val.startswith('"') else val
                    if key == "page_size" and not re.fullmatch(r"[1-9][0-9]?", setting):
                        raise fail(path, number, "table.page_size must be an integer from 1 to 99")
                    report["table"][key] = setting
                    continue
                m = re.fullmatch(r'(column|row|detail) (.+)', text)
                if not m:
                    raise fail(path, number, 'expected a table setting, column, row, or detail entry')
                kind, value = m.groups()
                cells = [unquote(v.strip(), path, number) for v in value.split("|")]
                if kind == "column" and len(cells) != 1:
                    raise fail(path, number, 'expected column "Name"')
                if kind == "detail" and len(cells) != 2:
                    raise fail(path, number, 'expected detail "Row key" | "Expanded detail"')
                if kind == "column":
                    report["columns"].append(cells[0])
                elif kind == "row":
                    report["rows"].append(cells)
                else:
                    if cells[0] in report["details"]:
                        raise fail(path, number, f"duplicate detail for row {cells[0]!r}")
                    report["details"][cells[0]] = cells[1]
            elif block == "activity":
                m = re.fullmatch(r'event (.+?) \| (.+?) \| (.+)', text)
                if not m:
                    raise fail(path, number, 'expected event "Time" | "Title" | "Detail"')
                report["activity"].append(tuple(unquote(v, path, number) for v in m.groups()))
            elif block == "chart":
                m = re.fullmatch(r"filter: (.+)", text)
                if m:
                    if "filter" in report["chart"]:
                        raise fail(path, number, "duplicate chart filter")
                    report["chart"]["filter"] = unquote(m.group(1), path, number)
                    continue
                m = re.fullmatch(r"title: (.+)", text)
                if m:
                    if "title" in report["chart"]:
                        raise fail(path, number, "duplicate chart title")
                    report["chart"]["title"] = unquote(m.group(1), path, number)
                    continue
                m = re.fullmatch(r'(series|point) (.+)', text)
                if not m:
                    raise fail(path, number, 'expected series "Label" | "color" or point "Label" | "Value" | "Value"')
                kind, value = m.groups()
                cells = [unquote(v.strip(), path, number) for v in value.split("|")]
                if kind == "series":
                    if len(cells) != 2 or cells[1] not in {"gold", "verdant", "arcane", "coral"}:
                        raise fail(path, number, "chart series needs a label and a supported color token")
                    report["chart"]["series"].append((cells[0], cells[1]))
                else:
                    if len(cells) < 2:
                        raise fail(path, number, "chart point needs a label and numeric values")
                    try:
                        values = [float(value) for value in cells[1:]]
                    except ValueError as exc:
                        raise fail(path, number, "chart values must be non-negative numbers") from exc
                    if any(not math.isfinite(value) or value < 0 for value in values):
                        raise fail(path, number, "chart values must be non-negative numbers")
                    report["chart"]["points"].append((cells[0], values))
            elif block == "professions":
                m = re.fullmatch(r'profession (.+)', text)
                if not m:
                    raise fail(path, number, 'expected profession "Name" | "Type" | "Overview"')
                cells = [unquote(v.strip(), path, number) for v in m.group(1).split("|")]
                if len(cells) != 3:
                    raise fail(path, number, 'expected profession "Name" | "Type" | "Overview"')
                if any(item["name"] == cells[0] for item in report["profession_tabs"]):
                    raise fail(path, number, f"duplicate profession tab {cells[0]!r}")
                report["profession_tabs"].append({"name": cells[0], "type": cells[1], "overview": cells[2], "steps": []})
            else:
                raise fail(path, number, "unexpected field")
        elif indent == 6 and block == "professions":
            m = re.fullmatch(r'step (.+)', text)
            if not m or not report["profession_tabs"]:
                raise fail(path, number, 'expected step "Range" | "Recipe or action" | "Count" | "Materials per craft / note" after a profession')
            cells = [unquote(v.strip(), path, number) for v in m.group(1).split("|")]
            if len(cells) != 4:
                raise fail(path, number, 'expected step "Range" | "Recipe or action" | "Count" | "Materials per craft / note"')
            report["profession_tabs"][-1]["steps"].append(cells)
        else:
            raise fail(path, number, "unexpected indentation")
    required = {"title", "heading", "feature", "metrics", "activity", "footer"}
    if "professions" not in seen:
        required.add("table")
    missing = required - seen
    if missing:
        raise fail(path, 1, "missing required blocks: " + ", ".join(sorted(missing)))
    for key in ("title",):
        if not report[key].strip():
            raise fail(path, 1, f"{key} cannot be empty")
    heading = report.get("heading", {})
    for key in ("title", "eyebrow", "subtitle"):
        if not heading.get(key):
            raise fail(path, 1, f"heading.{key} is required")
    if not report["metrics"] or not report["activity"]:
        raise fail(path, 1, "metrics and activity must not be empty")
    if "table" in seen and (not report["columns"] or not report["rows"]):
        raise fail(path, 1, "table columns and rows must not be empty")
    if any(len(row) != len(report["columns"]) for row in report["rows"]):
        raise fail(path, 1, "each table row must have the same number of cells as columns")
    if "professions" in seen:
        if not report["profession_tabs"] or any(not item["steps"] for item in report["profession_tabs"]):
            raise fail(path, 1, "each profession tab must contain at least one step")
    filter_columns = report["table"]["filters"]
    if len(set(filter_columns)) != len(filter_columns):
        raise fail(path, 1, "table filter columns must be unique")
    for filter_column in filter_columns:
        if filter_column not in report["columns"]:
            raise fail(path, 1, f"table.filter must name a declared column ({filter_column!r})")
    first_values = {row[0] for row in report["rows"]}
    if set(report["details"]) - first_values:
        raise fail(path, 1, "each detail must reference the first cell of a declared row")
    chart = report["chart"]
    if "chart" in seen:
        if not chart["series"] or not chart["points"]:
            raise fail(path, 1, "chart requires at least one series and one point")
        if any(len(point[1]) != len(chart["series"]) for point in chart["points"]):
            raise fail(path, 1, "each chart point must have one value per series")
        if chart.get("filter"):
            if chart["filter"] not in report["columns"]:
                raise fail(path, 1, f"chart.filter must name a declared table column ({chart['filter']!r})")
            if chart["filter"] not in filter_columns:
                raise fail(path, 1, "chart.filter must also be declared as a table filter")
            categories = {row[report["columns"].index(chart["filter"])] for row in report["rows"]}
            if any(label not in categories for label, _ in chart["points"]):
                raise fail(path, 1, "each clickable chart point must match a value in its linked table filter column")
    return report


def render(data: dict) -> str:
    e = lambda s: html.escape(str(s), quote=True)
    def overview_html(value: str) -> str:
        escaped = e(value)
        return re.sub(r"https://www\.wowhead\.com/classic/guide/[a-z0-9-]+", lambda match: f'<a class="source-link" href="{match.group(0)}" target="_blank" rel="noopener noreferrer">Wowhead guide</a>', escaped)
    nav = "\n".join(f'<a class="nav-item" href="{e(href)}">{e(label)}</a>' for label, href in data["nav"])
    metrics = "\n".join(f'<article class="metric" tabindex="0" title="{e(note)}"><span class="metric-label">{e(label)}</span><strong>{e(value)}</strong><small>{e(note)}</small></article>' for label, value, note in data["metrics"])
    table = data["table"]
    page_size = int(table.get("page_size", 8))
    filter_indices = {name: data["columns"].index(name) for name in table["filters"]}
    detail_column = bool(data["details"])
    headers = "".join(f'<th scope="col" aria-sort="none"><button class="sort-button" type="button" data-sort="{index}">{e(col)} <span aria-hidden="true">↕</span></button></th>' for index, col in enumerate(data["columns"]))
    if detail_column:
        headers += '<th scope="col" class="detail-heading">Inspect</th>'
    status_col = next((i for i, col in enumerate(data["columns"]) if col.casefold() == "status"), -1)
    def table_cell(index: int, cell: str) -> str:
        content = e(cell)
        if index == status_col:
            value = cell.casefold()
            status_class = "ended" if "ended" in value else "current" if "current" in value else "future" if "future" in value or "upcoming" in value else "none" if value in {"none", "no estimate"} else "review" if "review" in value else "queued" if "queued" in value else "complete" if value in {"complete", "ready", "active", "done"} else "review"
            content = f'<span class="tag {status_class}">{content}</span>'
        return f'<td tabindex="0" title="{e(cell)}">{content}</td>'
    rows = "\n".join("<tr>" + "".join(table_cell(i, cell) for i, cell in enumerate(row)) + (f'<td class="detail-cell"><details><summary>Inspect</summary><div class="record-detail">{e(data["details"][row[0]])}</div></details></td>' if row[0] in data["details"] else '<td class="detail-cell">—</td>' if detail_column else "") + "</tr>" for row in data["rows"])
    events = "\n".join(f'<li class="event"><time>{e(time)}</time><div><strong>{e(title)}</strong><p>{e(detail)}</p></div></li>' for time, title, detail in data["activity"])
    h, f = data["heading"], data["feature"]
    filters = []
    for filter_index, filter_name in enumerate(table["filters"]):
        column_index = filter_indices[filter_name]
        options = "".join(f'<option value="{e(value)}">{e(value)}</option>' for value in sorted({row[column_index] for row in data["rows"]}, key=str.casefold))
        filters.append(f'<label class="visually-hidden" for="recordFilter{filter_index}">Filter by {e(filter_name)}</label><select id="recordFilter{filter_index}" class="report-select" data-report-filter data-filter-name="{e(filter_name)}" data-filter-column="{column_index}"><option value="">All {e(filter_name.lower())}</option>{options}</select>')
    filters_html = "".join(filters)
    callout = ""
    if data["callout"]:
        c = data["callout"]
        callout = f'<aside class="callout"><span class="callout-mark" aria-hidden="true">✦</span><div><strong>{e(c.get("title", "Context"))}</strong><p>{e(c.get("text", ""))}</p></div></aside>'
    chart_html = ""
    if data["chart"]["series"]:
        chart = data["chart"]
        max_value = max((value for _, values in chart["points"] for value in values), default=1) or 1
        legend = "".join(f'<span><i class="legend-swatch {color}"></i>{e(label)}</span>' for label, color in chart["series"])
        plot_rows = []
        for label, values in chart["points"]:
            bars = "".join(f'<span class="plot-series"><span class="plot-name">{e(series_label)}</span><span class="plot-track"><i class="plot-bar {color}" style="width:{min(100, value / max_value * 100):.2f}%"></i></span><strong>{e(format(value, "g"))}</strong></span>' for value, (series_label, color) in zip(values, chart["series"]))
            filter_attr = f' data-chart-filter="{e(label)}" data-chart-column="{e(chart["filter"])}" aria-pressed="false"' if chart.get("filter") else ""
            plot_rows.append(f'<button class="plot-row" type="button"{filter_attr}><span class="plot-label">{e(label)}</span><span class="plot-values">{bars}</span></button>' if chart.get("filter") else f'<div class="plot-row"><span class="plot-label">{e(label)}</span><span class="plot-values">{bars}</span></div>')
        chart_html = f'<section class="panel chart-panel" id="distribution" aria-labelledby="distribution-title"><div class="section-head"><h2 id="distribution-title">{e(chart.get("title", "Comparison"))}</h2><span>COMPARISON</span></div><div class="chart-legend">{legend}</div><div class="plot">{"".join(plot_rows)}</div></section>'
    profession_html = ""
    if data["profession_tabs"]:
        tab_buttons = []
        tab_panels = []
        for index, profession in enumerate(data["profession_tabs"]):
            slug = re.sub(r"[^a-z0-9]+", "-", profession["name"].casefold()).strip("-")
            active = index == 0
            tab_buttons.append(f'<button class="profession-tab" id="tab-{slug}" type="button" role="tab" aria-controls="panel-{slug}" aria-selected="{str(active).lower()}" tabindex="{0 if active else -1}" data-profession-tab="{slug}">{e(profession["name"])}</button>')
            step_rows = "".join(f'<tr><td class="skill-range">{e(step[0])}</td><td class="recipe-name">{e(step[1])}</td><td class="craft-count">{e(step[2])}</td><td class="step-materials">{e(step[3])}</td></tr>' for step in profession["steps"])
            tab_panels.append(f'<section class="profession-panel" id="panel-{slug}" role="tabpanel" aria-labelledby="tab-{slug}" data-profession-panel="{slug}"{" hidden" if not active else ""}><div class="profession-summary"><span>{e(profession["type"])}</span><p>{overview_html(profession["overview"])}</p></div><div class="table-wrap"><table class="step-table"><thead><tr><th scope="col">Skill range</th><th scope="col">Recipe or action</th><th scope="col">Make / gather</th><th scope="col">Materials for row / route note</th></tr></thead><tbody>{step_rows}</tbody></table></div></section>')
        profession_html = f'<section class="profession-guide" id="records" aria-labelledby="profession-guide-title"><div class="section-head"><div><span class="eyebrow">CHOOSE A PROFESSION</span><h2 id="profession-guide-title">Step-by-step leveling routes</h2></div><span>{len(data["profession_tabs"])} GUIDES</span></div><div class="profession-tabs" role="tablist" aria-label="Profession leveling guides">{"".join(tab_buttons)}</div>{"".join(tab_panels)}</section>'
    records_html = profession_html or f'<section id="records" aria-labelledby="records-title"><div class="section-head"><h2 id="records-title">{e(table.get("title", "Record register"))}</h2><span>{len(data["rows"]):02d} ENTRIES</span></div><div class="table-tools"><label class="visually-hidden" for="recordSearch">Search records</label><input class="report-input" id="recordSearch" type="search" placeholder="{e(table.get("search", "Search records"))}" data-record-search>{filters_html}<span class="table-count" data-record-count></span></div><div class="table-wrap"><table data-report-table data-page-size="{page_size}" data-has-details="{str(detail_column).lower()}"><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table></div><div class="table-pager"><button class="page-button" data-page-prev type="button">Previous</button><span data-page-label></span><button class="page-button" data-page-next type="button">Next</button></div></section>'
    nav_html = f'<nav class="topbar"><a class="brand" href="#top"><i aria-hidden="true">◈</i>{e(data.get("brand", data["title"]))}</a><div class="nav-links">{nav}</div><a class="utility" href="#records" title="Search report records">⌕ <span>Search records</span></a><span class="avatar" title="Report overview">◉</span></nav>'
    return f'''<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(data["title"])}</title><link href="{BOOTSTRAP_CSS}" rel="stylesheet">
<style>
:root{{--ink:#e8edf5;--muted:#a9bdd1;--line:#2b3d52;--panel:#121d2e;--panel2:#101c2d;--gold:#f5bb69;--verdant:#7bd2b3;--arcane:#70d5f1;--coral:#f27f91;--bg:#0b1220}}
*{{box-sizing:border-box}} html{{scroll-behavior:smooth}} body{{margin:0;min-height:100vh;color:var(--ink);background:radial-gradient(circle at 90% 0,#17334a 0,var(--bg) 35%);font:15px/1.55 Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;letter-spacing:.008em;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;font-feature-settings:"kern" 1,"liga" 1}}
body:before{{content:"";position:fixed;inset:0;pointer-events:none;opacity:.12;background-image:linear-gradient(#9eaabd0a 1px,transparent 1px),linear-gradient(90deg,#9eaabd0a 1px,transparent 1px);background-size:44px 44px;mask-image:linear-gradient(to bottom,black,transparent 78%)}}
.shell{{width:min(1600px,calc(100% - 48px));margin:auto;position:relative}}.topbar{{height:72px;margin-inline:calc((min(1600px,100vw - 48px) - 100vw)/2);padding-inline:max(24px,calc((100vw - 1600px)/2));background:#0e1928ea;border-bottom:1px solid var(--line);display:flex;align-items:center;gap:30px}}.brand{{display:flex;align-items:center;gap:12px;text-decoration:none;color:var(--ink);font:650 14px/1.2 Inter,ui-sans-serif,system-ui,sans-serif;white-space:nowrap}}.brand i{{width:38px;height:38px;display:grid;place-items:center;border-radius:10px;background:#174259;color:#a5eaf8;font-style:normal;font-size:20px}}.nav-links{{display:flex;align-self:stretch;gap:25px}}.nav-item{{display:grid;align-items:center;color:#a9bdd1;text-decoration:none;font-size:13px;position:relative;transition:color .18s}}.nav-item:hover{{color:var(--arcane)}}.nav-item:first-child{{color:var(--arcane)}}.nav-item:first-child:after{{position:absolute;content:"";height:2px;background:var(--arcane);bottom:0;left:0;right:0}}.utility{{margin-left:auto;color:#b8cadd;border:1px solid #34475e;padding:7px 11px;border-radius:7px;font-size:12px;text-decoration:none}}.utility:hover{{border-color:var(--arcane);color:#fff}}.avatar{{width:29px;height:29px;border:1px solid #42657a;border-radius:50%;display:grid;place-items:center;color:var(--arcane);font:12px ui-sans-serif}}
.intro{{padding:38px 0 24px;max-width:1120px}}.eyebrow,.section-kicker{{font:700 11px/1.4 Inter,ui-sans-serif,system-ui,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#8fcee1}}h1{{font:700 clamp(38px,4vw,56px)/1.08 Inter,ui-sans-serif,system-ui,sans-serif;letter-spacing:-.04em;margin:10px 0 12px;max-width:22ch;text-wrap:balance;color:var(--ink)}}.subtitle{{font-size:16px;line-height:1.6;color:#b9c9d9;max-width:780px;margin:0}}.meta{{display:flex;gap:20px;margin-top:16px;color:var(--muted);font:500 11px/1.5 ui-monospace,Consolas,monospace;letter-spacing:.05em}}.meta span+span:before{{content:"";display:inline-block;width:4px;height:4px;border-radius:50%;background:var(--gold);margin:0 12px 2px 0}}
.feature{{position:relative;display:grid;grid-template-columns:1fr auto;align-items:center;gap:24px;padding:23px 25px;background:var(--panel);border:1px solid var(--line);border-radius:16px;box-shadow:0 12px 30px #050b1740;transition:border-color .2s,background .2s}}.feature:hover{{border-color:#70d5f177;background:#15243a}}.feature-label{{color:#8fcee1;font:700 11px/1.4 Inter,ui-sans-serif,system-ui,sans-serif;letter-spacing:.13em;text-transform:uppercase}}.feature h2{{font:650 22px/1.3 Inter,ui-sans-serif,system-ui,sans-serif;margin:7px 0 5px}}.feature p{{color:#b9c9d9;margin:0;max-width:900px;font-size:14px}}.feature-side{{text-align:right;color:var(--verdant);font:650 11px/1.5 Inter,ui-sans-serif,system-ui,sans-serif;letter-spacing:.07em;text-transform:uppercase}}.dot{{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--verdant);margin-right:8px;box-shadow:0 0 10px #7bd2b388}}
.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:17px 0 20px;border:0}}.metric{{padding:17px 18px 14px;min-height:112px;border:1px solid var(--line);border-radius:16px;background:var(--panel);box-shadow:0 12px 30px #050b1740;transition:border-color .18s,transform .18s;outline:none}}.metric:first-child{{padding-left:18px}}.metric:last-child{{border:1px solid var(--line)}}.metric:hover,.metric:focus{{border-color:#70d5f177;transform:translateY(-2px)}}.metric-label{{display:block;color:#b8cadd;text-transform:none;letter-spacing:0;font:500 13px/1.5 Inter,ui-sans-serif,system-ui,sans-serif}}.metric strong{{display:block;font:700 30px/1.15 Inter,ui-sans-serif,system-ui,sans-serif;margin:7px 0 4px;letter-spacing:-.04em;color:var(--arcane)}}.metric:nth-child(3n+2) strong{{color:var(--gold)}}.metric:nth-child(3n) strong{{color:var(--verdant)}}.metric small{{color:var(--muted);font-size:12px;line-height:1.5}}
.callout{{display:flex;gap:14px;margin:0 0 17px;padding:13px 16px;border:1px solid var(--line);border-left:3px solid var(--arcane);background:#152b3b;border-radius:0 10px 10px 0;color:var(--ink)}}.callout-mark{{color:var(--arcane);font-size:17px;line-height:1.3}}.callout strong{{font-size:13px;color:#c5edfa}}.callout p{{margin:4px 0 0;color:var(--muted);font-size:13px;line-height:1.55}}
.panel{{border:1px solid var(--line);border-radius:16px;background:var(--panel);box-shadow:0 12px 30px #050b1740}}.chart-panel{{padding:18px 20px;margin:0 0 20px}}.chart-legend{{display:flex;gap:20px;flex-wrap:wrap;margin:13px 0;color:var(--muted);font-size:12px}}.chart-legend span{{display:flex;align-items:center;gap:8px}}.legend-swatch{{width:9px;height:9px;border-radius:2px}}.legend-swatch.gold,.plot-bar.gold{{background:var(--gold)}}.legend-swatch.verdant,.plot-bar.verdant{{background:var(--verdant)}}.legend-swatch.arcane,.plot-bar.arcane{{background:var(--arcane)}}.legend-swatch.coral,.plot-bar.coral{{background:var(--coral)}}.plot-row{{display:grid;width:100%;grid-template-columns:minmax(120px,.65fr) minmax(0,1.35fr);gap:23px;align-items:center;padding:13px 10px;border:0;border-top:1px solid #2b3d52;background:transparent;text-align:left;color:inherit;font:inherit;transition:background .15s,border-color .15s;cursor:pointer}}.plot-row:hover,.plot-row:focus-visible{{background:#1a3045;outline:2px solid var(--arcane);outline-offset:-2px}}.plot-row.active{{background:#1c4b64;box-shadow:inset 3px 0 var(--arcane)}}.plot-label{{font-size:13px;color:#bfd5e2}}.plot-values{{display:grid;gap:8px}}.plot-series{{display:grid;grid-template-columns:minmax(82px,.42fr) minmax(80px,1fr) 40px;gap:12px;align-items:center}}.plot-name{{color:#a9bdd1;font-size:11px}}.plot-track{{height:9px;background:#203249;overflow:hidden;border-radius:4px}}.plot-bar{{display:block;height:100%;min-width:2px;border-radius:4px;box-shadow:0 0 10px currentColor}}.plot-series strong{{text-align:right;color:#e8edf5;font:700 11px ui-monospace}}
.lower{{display:grid;grid-template-columns:minmax(0,1.7fr) minmax(270px,.8fr);gap:20px}}.section-head{{display:flex;align-items:baseline;justify-content:space-between;padding-bottom:11px;border-bottom:1px solid var(--line);margin-bottom:3px}}.section-head h2{{font:650 19px/1.3 Inter,ui-sans-serif,system-ui,sans-serif;margin:0;color:var(--ink)}}.section-head span{{font:600 10px ui-monospace;color:var(--muted);letter-spacing:.08em}}.table-wrap{{overflow:auto}}table{{width:100%;border-collapse:collapse;white-space:nowrap}}th{{text-align:left;color:#acc4d6;text-transform:uppercase;letter-spacing:.07em;font:650 11px Inter,ui-sans-serif,system-ui,sans-serif;padding:12px 10px;border-bottom:1px solid var(--line)}}td{{padding:13px 10px;border-bottom:1px solid #2b3d52;color:#e8edf5;font-size:13px;transition:background .16s;outline:none}}td:first-child{{font:500 12px ui-monospace,Consolas,monospace;color:#a4e7f6}}tbody tr:hover td,td:focus{{background:#1a3045}}tbody tr:last-child td{{border-bottom:0}}.tag{{display:inline-flex;align-items:center;gap:7px;border:0;border-radius:100px;padding:4px 9px;color:#c8f4e1;background:#205043;font:700 10px Inter,ui-sans-serif,system-ui,sans-serif;text-transform:none;letter-spacing:0}}.tag:before{{content:"";width:6px;height:6px;background:var(--verdant);border-radius:50%}}.tag.review{{color:#ffe5bb;background:#59472b}}.tag.review:before{{background:var(--gold)}}.tag.queued{{color:#c5edfa;background:#21465b}}.tag.queued:before{{background:var(--arcane)}}.mono{{font-family:ui-monospace,monospace;color:#a8b6c4}}
.tag.ended{{color:#ffd2d9;background:#58303d}}.tag.ended:before{{background:var(--coral)}}.tag.current{{color:#ffe1af;background:#5b4429}}.tag.current:before{{background:var(--gold)}}.tag.future{{color:#c8f4e1;background:#205043}}.tag.future:before{{background:var(--verdant)}}.tag.none{{color:#d4dfed;background:#344159}}.tag.none:before{{background:#a9bdd1}}
.table-tools{{display:flex;gap:9px;flex-wrap:wrap;align-items:center;padding:12px 0}}.report-input,.report-select{{min-height:38px;padding:7px 11px;border:1px solid #34475e;border-radius:7px;background:#101c2d;color:#f2f7fc;font:13px Inter,ui-sans-serif,system-ui,sans-serif}}.report-input{{flex:1;min-width:190px}}.report-input::placeholder{{color:#8da3bb}}.report-input:focus,.report-select:focus{{outline:0;border-color:var(--arcane);box-shadow:0 0 0 .2rem #70d5f133}}.table-count{{margin-left:auto;color:var(--muted);font-size:11px}}.sort-button{{border:0;background:none;color:inherit;padding:0;font:inherit;text-transform:inherit;letter-spacing:inherit;cursor:pointer}}.sort-button:hover,.sort-button:focus-visible{{color:var(--arcane)}}.detail-heading{{width:80px}}.detail-cell{{white-space:normal;min-width:100px}}.detail-cell details summary{{color:var(--arcane);font-size:11px;cursor:pointer}}.record-detail{{position:relative;z-index:1;min-width:230px;max-width:360px;padding:12px;margin-top:8px;white-space:normal;background:#0d1a2b;border:1px solid #31485f;border-radius:9px;color:#c5d4e3;font-size:12px;line-height:1.6}}
.table-pager{{display:flex;justify-content:flex-end;align-items:center;gap:13px;padding-top:14px;color:var(--muted);font-size:11px}}.page-button{{border:1px solid #42657a;background:#173449;color:#bceafa;border-radius:7px;padding:6px 10px;cursor:pointer}}.page-button:hover:not(:disabled){{background:#205577;color:#fff}}.page-button:disabled{{opacity:.42;cursor:default}}.empty-row td{{padding:28px;text-align:center;color:var(--muted)}}
.profession-guide{{min-width:0;padding:20px;border:1px solid var(--line);border-radius:16px;background:var(--panel);box-shadow:0 12px 30px #050b1740}}.profession-tabs{{display:flex;gap:8px;overflow-x:auto;padding:16px 0 12px;border-bottom:1px solid var(--line);scrollbar-color:#42657a #101c2d}}.profession-tab{{flex:0 0 auto;border:1px solid #34475e;border-radius:999px;background:#101c2d;color:#b9c9d9;padding:8px 14px;font:600 12px Inter,ui-sans-serif,system-ui,sans-serif;cursor:pointer;transition:color .15s,border-color .15s,background .15s}}.profession-tab:hover,.profession-tab:focus-visible{{outline:2px solid #70d5f188;outline-offset:2px;color:#fff}}.profession-tab[aria-selected="true"]{{border-color:#70d5f1;background:#173b4e;color:#bceafa;box-shadow:inset 0 -2px #70d5f1}}.profession-panel{{padding-top:15px}}.profession-panel[hidden]{{display:none}}.profession-summary{{display:flex;align-items:flex-start;gap:13px;margin-bottom:13px;color:#b9c9d9}}.profession-summary>span{{flex:0 0 auto;color:var(--gold);font:700 10px/1.5 ui-monospace,Consolas,monospace;text-transform:uppercase;letter-spacing:.07em;padding:5px 8px;border:1px solid #59472b;border-radius:6px;background:#2d281f}}.profession-summary p{{margin:2px 0 0;font-size:13px}}.step-table{{white-space:normal;table-layout:auto}}.step-table th{{white-space:nowrap}}.step-table td{{vertical-align:top;line-height:1.5}}.step-table .skill-range{{min-width:95px;color:var(--gold);font:650 12px ui-monospace,Consolas,monospace;white-space:nowrap}}.step-table .recipe-name{{min-width:185px;color:#e8edf5;font-weight:600}}.step-table .craft-count{{min-width:105px;color:var(--verdant);font:600 12px ui-monospace,Consolas,monospace}}.step-table .step-materials{{min-width:280px;color:#b9c9d9;font-size:12px}}
.source-link{{color:var(--arcane);font-weight:650;text-decoration:none;white-space:nowrap}}.source-link:hover,.source-link:focus-visible{{color:#fff;text-decoration:underline}}
.activity{{list-style:none;margin:0;padding:4px 0}}.event{{display:grid;grid-template-columns:72px 1fr;gap:13px;padding:13px 0;border-bottom:1px solid #2b3d52;transition:background .18s}}.event:hover{{background:#1a3045}}.event time{{font:600 10px ui-monospace;color:var(--arcane);padding-top:3px}}.event strong{{font-weight:650;font-size:13px;color:#e8edf5}}.event p{{margin:4px 0 0;color:var(--muted);font-size:12px;line-height:1.55}}footer{{margin-top:28px;padding:18px 0 24px;border-top:1px solid var(--line);color:var(--muted);font:11px Inter,ui-sans-serif,system-ui,sans-serif;display:flex;justify-content:space-between;letter-spacing:.02em}}
@media(max-width:850px){{.shell{{width:calc(100% - 40px)}}.topbar{{gap:22px}}.nav-links{{gap:16px}}.lower{{grid-template-columns:1fr}}.metrics{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:560px){{.shell{{width:calc(100% - 32px)}}.topbar{{height:62px;gap:12px;margin-inline:-16px;padding-inline:16px}}.brand{{font-size:12px;letter-spacing:0}}.nav-links{{gap:12px;overflow:auto}}.nav-item{{font-size:10px}}.nav-item:nth-child(n+3){{display:none}}.utility span{{display:none}}.avatar{{display:none}}.intro{{padding-top:28px}}.meta{{display:block;line-height:2}}.meta span+span:before{{margin-inline:7px}}.feature{{grid-template-columns:1fr;padding:17px}}.feature-side{{text-align:left}}.metrics{{grid-template-columns:repeat(2,minmax(0,1fr));gap:9px;margin:14px 0}}.metric{{padding:12px 13px;min-height:96px}}.metric:first-child{{padding-left:13px}}.metric strong{{font-size:24px}}.event{{grid-template-columns:58px 1fr}}.chart-panel{{padding:15px 11px}}.plot-row{{grid-template-columns:1fr;gap:8px;padding:11px 8px}}.plot-series{{grid-template-columns:minmax(66px,.42fr) minmax(50px,1fr) 32px;gap:8px}}.table-count{{width:100%;margin:0}}footer{{gap:14px;flex-direction:column}}}}
@media(prefers-reduced-motion:reduce){{*,*:before,*:after{{scroll-behavior:auto!important;transition:none!important}}}}
</style></head><body id="top"><div class="shell">{nav_html}
<main><header class="intro" id="overview"><div class="eyebrow">{e(h['eyebrow'])}</div><h1>{e(h['title'])}</h1><p class="subtitle">{e(h['subtitle'])}</p><div class="meta">{''.join(f'<span>{e(x)}</span>' for x in h.get('meta','').split(' · ') if x)}</div></header>
<section class="feature" id="summary" tabindex="0" title="{e(f.get('tooltip', f['text']))}"><div><div class="feature-label">{e(f['label'])}</div><h2>{e(f['title'])}</h2><p>{e(f['text'])}</p></div><div class="feature-side"><span class="dot"></span>{e(f.get('status','Current'))}</div></section>
{callout}<section class="metrics" aria-label="Report metrics">{metrics}</section>
{chart_html}
<div class="lower">{records_html}
<section id="activity"><div class="section-head"><h2>Recent activity</h2><span>CHRONOLOGY</span></div><ol class="activity">{events}</ol></section></div></main>
<footer id="notes"><span>{e(data['footer']['text'])}</span><span>GENERATED REPORT&nbsp; / &nbsp;RECURSION</span></footer></div>
<script>
(()=>{{
  const tabs=[...document.querySelectorAll('[data-profession-tab]')],panels=[...document.querySelectorAll('[data-profession-panel]')];
  function selectTab(slug){{tabs.forEach(tab=>{{const active=tab.dataset.professionTab===slug;tab.setAttribute('aria-selected',String(active));tab.tabIndex=active?0:-1}});panels.forEach(panel=>panel.hidden=panel.dataset.professionPanel!==slug)}}
  tabs.forEach((tab,index)=>{{tab.addEventListener('click',()=>selectTab(tab.dataset.professionTab));tab.addEventListener('keydown',event=>{{if(!['ArrowRight','ArrowLeft','Home','End'].includes(event.key))return;event.preventDefault();const next=event.key==='Home'?0:event.key==='End'?tabs.length-1:(index+(event.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;tabs[next].focus();selectTab(tabs[next].dataset.professionTab)}})}});
  const table=document.querySelector('[data-report-table]');if(!table)return;
  const body=table.tBodies[0],rows=[...body.rows],size=Number(table.dataset.pageSize)||8,filters=[...document.querySelectorAll('[data-report-filter]')],search=document.querySelector('[data-record-search]'),count=document.querySelector('[data-record-count]'),label=document.querySelector('[data-page-label]'),prev=document.querySelector('[data-page-prev]'),next=document.querySelector('[data-page-next]');
  const empty=document.createElement('tr');empty.className='empty-row';empty.hidden=true;empty.innerHTML='<td colspan="'+table.rows[0].cells.length+'">No records match these filters.</td>';body.append(empty);
  let page=1,sortColumn=-1,sortDirection=1;
  function render(){{
    let matched=rows.filter(row=>{{const end=row.cells.length-(table.dataset.hasDetails==='true'?1:0),text=[...row.cells].slice(0,end).map(cell=>cell.innerText).join(' ').toLocaleLowerCase();return(!search.value.trim()||text.includes(search.value.trim().toLocaleLowerCase()))&&filters.every(filter=>!filter.value||row.cells[Number(filter.dataset.filterColumn)].innerText.trim()===filter.value)}});
    if(sortColumn>=0)matched.sort((a,b)=>a.cells[sortColumn].innerText.trim().localeCompare(b.cells[sortColumn].innerText.trim(),undefined,{{numeric:true,sensitivity:'base'}})*sortDirection);
    const pages=Math.max(1,Math.ceil(matched.length/size));page=Math.min(page,pages);const start=(page-1)*size,visible=new Set(matched.slice(start,start+size));
    for(const row of rows){{row.hidden=!visible.has(row);body.append(row)}}empty.hidden=matched.length>0;
    count.textContent=matched.length+' matching record'+(matched.length===1?'':'s');label.textContent='Page '+page+' of '+pages+' · showing '+Math.min(size,Math.max(0,matched.length-start))+' of '+matched.length;
    prev.disabled=page<=1;next.disabled=page>=pages;
    for(const button of table.querySelectorAll('[data-sort]')){{const active=Number(button.dataset.sort)===sortColumn;button.closest('th').setAttribute('aria-sort',active?(sortDirection===1?'ascending':'descending'):'none');button.querySelector('span').textContent=active?(sortDirection===1?'↑':'↓'):'↕'}}
    document.querySelectorAll('[data-chart-filter]').forEach(point=>{{const active=filters.some(filter=>filter.dataset.filterName===point.dataset.chartColumn&&filter.value===point.dataset.chartFilter);point.setAttribute('aria-pressed',String(active));point.classList.toggle('active',active)}});
  }}
  search.addEventListener('input',()=>{{page=1;render()}});filters.forEach(filter=>filter.addEventListener('change',()=>{{page=1;render()}}));
  prev.addEventListener('click',()=>{{page--;render()}});next.addEventListener('click',()=>{{page++;render()}});
  table.querySelectorAll('[data-sort]').forEach(button=>button.addEventListener('click',()=>{{const column=Number(button.dataset.sort);sortDirection=column===sortColumn?-sortDirection:1;sortColumn=column;render()}}));render();
  document.querySelectorAll('[data-chart-filter]').forEach(point=>point.addEventListener('click',()=>{{const filter=filters.find(item=>item.dataset.filterName===point.dataset.chartColumn);if(!filter)return;filter.value=filter.value===point.dataset.chartFilter?'':point.dataset.chartFilter;page=1;render()}}));
}})();
</script></body></html>
'''


def main(args: list[str]) -> int:
    if len(args) not in {0, 2}:
        print("usage: compile_report.py [input.rec output.html]", file=sys.stderr)
        return 2
    source = Path(args[0]).resolve() if args else DEFAULT_INPUT
    target = Path(args[1]).resolve() if args else DEFAULT_OUTPUT
    try:
        output = render(parse(source))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(output, encoding="utf-8", newline="\n")
    except (OSError, UnicodeError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1
    print(f"Wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
