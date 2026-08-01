from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates

from .analysis import analyze_bundle
from .export import analysis_to_csv_bytes, analysis_to_xlsx_bytes, analysis_to_xlsm_bytes

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="WDEAL API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULT_SQL = "SELECT * FROM input_data"
DEFAULT_CSV = """name,department,score,city
Aki,Sales,91,Tokyo
Mika,Engineering,88,Osaka
Jun,Marketing,95,Nagoya
"""
DEFAULT_VBA = """Option Explicit

Public Sub NormalizeValues()
    Dim i As Integer
    For i = 1 To 10
        If i Mod 2 = 0 Then
            Debug.Print i
        End If
    Next i
End Sub
"""


def _build_analysis(sql_text: str, csv_text: str, vba_text: str, chart_mode: str, show_legend: bool, show_grid: bool, max_rows: int) -> dict[str, Any]:
    return analyze_bundle(
        sql_text=sql_text,
        csv_text=csv_text,
        vba_text=vba_text,
        chart_mode=chart_mode,
        show_legend=show_legend,
        show_grid=show_grid,
        max_rows=max_rows,
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    analysis = _build_analysis(DEFAULT_SQL, DEFAULT_CSV, DEFAULT_VBA, "completeness", True, True, 25)
    return TEMPLATES.TemplateResponse(
        "standalone.html",
        {
            "request": request,
            "analysis": analysis,
            "analysis_json": json.dumps(analysis, ensure_ascii=False),
            "default_sql": DEFAULT_SQL,
            "default_csv": DEFAULT_CSV,
            "default_vba": DEFAULT_VBA,
        },
    )


@app.post("/api/analyze")
async def api_analyze(
    request: Request,
    sql_text: str = Form(DEFAULT_SQL),
    csv_text: str = Form(DEFAULT_CSV),
    vba_text: str = Form(DEFAULT_VBA),
    chart_mode: str = Form("completeness"),
    show_legend: bool = Form(True),
    show_grid: bool = Form(True),
    max_rows: int = Form(25),
) -> Response:
    analysis = _build_analysis(sql_text, csv_text, vba_text, chart_mode, show_legend, show_grid, max_rows)
    if request.headers.get("hx-request") == "true":
        return TEMPLATES.TemplateResponse(
            "partials/analysis_fragment.html",
            {
                "request": request,
                "analysis": analysis,
                "analysis_json": json.dumps(analysis, ensure_ascii=False),
            },
        )
    return JSONResponse(analysis)


@app.post("/api/export/{kind}")
async def api_export(
    kind: str,
    sql_text: str = Form(DEFAULT_SQL),
    csv_text: str = Form(DEFAULT_CSV),
    vba_text: str = Form(DEFAULT_VBA),
    chart_mode: str = Form("completeness"),
    show_legend: bool = Form(True),
    show_grid: bool = Form(True),
    max_rows: int = Form(25),
) -> Response:
    analysis = _build_analysis(sql_text, csv_text, vba_text, chart_mode, show_legend, show_grid, max_rows)

    if kind == "csv":
        body = analysis_to_csv_bytes(analysis)
        media_type = "text/csv; charset=utf-8"
        filename = "wdeal-export.csv"
    elif kind == "xlsx":
        body = analysis_to_xlsx_bytes(analysis)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = "wdeal-export.xlsx"
    elif kind == "xlsm":
        body = analysis_to_xlsm_bytes(analysis)
        media_type = "application/vnd.ms-excel.sheet.macroEnabled.12"
        filename = "wdeal-export.xlsm"
    else:
        return JSONResponse({"error": f"Unsupported export kind: {kind}"}, status_code=400)

    return Response(
        content=body,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
