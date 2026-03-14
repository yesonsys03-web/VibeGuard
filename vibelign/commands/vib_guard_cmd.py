import json
from pathlib import Path
from typing import Any, Dict, List

from vibelign.core.change_explainer import explain_from_git, explain_from_mtime
from vibelign.core.doctor_v2 import analyze_project_v2
from vibelign.core.guard_report import combine_guard
from vibelign.core.meta_paths import MetaPaths
from vibelign.core.protected_files import get_protected, is_protected
from vibelign.core.risk_analyzer import analyze_project



from vibelign.terminal_render import cli_print
print = cli_print

def _guard_status(report) -> str:
    if report.blocked:
        return "fail"
    if report.overall_level == "WARNING":
        return "warn"
    return "pass"


def _rewrite_recommendations(recommendations: List[str]) -> List[str]:
    rewritten = []
    for item in recommendations:
        rewritten.append(
            item.replace("`vibelign anchor`", "`vib anchor --suggest`")
            .replace("vibelign undo", "vib undo")
            .replace("vibelign", "vib")
        )
    return rewritten


def _protected_violations(root: Path, explain_report) -> List[str]:
    protected = get_protected(root)
    if not protected:
        return []
    violations = []
    for item in explain_report.to_dict().get("files", []):
        path = item.get("path")
        if isinstance(path, str) and is_protected(path, protected):
            violations.append(path)
    return violations


def _build_guard_envelope(
    root: Path, strict: bool, since_minutes: int
) -> Dict[str, Any]:
    legacy_doctor = analyze_project(root, strict=strict)
    explain_report = explain_from_git(root) or explain_from_mtime(
        root, since_minutes=since_minutes
    )
    if explain_report is None:
        return {
            "ok": False,
            "error": {
                "code": "guard_explain_unavailable",
                "message": "guard용 변경 설명 데이터를 만들지 못했습니다.",
                "hint": "git 상태를 직접 확인한 뒤 다시 실행하세요.",
            },
            "data": {
                "status": "fail",
                "strict": strict,
                "blocked": True,
                "project_score": 0,
                "project_status": "High Risk",
                "change_risk_level": "HIGH",
                "summary": "guard 설명 데이터를 만들지 못해 안전하게 실패 처리했습니다.",
                "recommendations": ["git status 로 작업 상태를 직접 확인하세요."],
                "protected_violations": [],
                "doctor": {
                    "project_score": 0,
                    "status": "High Risk",
                    "issues": [],
                    "recommended_actions": [],
                },
                "explain": {
                    "source": "fallback",
                    "risk_level": "HIGH",
                    "files": [],
                    "summary": "설명 데이터를 만들지 못했습니다.",
                },
            },
        }
    legacy_guard = combine_guard(legacy_doctor, explain_report)
    doctor_v2 = analyze_project_v2(root, strict=strict)
    violations = _protected_violations(root, explain_report)
    status = _guard_status(legacy_guard)
    if strict and status == "warn":
        status = "fail"
    data = {
        "status": status,
        "strict": strict,
        "blocked": legacy_guard.blocked or (strict and status == "fail"),
        "project_score": doctor_v2.project_score,
        "project_status": doctor_v2.status,
        "change_risk_level": legacy_guard.change_risk_level,
        "summary": legacy_guard.summary,
        "recommendations": _rewrite_recommendations(legacy_guard.recommendations),
        "protected_violations": violations,
        "doctor": doctor_v2.to_dict(),
        "explain": {
            "source": explain_report.source,
            "risk_level": explain_report.risk_level,
            "files": explain_report.files,
            "summary": explain_report.summary,
        },
    }
    return {"ok": True, "error": None, "data": data}


def _render_markdown(data: Dict[str, Any]) -> str:
    lines = [
        "# VibeLign Guard Report",
        "",
        f"Status: {data['status']}",
        f"Strict: {'yes' if data['strict'] else 'no'}",
        f"Project score: {data['project_score']} / 100",
        f"Project status: {data['project_status']}",
        f"Change risk: {data['change_risk_level']}",
        "",
        "## Summary",
        str(data["summary"]),
        "",
    ]
    if data["protected_violations"]:
        lines.extend(["## Protected files changed"])
        lines.extend([f"- `{item}`" for item in data["protected_violations"]])
        lines.append("")
    lines.extend(["## Recommended next steps"])
    lines.extend([f"- {item}" for item in data["recommendations"]])
    lines.extend(["", "## Recent changed files"])
    files = data["explain"]["files"]
    if files:
        lines.extend(
            [f"- `{item['path']}` ({item['status']}, {item['kind']})" for item in files]
        )
    else:
        lines.append("- 최근 변경된 파일이 없습니다.")
    return "\n".join(lines) + "\n"


def _update_guard_state(root: Path, meta: MetaPaths) -> None:
    if not meta.state_path.exists():
        return
    state = json.loads(meta.state_path.read_text(encoding="utf-8"))
    state["last_guard_run_at"] = (
        __import__("datetime")
        .datetime.now(__import__("datetime").timezone.utc)
        .isoformat()
    )
    _ = meta.state_path.write_text(
        json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def run_vib_guard(args: Any) -> None:
    root = Path.cwd()
    meta = MetaPaths(root)
    envelope = _build_guard_envelope(
        root, strict=args.strict, since_minutes=args.since_minutes
    )
    _update_guard_state(root, meta)
    if args.json:
        text = json.dumps(envelope, indent=2, ensure_ascii=False)
        print(text)
        if args.write_report:
            meta.ensure_vibelign_dirs()
            _ = meta.report_path("guard", "json").write_text(
                text + "\n", encoding="utf-8"
            )
        if envelope["data"]["status"] == "fail":
            raise SystemExit(1)
        return
    markdown = _render_markdown(envelope["data"])
    print(markdown, end="")
    if args.write_report:
        meta.ensure_vibelign_dirs()
        _ = meta.report_path("guard", "md").write_text(markdown, encoding="utf-8")
    if envelope["data"]["status"] == "fail":
        raise SystemExit(1)
