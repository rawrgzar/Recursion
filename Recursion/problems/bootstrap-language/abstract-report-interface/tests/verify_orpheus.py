"""Deterministic content and generated-markup checks for Orpheus report."""

from __future__ import annotations

import importlib.util
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.dont_write_bytecode = True


HERE = Path(__file__).resolve().parents[1]
SOURCE = HERE / "source" / "orpheus-mission.rec"
OUTPUT = HERE / "output" / "orpheus-mission.html"
COMPILER = HERE.parent / "tools" / "compile_report.py"


class MarkupAudit(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.anchors: list[str] = []
        self.rows = 0
        self.warnings = 0
        self.details = 0
        self.errors: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if "id" in values:
            if values["id"] in self.ids:
                self.errors.append(f"duplicate id: {values['id']}")
            self.ids.add(values["id"] or "")
        if tag == "a" and (values.get("href") or "").startswith("#"):
            self.anchors.append(values["href"][1:])
        if tag == "tr":
            self.rows += 1
        if tag == "details":
            self.details += 1
        if tag == "span" and "review" in (values.get("class") or "").split():
            self.warnings += 1


def check(condition: bool, description: str) -> None:
    if not condition:
        raise AssertionError(description)
    print(f"PASS {description}")


def main() -> None:
    spec = importlib.util.spec_from_file_location("compile_report", COMPILER)
    check(spec is not None and spec.loader is not None, "compiler module is loadable")
    compiler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(compiler)
    data = compiler.parse(SOURCE)
    generated = compiler.render(data)
    saved = OUTPUT.read_text(encoding="utf-8")
    check(generated == saved, "checked-in HTML exactly matches a fresh compiler render")
    check(len(data["metrics"]) == 4, "four mission overview metrics are present")
    expected_rows = [
        ["Reactor output", "84.2 MW", "75–90 MW", "Nominal"],
        ["Hull pressure", "96.4 kPa", "94–101 kPa", "Nominal"],
        ["Core temperature", "418 K", "390–430 K", "Nominal"],
        ["Battery reserve", "31%", "35–100%", "⚠ Warning"],
        ["Comms signal", "−82 dBm", "−90 to −60 dBm", "Nominal"],
        ["Radiation exposure", "7.8 mSv/day", "0–6 mSv/day", "⚠ Warning"],
        ["Navigation drift", "0.014°", "0–0.020°", "Nominal"],
        ["Life support O₂", "21.1%", "20–22%", "Nominal"],
        ["Coolant flow", "18.6 L/s", "17–21 L/s", "Nominal"],
        ["Shield integrity", "99.2%", "98–100%", "Nominal"],
    ]
    check(data["rows"] == expected_rows, "all ten subsystem readings, ranges, units, and states match source data")
    check(sum("Warning" in row[3] for row in data["rows"]) == 2, "exactly two subsystem warnings are present")
    expected_events = [
        ["DAY 179", "Battery reserve below planning threshold", "Reserve fell below 35% after an extended communications window."],
        ["DAY 181", "Radiation exposure above planning limit", "Exposure exceeded the daily planning limit for six consecutive hours."],
        ["DAY 183", "Navigation correction completed", "Correction completed successfully; drift returned within tolerance."],
        ["DAY 184", "Autonomous diagnostic cycle completed", "Two alerts remain unresolved."],
    ]
    check([list(event) for event in data["activity"]] == expected_events, "all four mission events and details match source data in order")
    gates = data["feature"]["text"]
    check(all(value.casefold() in gates.casefold() for value in ["Day 190", "Day 197", "Day 205", "Battery reserve recovery", "Communications alignment", "Navigation validation"]), "all three milestones and dependencies are represented")
    check(data["metrics"][0][1] == "184 days" and data["metrics"][1][1] == "142.8 M km" and data["metrics"][2][1] == "8 / 10" and data["metrics"][3][1] == "2", "overview values match supplied dataset")
    check(all(row[3] == ("⚠ Warning" if row[0] in {"Battery reserve", "Radiation exposure"} else "Nominal") for row in data["rows"]), "subsystem state labels match the two supplied alert readings")

    audit = MarkupAudit()
    audit.feed(saved)
    audit.close()
    check(not audit.errors, "generated HTML has no duplicate element IDs")
    check(all(anchor in audit.ids for anchor in audit.anchors), "all in-page navigation targets exist")
    check(audit.rows == 11, "telemetry table renders ten data rows plus one empty-state row")
    check(audit.warnings == 0 and saved.count("⚠ Warning") >= 2, "both warnings have a distinct caution marker without recoloring nominal states")
    check(audit.details == 3, "expandable context is rendered for both warnings and navigation correction")
    check('type="search"' in saved and 'data-report-filter' in saved and 'data-sort=' in saved, "search, state filtering, and sortable table controls are rendered")
    check("data-page-next" in saved and "data-page-prev" in saved and "<details>" in saved, "pagination and expandable details are rendered")
    check("prefers-reduced-motion:reduce" in saved and "aria-labelledby" in saved and "scope=\"col\"" in saved, "reduced motion and semantic table/section labels are present")
    check("addEventListener('input'" in saved and "addEventListener('change'" in saved and "addEventListener('click'" in saved, "generated script wires search, filters, and sorting/pagination interactions")


if __name__ == "__main__":
    main()
