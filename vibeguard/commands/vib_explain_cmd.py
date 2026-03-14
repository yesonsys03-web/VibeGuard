# === ANCHOR: VIB_EXPLAIN_CMD_START ===
import importlib
import json
from pathlib import Path
from typing import Any, Dict, List, cast

from vibeguard.core.change_explainer import explain_from_git, explain_from_mtime
from vibeguard.core.meta_paths import MetaPaths
from vibeguard.terminal_render import print_ai_response


def _fallback_explain_data() -> Dict[str, Any]:
    return {
        "source": "fallback",
        "risk_level": "LOW",
        "what_changed": ["변경 설명 데이터를 자동으로 만들지 못했습니다."],
        "why_it_matters": ["현재 작업 상태를 직접 확인하는 편이 안전합니다."],
        "what_to_do_next": "git status 나 최근 수정 파일을 직접 확인하세요.",
        "files": [],
        "summary": "자동 설명이 실패해 안전한 기본 안내를 보여줍니다.",
    }


def _build_explain_envelope(root: Path, since_minutes: int) -> Dict[str, Any]:
    report = explain_from_git(root) or explain_from_mtime(
        root, since_minutes=since_minutes
    )
    if report is None:
        return {
            "ok": False,
            "error": {
                "code": "explain_unavailable",
                "message": "변경 설명 데이터를 만들지 못했습니다.",
                "hint": "git 상태나 최근 수정 파일을 직접 확인하세요.",
            },
            "data": _fallback_explain_data(),
        }
    data = {
        "source": report.source,
        "risk_level": report.risk_level,
        "what_changed": report.what_changed,
        "why_it_matters": report.why_it_might_matter,
        "what_to_do_next": report.rollback_hint,
        "files": report.files,
        "summary": report.summary,
    }
    return {"ok": True, "error": None, "data": data}


def _render_markdown(data: Dict[str, Any]) -> str:
    files = cast(List[Dict[str, str]], data.get("files", []) or [])
    what_changed = cast(List[str], data.get("what_changed", []) or [])
    why_it_matters = cast(List[str], data.get("why_it_matters", []) or [])
    lines = [
        "# VibeLign Explain Report",
        "",
        f"Source: {data['source']}",
        f"Risk level: {data['risk_level']}",
        "",
        "## 1. 한 줄 요약",
        str(data["summary"]),
        "",
        "## 2. 변경된 내용",
    ]
    lines.extend(
        [f"- {item}" for item in what_changed] or ["- 눈에 띄는 변경이 없습니다."]
    )
    lines.extend(["", "## 3. 왜 중요한가"])
    lines.extend(
        [f"- {item}" for item in why_it_matters] or ["- 큰 영향은 없어 보입니다."]
    )
    lines.extend(
        ["", "## 4. 다음 할 일", str(data["what_to_do_next"]), "", "## 참고 파일"]
    )
    if files:
        lines.extend(
            [f"- `{item['path']}` ({item['status']}, {item['kind']})" for item in files]
        )
    else:
        lines.append("- 나열할 파일이 없습니다.")
    return "\n".join(lines) + "\n"


def run_vib_explain(args: Any) -> None:
    root = Path.cwd()
    envelope = _build_explain_envelope(root, since_minutes=args.since_minutes)
    meta = MetaPaths(root)
    if args.json:
        text = json.dumps(envelope, indent=2, ensure_ascii=False)
        print(text)
        if args.write_report:
            meta.ensure_vibelign_dirs()
            _ = meta.report_path("explain", "json").write_text(
                text + "\n", encoding="utf-8"
            )
        return
    if args.ai:
        ai_explain = importlib.import_module("vibeguard.core.ai_explain")
        if ai_explain.has_ai_provider():
            try:
                text, _attempted = ai_explain.explain_with_ai(envelope["data"])
            except Exception:
                text = None
        else:
            text = None
        if text:
            print_ai_response(text)
            if args.write_report:
                meta.ensure_vibelign_dirs()
                _ = meta.report_path("explain", "md").write_text(
                    text + "\n", encoding="utf-8"
                )
            return
    markdown = _render_markdown(envelope["data"])
    print(markdown, end="")
    if args.write_report:
        meta.ensure_vibelign_dirs()
        _ = meta.report_path("explain", "md").write_text(markdown, encoding="utf-8")


# === ANCHOR: VIB_EXPLAIN_CMD_END ===
