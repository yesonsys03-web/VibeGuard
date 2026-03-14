# === ANCHOR: VIB_CHECKPOINT_CMD_START ===
from datetime import datetime
from pathlib import Path
from typing import Any

from vibelign.core.local_checkpoints import create_checkpoint
from vibelign.core.meta_paths import MetaPaths


def run_vib_checkpoint(args: Any) -> None:
    root = Path.cwd()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    if args.message:
        msg = f"vibelign: checkpoint - {' '.join(args.message)} ({timestamp})"
    else:
        msg = f"vibelign: checkpoint ({timestamp})"
    summary = create_checkpoint(root, msg)
    if summary is None:
        print("변경된 파일이 없습니다. 체크포인트를 건너뜁니다.")
        return
    meta = MetaPaths(root)
    print(f"✓ 로컬 체크포인트 저장 완료! [{summary.checkpoint_id[:8]}]")
    print(f"  메시지: {summary.message}")
    print(f"  파일 수: {summary.file_count}개")
    print(f"  위치: {meta.checkpoints_dir.relative_to(root) / summary.checkpoint_id}")
    if summary.pruned_count:
        freed_kb = max(1, round(summary.pruned_bytes / 1024))
        print(
            f"  오래된 체크포인트 {summary.pruned_count}개를 정리했고, 약 {freed_kb}KB를 비웠어요."
        )
    print("문제가 생기면 `vib undo`로 되돌릴 수 있습니다.")


# === ANCHOR: VIB_CHECKPOINT_CMD_END ===
