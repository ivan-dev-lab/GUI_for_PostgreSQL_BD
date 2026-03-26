from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from openpyxl import Workbook


def export_to_csv(file_path: str | Path, headers: list[str], rows: Iterable[Iterable[object]]) -> None:
    with open(file_path, "w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.writer(csv_file, delimiter=";")
        writer.writerow(headers)
        writer.writerows(rows)


def export_to_xlsx(file_path: str | Path, sheet_title: str, headers: list[str], rows: Iterable[Iterable[object]]) -> None:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = sheet_title[:31] or "Отчет"
    worksheet.append(headers)
    for row in rows:
        worksheet.append(list(row))
    workbook.save(file_path)
