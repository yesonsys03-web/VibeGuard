
# 12_VibeLign_Patch_System.md

Version: 1.0  
Status: Core Engine Spec

---

# 1. Overview

Patch System은 VibeLign의 핵심 엔진이다.

사용자의 자연어 요청을 기반으로
AI가 **안전하고 정확한 코드 수정 요청(Patch Prompt)** 을 생성하도록 돕는다.

Patch System은 다음 요소들과 함께 동작한다.

Project Understanding Engine  
CodeSpeak Grammar  
Anchor System  
Preview Engine  

작동 흐름:

User Intent
↓
CodeSpeak Translation
↓
Anchor Selection
↓
Patch Prompt Generation
↓
Preview Simulation
↓
AI Edit Execution

---

# 2. Problem Definition

기존 AI 코딩의 가장 큰 문제는 다음과 같다.

1. Whole-file rewrite  
AI가 파일 전체를 다시 작성한다.

2. Wrong location edit  
수정해야 할 위치가 아닌 곳을 수정한다.

3. Structural damage  
모듈 구조가 깨진다.

4. Context hallucination  
AI가 존재하지 않는 코드 구조를 가정한다.

Patch System은 이 문제를 해결하기 위해 만들어졌다.

It should also help users who describe requests roughly or emotionally rather than technically.

---

# 3. Patch Philosophy

Patch System의 철학은 다음과 같다.

1. Edit small  
가능한 작은 수정만 허용한다.

2. Anchor-based edit  
수정 위치는 반드시 Anchor 기반이어야 한다.

3. AI prompt safety  
AI가 수정할 때 반드시 제한 조건을 갖는다.

4. Predictable change  
AI 수정 결과는 예측 가능해야 한다.

---

# 4. Patch System Architecture

Patch Engine

- Intent Parser
- CodeSpeak Translator
- Anchor Selector
- Patch Builder
- Safety Guard

각 모듈 역할

Intent Parser  
사용자의 자연어 요청 분석

CodeSpeak Translator  
요청을 CodeSpeak 구조로 변환

Anchor Selector  
수정할 코드 영역 선택

Patch Builder  
AI 프롬프트 생성

Safety Guard  
수정 제한 조건 삽입

---

# 5. Patch Command

CLI 명령

vib patch <user request>

MVP preview exposure:

- canonical flow: `vib patch --preview`
- no separate `vib preview` command in MVP

예시

vib patch add progress bar

또는

vib patch make ui cleaner

또는

vib patch split left panel

---

# 6. Patch Generation Flow

1 User Intent  
2 Intent Parsing  
3 CodeSpeak Translation  
4 Anchor Discovery  
5 Target Selection  
6 Patch Prompt Creation

---

# 7. Intent Parsing

사용자 입력

add progress bar

Intent Parser 결과

Intent: UI modification  
Action: add component  
Component: progress bar

If confidence is low, Patch System should ask clarifying questions instead of generating a confident-looking patch target.

---

# 8. CodeSpeak Translation

사용자 자연어 → CodeSpeak

add progress bar

변환

ui.component.progress_bar.add

또는

ui.layout.sidebar.split

CodeSpeak must be visible to the user in beginner-facing patch flows.

---

# 9. Anchor Selection

Anchor System을 이용해 수정 위치를 찾는다.

예시

ui_pipeline_worker  
ui_layout_root  
ui_main_panel  

선택 기준

keyword match  
module similarity  
anchor priority  
file relevance  

---

# 10. Patch Target Selection

Patch System은 다음 정보를 출력한다.

Target File  
Target Anchor  
Confidence Score  
Reason  

예시

Target File:
src/ui/pipeline_panel.py

Target Anchor:
ui_pipeline_worker

Confidence:
0.73

---

# 11. Patch Prompt Builder

Patch Prompt 구조

Context  
Task  
Constraints  
Expected Result  

---

# 12. Patch Prompt Example

Follow AI_DEV_SYSTEM_SINGLE_FILE.md rules.

Task:
Add a progress bar to the pipeline worker UI.

Target File:
src/ui/pipeline_panel.py

Target Anchor:
ui_pipeline_worker

Constraints:

- patch only
- do not rewrite whole file
- keep structure
- avoid unrelated edits

Expected Result:

UI displays progress bar  
progress updates during pipeline execution  

---

# 13. Safety Guard

Patch System은 다음을 강제한다.

No whole file rewrite  
No unrelated file edits  
Anchor based modification only  
Minimal patch scope  

---

# 14. Patch Confidence System

Patch는 confidence score를 가진다.

범위

0.0 - 1.0

기준

keyword match  
anchor similarity  
module relevance  
file proximity  

예시

Confidence: 0.82

---

# 15. Patch Output Format

작업 내용:
add progress bar

제안 대상 파일:
src/ui/pipeline_panel.py

제안 대상 앵커:
ui_pipeline_worker

신뢰도:
0.82

이 대상을 선택한 이유:
- UI module detected
- anchor relevance high
- keyword match strong

제약 조건:
- patch only
- keep file structure
- no unrelated edits

목표:
Add progress bar UI

---

# 16. Patch Preview Integration

Patch 생성 후

vib patch --preview

Preview Engine은 다음을 보여준다.

Before UI  
After UI  
Change simulation  

Preview contract in MVP:

- input: patch request plus selected target file and target anchor
- output: human-readable preview plus optional JSON payload
- formats: ASCII only in MVP
- HTML preview is post-MVP

---

# 17. Patch Safety Modes

Safe Mode  
기본 모드, 작은 수정만 허용

Strict Mode  
Anchor 범위 내부만 수정

Experimental Mode  
AI 자유 수정 허용

---

# 18. Integration with Doctor

Doctor 결과는 Patch에 영향을 준다.

Large file warning  
Mixed UI logic  
Missing anchors  

Patch System은 이를 참고한다.

---

# 19. Integration with Guard

Guard 명령

doctor  
explain  
patch risk analysis  

Verification rules:

- patch target must resolve to a file and anchor before generation succeeds
- patch output must include constraints and target rationale
- whole-file rewrite is not allowed in MVP
- `vib guard` is the required post-edit verification command

Playground rule:

- safe experimentation is allowed only through preview-first, anchor-bound, minimal edits
- beginner-safe experimentation assumes checkpoint before edit, history for recovery visibility, and undo after failure when needed

---

# 20. MVP Scope

Intent parsing  
CodeSpeak translation  
Anchor selection  
Patch prompt generation  
Confidence score  
ASCII preview via `vib patch --preview`  

Not in MVP:

- standalone preview command
- HTML preview
- automatic multi-anchor patching
- automatic patch application

---

# 21. Future Expansion

Multi-anchor patch  
Refactor patches  
Automatic patch chains  
Patch learning system  

---

# 22. Summary

Patch System은 VibeLign의 핵심 엔진이다.

사용자 의도를 안전한 AI 코드 수정으로 변환한다.

핵심 원칙

Anchor based editing  
Minimal changes  
Predictable AI behavior
