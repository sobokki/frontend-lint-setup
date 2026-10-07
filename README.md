# frontend-lint-setup

프론트엔드(Next.js / React / Vite) 프로젝트에 **lint · 포매터 · 정적분석 도구**를
**검사 → 설치 → 적용**까지 해주는 **Claude Code · Codex 공용 실행형 스킬**.

> 프론트엔드를 몰라도 괜찮아요. 이 스킬은 **항상 한국어로, 초심자도 이해하게 친절히** 설명합니다.

---

## 이 스킬이 해주는 것

한마디로 **"코드를 자동으로 깔끔하게 정리해주는 도구들을 대신 세팅"** 해줍니다.

| 도구 | 쉬운 설명 |
|---|---|
| **Prettier** | 자동 문서 정렬기 — 띄어쓰기·따옴표·줄바꿈을 한 스타일로 통일 |
| **ESLint (import 정렬 / 미사용 제거)** | "재료 목록" 자동 정리 + 안 쓰는 코드 자동 삭제 |
| **`import type` 강제** | 진짜 코드와 타입(설명서)을 구분해서 표시 |
| **Knip** (선택) | 안 쓰는 파일·의존성 찾아주는 창고 정리기 |
| **마무리 검사** (선택) | Claude Code·Codex의 Stop 훅 (환경별 등록·활성화) |

---

## 설치

### Codex

개인 스킬 폴더에 저장하면 여러 프로젝트에서 사용할 수 있습니다.

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/sobokki/frontend-lint-setup.git ~/.agents/skills/frontend-lint-setup
```

특정 프로젝트에서만 쓰려면 프로젝트 루트에서 다음 명령을 사용하세요. 개인 설치와 프로젝트 설치 중 하나를 선택하면 됩니다.

```bash
mkdir -p .agents/skills
git clone https://github.com/sobokki/frontend-lint-setup.git .agents/skills/frontend-lint-setup
```

프로젝트 내부에 clone한 폴더는 별도 Git 저장소입니다. 팀 저장소에 함께 배포하려면 일반 파일로 복사하거나 submodule을 명시적으로 사용하세요. 중첩 저장소를 그대로 `git add`하면 팀원이 파일을 받지 못할 수 있습니다.

설치 후 대상 프로젝트에서 새 Codex 세션을 열고 `$frontend-lint-setup`을 입력하세요. 인식되지 않으면 Codex를 재시작하세요.

### Claude Code

Claude Code의 개인 스킬 폴더에 넣으면 됩니다.

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/sobokki/frontend-lint-setup ~/.claude/skills/frontend-lint-setup
```

> 이미 설치했다면 다시 clone하지 말고 해당 설치 폴더에서 변경 사항을 확인한 뒤 `git pull --ff-only`로 업데이트하세요. Codex와 Claude Code에 각각 clone했다면 두 폴더를 각각 업데이트해야 합니다.

설치 후 Claude Code를 재시작하거나 새 세션을 열면 스킬이 인식됩니다.

---

## 사용법

### 1) 실행하기 — 아무거나 편한 방법으로

- **Codex:** 프롬프트에 `$frontend-lint-setup` 입력
- **Claude Code:** 프롬프트에 `/frontend-lint-setup` 입력
- **자연어로 부르기:** 아래처럼 말해도 자동 실행됩니다
  - "프론트 린트 세팅해줘"
  - "eslint 세팅해줘"
  - "포매터(prettier) 넣어줘"
  - "정적분석 도구 설치"

- **대상 폴더 지정(선택):** 모노레포면 폴더를 알려줄 수 있어요
  - Codex: `$frontend-lint-setup frontend 폴더에 적용해줘`
  - Codex: `$frontend-lint-setup apps/web 폴더를 점검해줘`
  - Claude Code: `/frontend-lint-setup frontend`
  - Claude Code: `/frontend-lint-setup apps/web`
  - (생략하면 자동으로 프론트엔드 폴더를 찾습니다)

### 2) 실행하면 이런 순서로 진행돼요

```
① 검사 리포트   프로젝트를 살펴보고 "뭐가 있고 뭐가 없는지" 표로 보여줌
      ↓
② 설치할까요?   "이 도구들 설치할까요?" 물어봄 (전체 / 일부 / 나중에)
      ↓  (설치해달라고 하면)
③ 실제 설치·적용  패키지 설치 + 설정 작성 + (확인 후) 전체 코드 정리 + 빌드 검증
      ↓
④ 마무리 검사 설정?  Claude Code / Codex: Stop 훅
      ↓  (넣어달라고 하면)
⑤ 적용         선택한 환경의 설정을 병합하고 검사 실행
```

**각 단계에서 당신이 결정해요.** 되돌리기 어려운 것(설치·대량 수정·파일 삭제·커밋) 전엔 **항상 먼저 물어봅니다.** 그냥 "①만 보고 싶어" 하면 리포트만 보고 멈출 수도 있어요.

### 3) 실제 대화 예시 (Claude Code)

```
당신:  프론트 린트 세팅해줘
스킬:  (프로젝트 감지) "Next.js 16 프론트엔드네요. 지금 Prettier가 없고..."
       → 검사 리포트 표 제시
스킬:  "이 도구들 설치할까요? (전체 / 일부 / 나중에)"
당신:  전체 설치해줘
스킬:  (설치) "설치 완료. 이제 전체 코드를 새 규칙에 맞게 정리할까요?
       357개 파일이 바뀝니다. import 정리도 포함돼 변경 내용과 테스트를 확인할게요."
당신:  응 정리해줘
스킬:  (정리 + pnpm build 검증) "완료! lint 0 에러, 빌드 성공."
스킬:  "작업 끝마다 자동 검사(Stop 훅)를 넣을까요?"
당신:  넣어줘
스킬:  (Stop 훅 설치·테스트) "완료. /hooks 한 번 열면 이번 세션부터,
       아니면 다음 세션부터 자동으로 작동해요."
```

---

## 알아두면 좋은 것

- **"자동 설치기"가 아니라 "작업 설명서"예요.** 스킬을 부르면 Claude Code 또는 Codex가 이 설명서를 따라 **확인받으며** 설치·적용해줍니다. 말없이 프로젝트를 뒤엎지 않아요.
- **패키지 매니저:** 예시는 `pnpm` 기준. npm/yarn이면 그에 맞게 설치합니다.
- **Tailwind v4 주의:** Prettier의 Tailwind 정렬은 `tailwindStylesheet`에 실제 CSS 진입점 경로를 넣어야 작동해요 (스킬이 자동으로 찾아 넣어줍니다).
- **Codex Stop 훅:** `.codex/hooks.json` 또는 기존 `config.toml`에 등록합니다. 설치 후 `/hooks`에서 사용자가 훅 내용을 검토하고 신뢰해야 실행됩니다. `AGENTS.md` 검사 지침은 보조 수단 또는 훅 미지원 환경의 대안입니다. [Codex 설치 절차](references/codex-stop-hooks.md)를 참고하세요.
- **검사 범위:** 기본 훅은 변경된 JS·TS 파일에 ESLint를 실행합니다. 프로젝트 전체 `tsc` 타입 검사는 별도입니다. 실패하면 추가 수정을 요청하지만, 재개된 턴은 무한 루프 방지를 위해 건너뜁니다. 수정 후 재검사와 CI는 계속 필요합니다.
- **Claude Code Stop 훅 활성화:** 세션 도중 넣으면 그 세션엔 안 뜹니다 → `/hooks`를 한 번 열거나 재시작. **다음 세션부터는 자동으로 작동**해요.
- **Stop 훅 vs git 커밋 훅:** Stop 훅은 "Claude가 응답 끝낼 때", 커밋 훅은 "당신이 커밋할 때" — 서로 다릅니다.

---

## 구성 파일

```
SKILL.md                       # 워크플로 + 규칙 (핵심 — 두 에이전트가 함께 읽는 설명서)
references/web-react.md         # React/Next/Vite 플러그인 추천 표
references/cross-cutting.md     # 범용/모노레포 도구 (Knip·OXLint·Biome)
agents/openai.yaml             # Codex 스킬 표시 이름·기본 프롬프트
assets/codex-lint-instructions.md # Codex AGENTS.md 병합용 템플릿
assets/frontend-lint-stop.sh    # 공통 Stop 훅 (Codex는 --codex로 실행)
references/codex-stop-hooks.md  # Codex 훅 등록·신뢰·검증 절차
evals/evals.json                # 공통·환경별 동작 평가 시나리오
```

### 스킬 테스트 (evals)

`evals/evals.json`은 공통 규칙과 Codex/Claude Code 분기 동작을 확인하는 시나리오 모음입니다. 자동 실행기는 포함하지 않습니다.
격리된 테스트 프로젝트에서 각 `prompt`를 실행하고 실제 동작을 `expected_output`과 비교하세요.

Codex에서는 대상 폴더 인식, Stop 훅 등록·신뢰, 실패 피드백·재검사, 기존 훅 보존·중복 방지를 확인합니다. 지침만 요청한 경우에는 기존 `AGENTS.md` 병합을 확인합니다.
Claude Code에서는 기존 Stop 훅 설치·루프 가드가 유지되는지 확인합니다.

테스트 실행에는 Python 3, Git, Bash, Node.js가 필요합니다. 훅의 파일 감지·종료 코드 회귀 테스트는 실제 Git 저장소와 ESLint 호출 대역을 사용합니다. 이 테스트만으로 ESLint 자체와 에이전트 대화 전체를 검증하지는 않습니다.

```bash
python3 -m unittest discover -s tests -v
```

실제 ESLint 통합 테스트는 별도 임시 프로젝트에 아래 패키지를 설치한 뒤 실행할 수 있습니다. 의존성을 지정하지 않으면 통합 테스트 5개는 skip됩니다.

```bash
# 별도 테스트 폴더에서 실행 (Node 22.13 이상인 22.x 또는 호환되는 LTS 권장)
npm install --ignore-scripts --no-audit --no-fund eslint@9 @eslint/js@9 \
  typescript@5 typescript-eslint@8 eslint-config-next@16 next@16 react@19 react-dom@19 \
  eslint-plugin-react eslint-plugin-react-hooks eslint-plugin-react-refresh \
  eslint-config-prettier eslint-plugin-simple-import-sort eslint-plugin-unused-imports globals

# 이 스킬 저장소에서 실행; 아래 경로를 실제 테스트 폴더로 변경
FRONTEND_LINT_NODE_MODULES=/absolute/path/to/test-project/node_modules \
  python3 -m unittest discover -s tests -v
```

검증 범위: ESLint 9.39.5 / eslint-config-next 16.4.0 / typescript-eslint 8.71.1에서 Next·Vite의 TS/JS 전용 설정 및 일반 React JS 설정에서 JSX·TSX·MTS·CTS·MJS·CJS 파일 검사, 실제 ESLint로 훅의 실패 차단·수정 후 통과. 다른 메이저 버전은 설치 시 호환성을 다시 확인해야 합니다. 에이전트 대화 전체와 앱 빌드·Tailwind 정렬까지 검증한 것은 아닙니다.

### Watch 실사용 검증 (2026-10-07)

`anti-monitor`의 `release/v1.6.0` (`5c62694d`)에서 만든 별도 작업 브랜치에서 Codex로 스킬 절차를 적용했습니다. ESLint 8.57.1의 `.eslintrc.cjs`, Tailwind 3.4.19의 커스텀 preset, pnpm 10.8.1을 유지했습니다.

- 별도 검증 설정·샘플에서 import 정렬·미사용 제거·type import·Tailwind 정렬 및 두 번째 실행 시 변경 없음을 확인했습니다.
- 기존 `--max-warnings 0` 검사와 충돌하지 않도록 새 규칙은 검증 설정에만 적용했습니다. 서비스 코드 전체 포맷·규칙 전환은 수행하지 않았습니다.
- Claude Stop 훅을 직접 실행해 정상 통과·오류 차단·재진입 방지를 확인했습니다. 이 과정에서 ESLint 8 legacy가 거부하는 `--no-warn-ignored` 옵션을 제거하고 legacy 회귀 테스트를 추가했습니다. Claude 앱에서 스킬 대화를 끝까지 실행한 검증은 아닙니다.
- 기존 마무리 검사 지침이 있어 AGENTS.md를 중복 수정하지 않았습니다.
- 변경 전후 정적 검사(tsc·기존 ESLint·ts-prune), 프론트 테스트 1,986개, 빌드를 통과했습니다. 빌드에는 chunk 크기 경고가 남습니다.

### Codex Stop 훅 실사용 검증 (2026-10-07)

- Codex CLI 0.160.1의 실제 Stop 이벤트에 공통 스크립트를 `--codex`로 연결했습니다. 격리된 임시 저장소에서 ESLint 오류 → exit 2 피드백 → Codex의 해당 파일 수정 → 명시적 ESLint 재검사 통과를 확인했습니다.
- 재개된 Stop 이벤트는 `stop_hook_active: true`로 들어왔고, 루프 가드가 `{}`와 exit 0을 반환했습니다. 검사 규칙과 훅은 수정되지 않았습니다.
- 사용자 설정과 분리된 임시 Codex 홈에서, 검토한 테스트 훅만 세션 설정으로 등록하고 `--dangerously-bypass-hook-trust`를 일회성 사용했습니다. 일반 설치의 `/hooks` 사용자 신뢰 절차를 자동화하거나 Watch의 훅을 활성화한 검증은 아닙니다.
- 회귀·통합 테스트 35개를 통과했고, 별도로 Watch에 설치된 ESLint 8.57.1에서도 Claude/Codex 모드의 실패·수정 후 통과를 확인했습니다. Codex 0.160.1 + ESLint 9.39.5에서 실제 lifecycle을 검증했으며 다른 버전·클라이언트는 별도 확인이 필요합니다.

### Codex 공식 문서

- [Stop 훅과 신뢰 설정](https://learn.chatgpt.com/docs/hooks)
- [스킬 설치 위치와 호출 방법](https://learn.chatgpt.com/docs/build-skills)
- [AGENTS.md 지침 적용 방식](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

---

## 크레딧 & 라이선스

Claude Code의 `recommend-static-test-tools` 스킬의 **"프레임워크 감지 → 도구 추천" 개념에서 영감**을 받아,
검사→설치→적용→Stop 훅→피드백 흐름과 한국어 초심자 친화 설명을 갖춘 개인용 스킬로 새로 작성했습니다.
레퍼런스 데이터·워크플로·스크립트는 모두 자체 리서치/작성 내용입니다.

라이선스: [MIT](./LICENSE)
