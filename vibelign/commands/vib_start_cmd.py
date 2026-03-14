from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

from vibelign.commands.vib_doctor_cmd import build_doctor_envelope
from vibelign.commands.vib_init_cmd import run_vib_init
from vibelign.core.hook_setup import detect_tool, is_hook_set, setup_hook_if_needed
from vibelign.core.meta_paths import MetaPaths
from vibelign.terminal_render import print_ai_response, should_use_rich



from vibelign.terminal_render import cli_print
print = cli_print

def _status_line(status: str) -> str:
    if status in {"Safe", "Good"}:
        return "프로젝트 상태가 좋아요. 바로 AI 코딩을 시작해도 됩니다."
    if status == "Caution":
        return "큰 문제는 아니지만, 먼저 조금 정리하면 더 안전해요."
    return "지금은 바로 크게 수정하기보다, 먼저 문제를 확인하는 게 좋아요."


def _next_step(data: Dict[str, Any]) -> str:
    actions = data.get("recommended_actions") or []
    if actions:
        return str(actions[0])
    return "vib anchor --suggest"


def _has_git(root: Path) -> bool:
    return (root / ".git").is_dir()


def _ensure_rule_files(root: Path) -> Dict[str, List[str]]:
    """AI 룰 파일이 없으면 생성. 이미 있으면 건드리지 않음."""
    from vibelign.commands.export_cmd import AGENTS_MD_CONTENT
    from vibelign.core.ai_dev_system import AI_DEV_SYSTEM_CONTENT

    created: List[str] = []
    skipped: List[str] = []
    for fname, content in [
        ("AI_DEV_SYSTEM_SINGLE_FILE.md", AI_DEV_SYSTEM_CONTENT),
        ("AGENTS.md", AGENTS_MD_CONTENT),
    ]:
        path = root / fname
        if not path.exists():
            path.write_text(content, encoding="utf-8")
            created.append(fname)
        else:
            skipped.append(fname)
    return {"created": created, "skipped": skipped}


def _build_output(
    init_result: Optional[Dict[str, List[str]]],
    hook_label: Optional[str],
    hook_active: bool,
    git_active: bool,
    doctor_data: Dict[str, Any],
) -> str:
    sections: List[str] = []

    # 초기 설정 섹션 (첫 실행 때만)
    if init_result is not None:
        lines = ["## 초기 설정"]
        for f in init_result.get("created", []):
            lines.append(f"- {f}  ← 새로 생성됨")
        for f in init_result.get("skipped", []):
            lines.append(f"- {f}  ← 이미 있음, 유지")
        sections.append("\n".join(lines))

    # AI 도구 연동 섹션
    if hook_label and hook_active:
        lines = [
            "## AI 도구 연동",
            f"- {hook_label} 훅 활성화됨",
            "- AI가 파일을 수정하면 자동으로 checkpoint 가 저장돼요",
        ]
        sections.append("\n".join(lines))
    elif not hook_active and not git_active:
        lines = [
            "## 변경사항 추적 안내",
            "- AI 작업이 끝날 때마다 `vib checkpoint` 를 실행하면",
            "  `vib explain` 으로 무엇이 바뀌었는지 확인할 수 있어요",
            "- git 을 사용하면 별도 명령어 없이 자동 추적돼요",
        ]
        sections.append("\n".join(lines))

    # 프로젝트 상태 섹션
    score = doctor_data["project_score"]
    status = doctor_data["status"]
    next_step = _next_step(doctor_data)
    lines = [
        "## 프로젝트 상태",
        f"점수: {score} / 100",
        "",
        _status_line(status),
        "",
        f"다음 할 일: {next_step}",
    ]
    sections.append("\n".join(lines))

    return "\n\n".join(sections)


def run_vib_start(args: Any) -> None:
    root = Path.cwd()
    meta = MetaPaths(root)

    # [1] 첫 실행이면 전체 init, 기존 프로젝트면 룰 파일만 보장
    init_result: Optional[Dict[str, List[str]]] = None
    if not meta.state_path.exists():
        print("처음 사용하는 프로젝트예요. 기본 설정을 만들어드릴게요.")
        print()
        init_result = run_vib_init(SimpleNamespace())
    else:
        # 기존 프로젝트라도 AI 룰 파일이 없으면 자동 생성 (state.json 등은 건드리지 않음)
        rule_result = _ensure_rule_files(root)
        if rule_result["created"]:
            init_result = rule_result  # 새로 생성된 파일 있으면 출력에 표시

    # [2] AI 도구 훅 설정 제안 (interactive → 반드시 Rich 출력 전에)
    setup_hook_if_needed(root)

    # [3] 훅/git 상태 파악
    tool = detect_tool(root)
    hook_active = tool is not None and is_hook_set(root, tool)
    hook_label = {"claude": "Claude Code"}.get(tool, tool) if tool else None
    git_active = _has_git(root)

    # [4] Rich 패널 출력
    print()
    doctor_envelope = build_doctor_envelope(root, strict=False)
    doctor_data = doctor_envelope["data"]

    output_text = _build_output(
        init_result=init_result,
        hook_label=hook_label,
        hook_active=hook_active,
        git_active=git_active,
        doctor_data=doctor_data,
    )
    print_ai_response(output_text)
