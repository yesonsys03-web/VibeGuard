# === ANCHOR: PATCH_SUGGESTER_START ===
from pathlib import Path
import re
import json
from dataclasses import dataclass, asdict
from vibeguard.core.meta_paths import MetaPaths
from vibeguard.core.project_scan import iter_source_files, relpath_str
from vibeguard.core.anchor_tools import extract_anchors

KEYWORD_HINTS = {
    "progress": [
        "progress",
        "worker",
        "backup",
        "copy",
        "ui",
        "status",
        "render",
        "widget",
        "panel",
        "terminal",
    ],
    "backup": ["backup", "worker", "copy", "hash", "verify"],
    "ui": ["ui", "window", "dialog", "widget", "layout", "button"],
    "button": ["button", "ui", "window", "dialog", "layout"],
    "log": ["log", "logger", "logging", "status"],
    "schedule": ["schedule", "scheduler", "cron", "timer"],
    "config": ["config", "settings", "json", "yaml", "toml"],
}

LOW_PRIORITY_NAMES = {"__init__.py", "__init__.js", "__init__.ts"}


@dataclass
class PatchSuggestion:
    request: str
    target_file: str
    target_anchor: str
    confidence: str
    rationale: list[str]

    def to_dict(self):
        return asdict(self)


def tokenize(text):
    return re.findall(r"[a-zA-Z_]+", text.lower())


def _score_anchor_names(anchor_names, request_tokens, label):
    score = 0
    rationale = []
    for anchor in anchor_names:
        al = anchor.lower()
        local_score = 0
        local_matches = []
        for token in request_tokens:
            if token in al:
                local_score += 3
                local_matches.append(token)
        if local_score > 0:
            score = max(score, local_score)
            joined = ", ".join(dict.fromkeys(local_matches))
            rationale = [f"{label} '{anchor}'에 키워드 {joined} 이(가) 포함됨"]
    return score, rationale


def score_path(path: Path, request_tokens, anchor_meta=None):
    score = 0
    rationale = []
    pt = str(path).lower()
    stem = path.stem.lower()

    if path.name in LOW_PRIORITY_NAMES:
        score -= 6
        rationale.append("init 스타일 파일이라 우선순위 낮음")
    if (
        "/tests/" in pt
        or pt.startswith("tests/")
        or "/docs/" in pt
        or pt.startswith("docs/")
    ):
        score -= 5
        rationale.append("docs/test 경로라 우선순위 낮음")

    for token in request_tokens:
        if token and token in pt:
            score += 3
            rationale.append(f"경로에 키워드 '{token}'이 포함됨")
    for key, hints in KEYWORD_HINTS.items():
        if key in request_tokens:
            for hint in hints:
                if hint in pt:
                    score += 2
                    rationale.append(f"'{key}' 키워드 계열인 '{hint}'와 경로가 일치")
    if stem in request_tokens:
        score += 4
        rationale.append(f"파일명 '{stem}'이 요청과 직접 일치")
    ui_request = any(
        tok in request_tokens
        for tok in [
            "progress",
            "ui",
            "button",
            "dialog",
            "window",
            "layout",
            "sidebar",
            "panel",
            "widget",
            "screen",
            "render",
        ]
    )
    if ui_request and any(
        tok in pt
        for tok in ["ui", "window", "dialog", "widget", "render", "terminal", "panel"]
    ):
        score += 3
        rationale.append("UI 성격 요청과 경로 특성이 잘 맞음")
    if any(
        tok in stem for tok in ["worker", "service", "window", "scheduler", "backup"]
    ):
        score += 1
    if isinstance(anchor_meta, dict):
        real_anchor_score, real_anchor_rationale = _score_anchor_names(
            anchor_meta.get("anchors", []), request_tokens, "실제 앵커"
        )
        suggested_score, suggested_rationale = _score_anchor_names(
            anchor_meta.get("suggested_anchors", []), request_tokens, "추천 앵커"
        )
        if real_anchor_score:
            score += real_anchor_score + 6
            rationale.extend(real_anchor_rationale)
        elif suggested_score:
            score += suggested_score + 2
            rationale.extend(suggested_rationale)
    return score, rationale


def choose_anchor(anchors, request_tokens):
    if not anchors:
        return "[먼저 앵커를 추가하세요]", ["이 파일에는 아직 앵커가 없습니다"]
    best_anchor = anchors[0]
    best_score = -1
    best_rationale = [f"첫 번째 앵커 '{best_anchor}'를 기본값으로 선택"]
    for anchor in anchors:
        score = 0
        rationale = []
        al = anchor.lower()
        for token in request_tokens:
            if token in al:
                score += 3
                rationale.append(f"앵커에 키워드 '{token}'이 포함됨")
        if "core" in al or "logic" in al or "worker" in al:
            score += 1
        if score > best_score:
            best_score = score
            best_anchor = anchor
            best_rationale = rationale or [
                f"사용 가능한 앵커 중 '{anchor}'를 최선으로 선택"
            ]
    return best_anchor, best_rationale


def choose_suggested_anchor(suggested_anchors, request_tokens):
    if not suggested_anchors:
        return None, []
    best_anchor = suggested_anchors[0]
    best_score = -1
    best_rationale = [f"추천 앵커 '{best_anchor}'를 기본값으로 선택"]
    for anchor in suggested_anchors:
        score = 0
        rationale = []
        al = anchor.lower()
        for token in request_tokens:
            if token in al:
                score += 3
                rationale.append(f"추천 앵커에 키워드 '{token}'이 포함됨")
        if score > best_score:
            best_score = score
            best_anchor = anchor
            best_rationale = rationale or [f"추천 앵커 중 '{anchor}'가 가장 적합함"]
    return best_anchor, best_rationale


def load_anchor_metadata(root: Path):
    meta = MetaPaths(root)
    if not meta.anchor_index_path.exists():
        return {}
    try:
        payload = json.loads(meta.anchor_index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    files = payload.get("files", {})
    return files if isinstance(files, dict) else {}


def suggest_patch(root: Path, request: str):
    request_tokens = tokenize(request)
    metadata = load_anchor_metadata(root)
    scored = []
    for path in iter_source_files(root):
        rel = relpath_str(root, path)
        score, rationale = score_path(path, request_tokens, metadata.get(rel, {}))
        scored.append((score, path, rationale))

    if not scored:
        return PatchSuggestion(
            request,
            "[소스 파일 없음]",
            "[없음]",
            "low",
            ["프로젝트에 아직 소스 파일이 없습니다"],
        )

    scored.sort(key=lambda x: (-x[0], str(x[1])))
    best_score, best_path, reasons = scored[0]
    anchors = extract_anchors(best_path)
    anchor, ar = choose_anchor(anchors, request_tokens)
    if anchor == "[먼저 앵커를 추가하세요]":
        file_meta = metadata.get(relpath_str(root, best_path), {}) if metadata else {}
        suggested = (
            file_meta.get("suggested_anchors", [])
            if isinstance(file_meta, dict)
            else []
        )
        suggested_anchor, suggested_rationale = choose_suggested_anchor(
            suggested, request_tokens
        )
        if suggested_anchor:
            anchor = f"[추천 앵커: {suggested_anchor}]"
            ar = suggested_rationale
    confidence = "high" if best_score >= 8 else "medium" if best_score >= 4 else "low"
    return PatchSuggestion(
        request, relpath_str(root, best_path), anchor, confidence, reasons[:5] + ar[:3]
    )


# === ANCHOR: PATCH_SUGGESTER_END ===
