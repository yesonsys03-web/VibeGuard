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
from .commands.vib_undo_cmd import run_vib_undo


def build_parser():
    run_vib_guard = importlib.import_module(
        "vibeguard.commands.vib_guard_cmd"
    ).run_vib_guard
    parser = argparse.ArgumentParser(
        prog="vib",
        description="VibeLign CLI (VibeGuard와 호환되는 새 진입점)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help=".vibelign 메타데이터 초기화")
    p.set_defaults(func=run_vib_init)

    p = sub.add_parser("checkpoint", help="현재 상태를 체크포인트로 저장")
    p.add_argument("message", nargs="*", help="체크포인트 메시지")
    p.set_defaults(func=run_vib_checkpoint)

    p = sub.add_parser("undo", help="최근 체크포인트로 되돌리기")
    p.add_argument("--list", action="store_true", help="체크포인트 목록 보기")
    p.set_defaults(func=run_vib_undo)

    p = sub.add_parser("history", help="체크포인트 이력 보기")
    p.set_defaults(func=run_vib_history)

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

    return parser


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
# === ANCHOR: VIB_CLI_END ===
