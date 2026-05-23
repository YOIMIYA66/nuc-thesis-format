#!/usr/bin/env python3
"""Initial DOCX compliance checks for the NUC thesis format skill.

This script performs structural checks that can be verified from DOCX XML.
It is intentionally conservative: failing checks need attention, while warnings
mark items that usually require Word/WPS visual inspection.
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}

EXPECTED_MARGINS = {
    "top": 1701,     # 30 mm
    "bottom": 1417,  # 25 mm
    "left": 1701,    # 30 mm
    "right": 1134,   # 20 mm
    "header": 1417,  # 25 mm
    "footer": 1021,  # 18 mm
}


def q(name: str) -> str:
    return f"{{{NS['w']}}}{name}"


def read_xml(zf: zipfile.ZipFile, name: str) -> ET.Element | None:
    if name not in zf.namelist():
        return None
    return ET.fromstring(zf.read(name))


def paragraph_text(p: ET.Element) -> str:
    parts: list[str] = []
    for node in p.iter():
        if node.tag == q("t") and node.text:
            parts.append(node.text)
        elif node.tag == q("tab"):
            parts.append("\t")
        elif node.tag in {q("br"), q("cr")}:
            parts.append("\n")
    return "".join(parts).strip()


def extract_paragraphs(root: ET.Element | None) -> list[str]:
    if root is None:
        return []
    paras = []
    for p in root.findall(".//w:p", NS):
        text = paragraph_text(p)
        if text:
            paras.append(re.sub(r"\s+", " ", text).strip())
    return paras


def extract_text(root: ET.Element | None) -> str:
    return "\n".join(extract_paragraphs(root))


def chinese_char_count(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def compact(text: str) -> str:
    return re.sub(r"\s+", "", text)


class Report:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.warnings: list[str] = []
        self.passes: list[str] = []

    def pass_(self, message: str) -> None:
        self.passes.append(message)

    def fail(self, message: str) -> None:
        self.failures.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def emit(self) -> int:
        for message in self.passes:
            print(f"[PASS] {message}")
        for message in self.warnings:
            print(f"[WARN] {message}")
        for message in self.failures:
            print(f"[FAIL] {message}")
        print()
        print(
            f"Summary: {len(self.passes)} passed, "
            f"{len(self.warnings)} warnings, {len(self.failures)} failures"
        )
        return 1 if self.failures else 0


def check_margins(root: ET.Element, report: Report) -> None:
    sects = root.findall(".//w:sectPr", NS)
    if not sects:
        report.fail("No section properties found; cannot verify page margins.")
        return

    tolerance = 35
    for idx, sect in enumerate(sects, 1):
        pg_mar = sect.find("w:pgMar", NS)
        if pg_mar is None:
            report.fail(f"Section {idx} has no page margin settings.")
            continue
        for key, expected in EXPECTED_MARGINS.items():
            raw = pg_mar.get(q(key))
            if raw is None:
                report.fail(f"Section {idx} missing margin attribute {key}.")
                continue
            try:
                value = int(raw)
            except ValueError:
                report.fail(f"Section {idx} margin {key} is not numeric: {raw}")
                continue
            if abs(value - expected) > tolerance:
                report.fail(
                    f"Section {idx} margin {key} is {value} twips, expected about {expected}."
                )
    if not any("margin" in item for item in report.failures):
        report.pass_("Page margins match 30/25/30/20mm and header/footer offsets.")


def check_headers(zf: zipfile.ZipFile, report: Report, kind: str) -> None:
    header_text = "\n".join(
        extract_text(read_xml(zf, name))
        for name in zf.namelist()
        if name.startswith("word/header") and name.endswith(".xml")
    )
    expected = "英文文献及中文翻译" if kind == "translation" else "中北大学2026届毕业设计说明书"
    if expected in compact(header_text):
        report.pass_(f"Header contains {expected}.")
    else:
        report.fail(f"Header does not contain required text: {expected}.")


def find_pattern(paras: list[str], pattern: str) -> int | None:
    rx = re.compile(pattern, re.I)
    for idx, para in enumerate(paras):
        if rx.search(para):
            return idx
    return None


def section_slice(paras: list[str], start_pattern: str, end_pattern: str | None) -> list[str]:
    start = find_pattern(paras, start_pattern)
    if start is None:
        return []
    if end_pattern is None:
        return paras[start + 1 :]
    end = None
    rx = re.compile(end_pattern, re.I)
    for idx in range(start + 1, len(paras)):
        if rx.search(paras[idx]):
            end = idx
            break
    return paras[start + 1 : end]


def check_thesis_structure(paras: list[str], report: Report) -> None:
    checks = [
        ("Chinese abstract", r"摘\s*要"),
        ("English abstract", r"\babstract\b"),
        ("Table of contents", r"目\s*录"),
        ("Introduction chapter", r"^(1\s+)?(引言|绪论|前言)\b|^1\s+"),
        ("Conclusion", r"结\s*论"),
        ("References", r"参\s*考\s*文\s*献"),
        ("Acknowledgements", r"致\s*谢"),
    ]
    positions: dict[str, int] = {}
    for label, pattern in checks:
        pos = find_pattern(paras, pattern)
        if pos is None:
            report.fail(f"Missing required section: {label}.")
        else:
            positions[label] = pos

    ordered = [
        "Chinese abstract",
        "English abstract",
        "Table of contents",
        "Introduction chapter",
        "Conclusion",
        "References",
        "Acknowledgements",
    ]
    present = [positions[name] for name in ordered if name in positions]
    if present == sorted(present) and len(present) == len(positions):
        report.pass_("Required thesis sections appear in the expected order.")
    else:
        report.fail("Required thesis sections are out of order.")


def check_keywords(paras: list[str], report: Report) -> None:
    cn_lines = [p for p in paras if re.search(r"关\s*键\s*词", p)]
    if not cn_lines:
        report.fail("Chinese keywords line is missing.")
    else:
        line = cn_lines[0]
        payload = re.sub(r"^.*?关\s*键\s*词\s*[:：]?", "", line).strip()
        words = [w for w in re.split(r"[，,;；\s]+", payload) if w]
        if 3 <= len(words) <= 5:
            report.pass_("Chinese keywords count is 3 to 5.")
        else:
            report.fail(f"Chinese keywords count is {len(words)}, expected 3 to 5.")
        if payload.endswith(("。", ".", "；", ";", "，", ",")):
            report.fail("Chinese keywords line ends with punctuation.")

    en_lines = [p for p in paras if re.search(r"\bkey\s*words?\b|\bkeyword\b", p, re.I)]
    if not en_lines:
        report.warn("English Keyword line was not found by heuristic search.")
    else:
        line = en_lines[-1]
        payload = re.sub(r"^.*?\bkey\s*words?\b\s*[:：]?", "", line, flags=re.I).strip()
        if ";" in payload or "；" in payload:
            report.fail("English Keyword line should use English commas, not semicolons.")
        if "，" in payload:
            report.fail("English Keyword line should use English commas, not Chinese commas.")
        words = [w for w in re.split(r"[,]+", payload) if w.strip()]
        if 3 <= len(words) <= 5:
            report.pass_("English keywords count is 3 to 5.")
        else:
            report.warn(f"English keywords count appears to be {len(words)}, expected 3 to 5.")
        if payload.endswith((".", ";", "；", ",", "，")):
            report.fail("English Keyword line ends with punctuation.")


def check_references(paras: list[str], report: Report) -> None:
    ref_paras = section_slice(paras, r"参\s*考\s*文\s*献", r"致\s*谢")
    if not ref_paras:
        report.fail("References section content was not found.")
        return

    refs = [p for p in ref_paras if re.match(r"^\[\d+\]", p)]
    english_refs = [p for p in refs if re.search(r"[A-Za-z]{5,}", p)]
    if len(refs) >= 20:
        report.pass_("Reference count is at least 20.")
    else:
        report.fail(f"Reference count is {len(refs)}, expected at least 20.")
    if len(english_refs) >= 5:
        report.pass_("English reference count is at least 5.")
    else:
        report.fail(f"English reference count is {len(english_refs)}, expected at least 5.")

    expected_numbers = list(range(1, len(refs) + 1))
    actual_numbers = []
    for ref in refs:
        m = re.match(r"^\[(\d+)\]", ref)
        if m:
            actual_numbers.append(int(m.group(1)))
    if actual_numbers == expected_numbers:
        report.pass_("Reference numbers are continuous from [1].")
    else:
        report.fail("Reference numbers are not continuous from [1].")


def check_numbering(text: str, report: Report) -> None:
    bad_half_paren = re.findall(r"(?m)^\s*\d+\)", text)
    bad_chinese_nums = re.findall(r"(?m)^\s*[一二三四五六七八九十]+[、.．]", text)
    if bad_half_paren:
        report.fail("Found half-parenthesis numbering such as 1), which is forbidden.")
    if bad_chinese_nums:
        report.fail("Found Chinese numeral list numbering such as 一、, which is forbidden.")
    if not bad_half_paren and not bad_chinese_nums:
        report.pass_("No forbidden half-parenthesis or Chinese-numeral numbering found.")

    malformed_figures = re.findall(r"图\s*\d+(?!\.)", text)
    malformed_tables = re.findall(r"表\s*\d+(?!\.)", text)
    if malformed_figures:
        report.warn("Some figure captions may not use chapter numbering like 图1.1.")
    if malformed_tables:
        report.warn("Some table captions may not use chapter numbering like 表1.1.")


def check_translation(paras: list[str], report: Report) -> None:
    text = "\n".join(paras)
    count = chinese_char_count(text)
    if count >= 3000:
        report.pass_("Chinese translation contains at least 3000 Chinese characters.")
    else:
        report.fail(f"Chinese character count is {count}, expected at least 3000 for translation.")
    if re.search(r"英文原文|原文", text):
        report.pass_("Translation package appears to include an original-text section.")
    else:
        report.warn("Original-text section heading was not found; verify English original is included.")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    parser.add_argument("--kind", choices=["thesis", "translation"], default="thesis")
    args = parser.parse_args(argv)

    if args.docx.suffix.lower() != ".docx":
        print("[FAIL] This checker only supports .docx. Convert .doc to .docx first.", file=sys.stderr)
        return 1
    if not args.docx.exists():
        print(f"[FAIL] File not found: {args.docx}", file=sys.stderr)
        return 1

    report = Report()
    with zipfile.ZipFile(args.docx) as zf:
        root = read_xml(zf, "word/document.xml")
        if root is None:
            print("[FAIL] word/document.xml not found; invalid DOCX.", file=sys.stderr)
            return 1
        paras = extract_paragraphs(root)
        text = "\n".join(paras)

        check_margins(root, report)
        check_headers(zf, report, args.kind)
        check_numbering(text, report)
        if args.kind == "thesis":
            check_thesis_structure(paras, report)
            check_keywords(paras, report)
            check_references(paras, report)
            report.warn("Verify page count, Roman/Arabic page-number sections, fonts, bolding, and automatic TOC visually in Word/WPS.")
        else:
            check_translation(paras, report)
            report.warn("Verify translated pages, inserted screenshots/original PDF clarity, and page numbering visually in Word/WPS.")

    return report.emit()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
