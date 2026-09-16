# frontend-lint-setup

프론트엔드(Next.js / React / Vite) 프로젝트에 **lint · formatter · 정적분석 도구**를
**검사 → 설치 → 적용**까지 해주는 Claude Code 실행형 스킬.

## 흐름

```
① 검사 리포트  →  ② "설치할까요?" 묻기  →  ③ 실제 설치·적용
                                          →  ④ "Stop 훅 넣을까요?" 묻기  →  ⑤ 적용
```

- 담기는 도구: Prettier(+Tailwind 정렬), ESLint(import 정렬·미사용 제거·`import type` 강제), (선택) Knip, Stop 훅
- 설명은 **항상 한국어 + 프론트엔드 초심자 친화**로 제공 (요청하지 않아도 기본)
- 되돌리기 어려운 행동(설치·대량 수정·삭제·커밋) 전엔 항상 확인

## 설치

Claude Code 개인 스킬 폴더에 두면 됩니다:

```bash
git clone <this-repo> ~/.claude/skills/frontend-lint-setup
```

이후 Claude Code에서 `/frontend-lint-setup` 또는 "프론트 린트 세팅해줘" 같은 요청으로 실행.

## 구성

```
SKILL.md                       # 워크플로 + 규칙 (핵심)
references/web-react.md         # React/Next/Vite 플러그인 표
references/cross-cutting.md     # 범용/모노레포 도구 (Knip·OXLint·Biome)
assets/frontend-lint-stop.sh    # Stop 훅 스크립트 (변경 파일 eslint 검사)
```

## 크레딧

Anthropic Claude Code의 `recommend-static-test-tools` 스킬(리포트 전용)을 기반으로,
**실제 설치·적용 + Stop 훅 단계 + 한국어 친절 설명**을 더해 개인용으로 재구성했습니다.
