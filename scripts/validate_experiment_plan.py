#!/usr/bin/env python3
"""Validate required fields in a growth experiment plan CSV."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


REQUIRED_FIELDS = [
    "实验编号",
    "业务阶段",
    "业务问题",
    "目标用户",
    "核心痛点",
    "触发场景",
    "增长假设",
    "测试动作",
    "渠道",
    "核心指标",
    "成功标准",
    "下一步动作",
]


def is_blank(value: str | None) -> bool:
    return value is None or value.strip() == ""


def validate_file(input_path: Path, invalid_rows_path: Path) -> int:
    invalid_rows: list[dict[str, str]] = []

    with input_path.open("r", newline="", encoding="utf-8-sig") as input_file:
        reader = csv.DictReader(input_file)
        if reader.fieldnames is None:
            raise ValueError("输入 CSV 缺少表头")

        missing_columns = [field for field in REQUIRED_FIELDS if field not in reader.fieldnames]
        if missing_columns:
            raise ValueError("缺少必要列：" + "，".join(missing_columns))

        output_fields = list(reader.fieldnames)
        if "错误信息" not in output_fields:
            output_fields.append("错误信息")

        for row_number, row in enumerate(reader, start=2):
            missing_fields = [field for field in REQUIRED_FIELDS if is_blank(row.get(field))]
            if missing_fields:
                output_row = dict(row)
                output_row["错误信息"] = f"第 {row_number} 行缺少字段：" + "，".join(missing_fields)
                invalid_rows.append(output_row)

    invalid_rows_path.parent.mkdir(parents=True, exist_ok=True)
    with invalid_rows_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=output_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(invalid_rows)

    return len(invalid_rows)


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python3 scripts/validate_experiment_plan.py input.csv output/invalid_rows.csv", file=sys.stderr)
        return 2

    input_path = Path(sys.argv[1])
    invalid_rows_path = Path(sys.argv[2])

    if not input_path.exists():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        invalid_count = validate_file(input_path, invalid_rows_path)
    except Exception as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1

    if invalid_count:
        print(f"Found {invalid_count} invalid rows. Details written to {invalid_rows_path}")
        return 1

    print(f"Validation passed. Empty invalid rows file written to {invalid_rows_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
