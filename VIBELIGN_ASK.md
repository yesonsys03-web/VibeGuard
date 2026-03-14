다음 파일을 코딩을 전혀 모르는 사람도 이해할 수 있도록 한국어로 쉽게 설명해주세요.
전문 용어는 최대한 피하고, 비유나 예시를 들어 설명해주세요.
불필요한 인사말이나 서론 없이 바로 본문부터 시작하세요.
각 섹션 제목은 아래 형식을 정확히 유지하고, 섹션마다 1~3개의 짧은 문단 또는 bullet 목록만 사용하세요.
과한 마크다운 장식은 쓰지 말고, 코드/함수/파일명만 `backtick`으로 감싸세요.

파일명: vibelign/vib_cli.py
줄 수: 124줄
내용:
```py
# === ANCHOR: VIB_CLI_START ===
import argparse
import importlib

from .commands.vib_anchor_cmd import run_vib_anchor
from .commands.vib_checkpoint_cmd import run_vib_checkpoint
from .commands.vib_doctor_cmd import run_vib_doctor
from .commands.vib_explain_cmd import run_vib_explain
from .commands.vib_history_cmd import run_vib_history
from .commands.vib_init_cmd import run_vib_init
from .commands.vib_patch_cmd import run_vib_patch
from .commands.vib_start_cmd import run_vib_start
from .commands.vib_undo_cmd import run_vib_undo
from vibelign.commands.ask_cmd import run_ask
from vibelign.commands.config_cmd import run_config
from vibelign.commands.export_cmd import run_export
from vibelign.commands.protect_cmd import run_protect
from vibelign.commands.watch_cmd import run_watch_cmd


def build_parser():
    run_vib_guard = importlib.import_module(
        "vibelign.commands.vib_guard_cmd"
    ).run_vib_guard
    parser = argparse.ArgumentParser(
        prog="vib",
        description="VibeLign CLI (VibeLign와 호환되는 새 진입점)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help=".vibelign 메타데이터 초기화")
    p.set_defaults(func=run_vib_init)

    p = sub.add_parser("start", help="처음 쓰는 사람용 시작 명령")
    p.add_argument("message", nargs="*", help="원하면 바로 저장할 체크포인트 메시지")
    p.set_defaults(func=run_vib_start)

    p = sub.add_parser("checkpoint", help="현재 상태를 체크포인트로 저장")
    p.add_argument("message", nargs="*", help="체크포인트 메시지")
    p.set_defaults(func=run_vib_checkpoint)

    p = sub.add_parser("undo", help="최근 체크포인트로 되돌리기")
    p.add_argument("--list", action="store_true", help="체크포인트 목록 보기")
    p.set_defaults(func=run_vib_undo)

    p = sub.add_parser("history", help="체크포인트 이력 보기")
    p.set_defaults(func=run_vib_history)

    p = sub.add_parser("protect", help="중요 파일을 AI 수정으로부터 보호")
    p.add_argument("file", nargs="?", help="보호할 파일명")
    p.add_argument("--remove", action="store_true", help="보호 해제")
    p.add_argument("--list", action="store_true", help="보호 목록 보기")
    p.set_defaults(func=run_protect)

    p = sub.add_parser("ask", help="파일 내용을 쉬운 말로 설명")
    p.add_argument("file", help="설명이 필요한 파일명")
    p.add_argument("question", nargs="*", help="특정 질문")
    p.add_argument("--write", action="store_true", help="프롬프트를 파일로 저장")
    p.set_defaults(func=run_ask)

    p = sub.add_parser("config", help="API 키 설정")
    p.set_defaults(func=run_config)

    p = sub.add_parser("doctor", help="PRD 스타일의 VibeLign 프로젝트 진단")
    p.add_argument("--json", action="store_true")
    p.add_argument("--strict", action="store_true")
    p.add_argument("--detailed", action="store_true")
    p.add_argument("--fix-hints", action="store_true")
    p.add_argument("--write-report", action="store_true")
    p.set_defaults(func=run_vib_doctor)

    p = sub.add_parser("anchor", help="VibeLign 앵커 추천/삽입/검증")
    p.add_argument("--suggest", action="store_true")
    p.add_argument("--auto", action="store_true")
    p.add_argument("--validate", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--json", action="store_true")
    p.add_argument("--only-ext", default="")
    p.set_defaults(func=run_vib_anchor)

    p = sub.add_parser("patch", help="CodeSpeak-ready 패치 계획 생성")
    p.add_argument("request", nargs="+")
    p.add_argument("--ai", action="store_true")
    p.add_argument("--json", action="store_true")
    p.add_argument("--preview", action="store_true")
    p.add_argument("--write-report", action="store_true")
    p.set_defaults(func=run_vib_patch)

    p = sub.add_parser("explain", help="최근 변경을 쉬운 말로 설명")
    p.add_argument("--json", action="store_true")
    p.add_argument("--ai", action="store_true")
    p.add_argument("--since-minutes", type=int, default=120)
    p.add_argument("--write-report", action="store_true")
    p.set_defaults(func=run_vib_explain)

    p = sub.add_parser("guard", help="최근 변경과 구조 위험을 함께 검증")
    p.add_argument("--json", action="store_true")
    p.add_argument("--strict", action="store_true")
    p.add_argument("--since-minutes", type=int, default=120)
    p.add_argument("--write-report", action="store_true")
    p.set_defaults(func=run_vib_guard)

    p = sub.add_parser("export", help="도우미 템플릿 내보내기")
    p.add_argument("tool", choices=["claude", "opencode", "cursor", "antigravity"])
    p.set_defaults(func=run_export)

    p = sub.add_parser("watch", help="실시간 구조 모니터링")
    p.add_argument("--strict", action="store_true")
    p.add_argument("--write-log", action="store_true")
    p.add_argument("--json", action="store_true")
    p.add_argument("--debounce-ms", type=int, default=800)
    p.set_defaults(func=run_watch_cmd)

    return parser


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
# === ANCHOR: VIB_CLI_END ===
```

반드시 아래 형식으로 답해주세요:

## 1. 한 줄 요약
- 이 파일이 하는 일을 한두 문장으로만 요약해주세요.

## 2. 주요 기능을 쉬운 말로 설명
- 핵심 기능을 코드 비유나 쉬운 예시로 설명해주세요.

## 3. 다른 파일과 연결
- 이 파일이 어떤 파일/기능과 이어지는지 간단한 목록으로 설명해주세요.

## 4. 수정할 때 주의할 점
- AI나 사람이 수정할 때 조심해야 할 포인트를 짧은 목록으로 정리해주세요.
