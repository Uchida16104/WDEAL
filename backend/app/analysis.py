from __future__ import annotations

import csv
import io
import math
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import sqlite3
import pandas as pd


SQL_KEYWORDS = {
    "select", "from", "where", "group", "by", "having", "order", "limit",
    "with", "join", "left", "right", "inner", "outer", "full", "cross",
    "on", "as", "case", "when", "then", "else", "end", "union", "all",
    "distinct", "insert", "update", "delete", "create", "alter", "drop",
    "table", "view", "into", "values", "and", "or", "not", "null",
}

VBA_PROC_RE = re.compile(
    r"(?im)^\s*(?:Public\s+|Private\s+|Friend\s+)?(Sub|Function)\s+([A-Za-z_][A-Za-z0-9_]*)"
)
VBA_ATTR_RE = re.compile(r"(?im)^\s*Attribute\s+([A-Za-z0-9_\.]+)")
VBA_COMMENT_RE = re.compile(r"(?m)^\s*'")
VBA_ON_ERROR_RE = re.compile(r"(?im)\bOn\s+Error\b")


def _blank_frame() -> pd.DataFrame:
    return pd.DataFrame()


def parse_csv_text(csv_text: str) -> tuple[pd.DataFrame, str | None]:
    text = (csv_text or "").strip()
    if not text:
        return _blank_frame(), None

    try:
        # sniffer can fail on short or malformed text; fall back to comma
        sample = text[:4096]
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=[",", "\t", ";", "|"])
            sep = dialect.delimiter
        except Exception:
            sep = ","
        df = pd.read_csv(io.StringIO(text), sep=sep)
        return df, None
    except Exception as exc:
        return _blank_frame(), f"CSV parse error: {exc}"


def _register_input(con: sqlite3.Connection, df: pd.DataFrame) -> None:
    safe_df = df.copy() if df is not None else pd.DataFrame()
    if safe_df.empty and len(safe_df.columns) == 0:
        safe_df = pd.DataFrame([{}])  # ensure SELECT * FROM input_data is valid
    safe_df.to_sql("input_data", con, index=False, if_exists="replace")
    safe_df.to_sql("csv_data", con, index=False, if_exists="replace")


def run_sql(sql_text: str, df: pd.DataFrame) -> tuple[pd.DataFrame, str | None, dict[str, Any]]:
    sql = (sql_text or "").strip()
    meta = {
        "query_kind": "blank",
        "statement_count": 0,
        "keywords": [],
        "token_count": 0,
    }
    if not sql:
        return df.copy(), None, meta

    meta["query_kind"] = "sql"
    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|<=|>=|<>|!=|:=|\*|/|\+|-|=|\(|\)|,|\.|;", sql)
    meta["token_count"] = len(tokens)
    keywords = [tok.lower() for tok in tokens if tok.lower() in SQL_KEYWORDS]
    meta["keywords"] = sorted(set(keywords))
    meta["statement_count"] = sql.count(";") + 1

    con = sqlite3.connect(":memory:")
    try:
        _register_input(con, df if df is not None else pd.DataFrame())
        result = pd.read_sql_query(sql, con)
        return result, None, meta
    except Exception as exc:
        return (df.copy() if df is not None else pd.DataFrame()), f"SQL execution error: {exc}", meta
    finally:
        con.close()


def _detect_vba_language_features(vba_text: str) -> dict[str, Any]:
    text = vba_text or ""
    lines = text.splitlines()
    procs = VBA_PROC_RE.findall(text)
    proc_names = [name for _, name in procs]
    attrs = VBA_ATTR_RE.findall(text)
    comments = len(VBA_COMMENT_RE.findall(text))
    on_error = len(VBA_ON_ERROR_RE.findall(text))

    identifiers = re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", text)
    freq = Counter(i.lower() for i in identifiers)
    top_identifiers = [
        {"name": name, "count": count}
        for name, count in freq.most_common(12)
        if name not in {"sub", "function", "end", "if", "then", "else", "elseif", "for", "next", "do", "loop", "dim", "set", "let"}
    ]

    blank_lines = sum(1 for line in lines if not line.strip())
    indent_levels = [len(line) - len(line.lstrip(" ")) for line in lines if line.strip()]
    max_indent = max(indent_levels) if indent_levels else 0
    avg_indent = round(sum(indent_levels) / len(indent_levels), 2) if indent_levels else 0.0

    complexity_signals = {
        "loops": len(re.findall(r"(?im)\bFor\b|\bDo\b|\bWhile\b", text)),
        "conditionals": len(re.findall(r"(?im)\bIf\b|\bSelect\s+Case\b", text)),
        "procedures": len(proc_names),
        "error_handling": on_error,
        "comments": comments,
    }

    score = (
        complexity_signals["loops"] * 2
        + complexity_signals["conditionals"] * 2
        + complexity_signals["procedures"] * 3
        + complexity_signals["error_handling"] * 2
        + len(attrs)
    )

    return {
        "line_count": len(lines),
        "non_empty_lines": len([line for line in lines if line.strip()]),
        "blank_lines": blank_lines,
        "character_count": len(text),
        "procedure_count": len(proc_names),
        "procedure_names": proc_names,
        "attribute_count": len(attrs),
        "attributes": attrs,
        "comment_lines": comments,
        "on_error_count": on_error,
        "top_identifiers": top_identifiers,
        "indentation": {
            "max_indent": max_indent,
            "avg_indent": avg_indent,
        },
        "complexity_signals": complexity_signals,
        "complexity_score": score,
    }


def _column_profile(series: pd.Series) -> dict[str, Any]:
    non_null = int(series.notna().sum())
    missing = int(series.isna().sum())
    unique = int(series.nunique(dropna=True))
    sample_values = [None if pd.isna(v) else _scalar(v) for v in series.head(5).tolist()]

    return {
        "name": str(series.name),
        "dtype": str(series.dtype),
        "non_null": non_null,
        "missing": missing,
        "unique": unique,
        "sample": sample_values,
        "null_ratio": round((missing / len(series)), 4) if len(series) else 0.0,
    }


def _scalar(value: Any) -> Any:
    if pd.isna(value):
        return None
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    if hasattr(value, "item"):
        try:
            scalar = value.item()
            if isinstance(scalar, float) and math.isnan(scalar):
                return None
            return scalar
        except Exception:
            pass
    return value


def _dataframe_preview(df: pd.DataFrame, max_rows: int = 25) -> list[dict[str, Any]]:
    if df is None or df.empty:
        return []
    preview = df.head(max_rows).copy()
    preview = preview.where(pd.notna(preview), None)
    rows = []
    for _, row in preview.iterrows():
        rows.append({col: _scalar(val) for col, val in row.to_dict().items()})
    return rows


def _type_distribution(df: pd.DataFrame) -> dict[str, int]:
    buckets = {"numeric": 0, "text": 0, "datetime": 0, "boolean": 0, "other": 0}
    for dtype in df.dtypes:
        if pd.api.types.is_bool_dtype(dtype):
            buckets["boolean"] += 1
        elif pd.api.types.is_numeric_dtype(dtype):
            buckets["numeric"] += 1
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            buckets["datetime"] += 1
        elif pd.api.types.is_string_dtype(dtype) or dtype == "object":
            buckets["text"] += 1
        else:
            buckets["other"] += 1
    return buckets


def analyze_bundle(
    sql_text: str,
    csv_text: str,
    vba_text: str,
    chart_mode: str = "completeness",
    show_legend: bool = True,
    show_grid: bool = True,
    max_rows: int = 25,
) -> dict[str, Any]:
    raw_df, csv_error = parse_csv_text(csv_text)
    result_df, sql_error, sql_meta = run_sql(sql_text, raw_df)

    if result_df is None:
        result_df = pd.DataFrame()

    columns = [_column_profile(result_df[col]) for col in result_df.columns] if len(result_df.columns) else []

    numeric_cols = list(result_df.select_dtypes(include="number").columns)
    numeric_summary = {}
    if numeric_cols:
        desc = result_df[numeric_cols].describe(include="all").replace({pd.NA: None})
        numeric_summary = {
            index: {col: _scalar(desc.at[index, col]) for col in desc.columns}
            for index in desc.index
        }

    missing_by_column = [
        {"column": col["name"], "missing": col["missing"], "null_ratio": col["null_ratio"]}
        for col in columns
    ]
    missing_total = int(result_df.isna().sum().sum()) if len(result_df.columns) else 0
    rows_total = int(len(result_df))
    cols_total = int(len(result_df.columns))
    duplicate_rows = int(result_df.duplicated().sum()) if rows_total else 0
    memory_bytes = int(result_df.memory_usage(deep=True).sum()) if rows_total or cols_total else 0

    type_dist = _type_distribution(result_df)

    sql_tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|<=|>=|<>|!=|:=|\*|/|\+|-|=|\(|\)|,|\.|;", (sql_text or ""))
    sql_identifiers = [t.lower() for t in sql_tokens if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", t)]
    sql_keyword_hits = [tok for tok in sql_identifiers if tok in SQL_KEYWORDS]

    vba_analysis = _detect_vba_language_features(vba_text or "")

    error_messages = [msg for msg in [csv_error, sql_error] if msg]

    completeness_values = [
        round((1.0 - col["null_ratio"]) * 100, 2)
        for col in columns
    ]
    completeness_labels = [col["name"] for col in columns]

    if chart_mode == "missing":
        chart_type = "bar"
        chart_labels = [item["column"] for item in missing_by_column]
        chart_values = [item["missing"] for item in missing_by_column]
        dataset_label = "Missing cells"
    elif chart_mode == "types":
        chart_type = "doughnut"
        chart_labels = list(type_dist.keys())
        chart_values = list(type_dist.values())
        dataset_label = "Column types"
    else:
        chart_type = "bar"
        chart_labels = completeness_labels
        chart_values = completeness_values
        dataset_label = "Completeness %"

    chart = {
        "type": chart_type,
        "labels": chart_labels,
        "values": chart_values,
        "dataset_label": dataset_label,
        "show_legend": bool(show_legend),
        "show_grid": bool(show_grid),
        "show_nulls": chart_mode == "missing",
    }

    summary = {
        "rows": rows_total,
        "columns": cols_total,
        "missing_cells": missing_total,
        "duplicate_rows": duplicate_rows,
        "memory_bytes": memory_bytes,
        "dtype_distribution": type_dist,
    }

    return {
        "summary": summary,
        "columns": columns,
        "preview_rows": _dataframe_preview(result_df, max_rows=max_rows),
        "preview_columns": list(result_df.columns),
        "preview_shape": {"rows": rows_total, "columns": cols_total},
        "numeric_summary": numeric_summary,
        "missing_by_column": missing_by_column,
        "chart": chart,
        "chart_mode": chart_mode,
        "sql": {
            "query_kind": sql_meta["query_kind"],
            "statement_count": sql_meta["statement_count"],
            "token_count": sql_meta["token_count"],
            "keywords": sql_keyword_hits,
        },
        "vba": vba_analysis,
        "errors": error_messages,
        "result_csv": result_df.to_csv(index=False),
        "source_rows": int(len(raw_df)),
        "source_columns": int(len(raw_df.columns)),
    }


def analysis_to_dataframe(analysis: dict[str, Any]) -> pd.DataFrame:
    rows = analysis.get("preview_rows", [])
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)
