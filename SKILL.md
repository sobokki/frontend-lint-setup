---
name: frontend-lint-setup
description: |
  프론트엔드(Next.js / React / Vite) 프로젝트에 lint·formatter·정적분석 도구를 검사→설치→적용까지 해주는 실행형 스킬.
  Triggers on: "프론트 린트 세팅", "eslint 세팅해줘", "포매터 넣어줘", "prettier 설정",
  "frontend lint setup", "정적분석 도구 설치", "lint 도구 세팅".
  흐름: 검사 리포트 → 설치 여부 묻기 → 실제 설치·적용 → Stop 훅 여부 묻기 → 적용.
argument-hint: "[대상 폴더: 예) frontend, apps/web (생략 시 자동 감지)]"
---

# 프론트엔드 Lint/Format 세팅 (실행형)

프론트엔드 프로젝트를 검사해서 필요한 lint·formatter·정적분석 도구를 **추천하고, 확인받아 실제로 설치·적용**까지 해준다.
`recommend-static-test-tools` 스킬(리포트 전용)을 기반으로, 실제 설치·적용 + Stop 훅 단계를 더한 개인용 버전.

---

## 🟢 절대 규칙 (모든 응답에 항상 적용 — 사용자가 요구하지 않아도)

1. **항상 한국어로 설명한다.** 레퍼런스 자료가 영어여도, 사용자에게 보이는 설명은 한국어.
2. **프론트엔드를 모르는 사람도 이해하게 친절히 설명한다.** 전문용어를 쓰면 반드시 쉬운 비유를 곁들인다.
   - 예: 린터=코드 감시원/맞춤법 검사기, 포매터=자동 문서 정렬기, import 정렬=재료 목록 자동 정리, 미사용 제거=안 쓰는 짐 버리기, Stop 훅=작업 마무리 자동 검사대.
   - "이게 왜 필요한지"를 before/after 예시로 보여준다.
3. **표·체크리스트·번호목록**으로 구조화해서 한눈에 보이게 한다.
4. **되돌리기 어려운 행동(설치·대량 수정·파일 삭제·커밋·push) 전에는 반드시 확인**받는다. 승인 없이 진행하지 않는다.
5. **기획/사양을 임의로 바꾸지 않는다.** 제약이 있으면 선택지를 제시하고 사용자가 결정.
6. **재실행 안전(중복 방지·병합).** 이미 설치·설정된 도구는 **덮어쓰지 않고 건드리지 않는다.** 1-2 진단에서 이미 있는 걸 파악해, 없는 것만 추가하고, 설정 파일은 통째로 갈아엎지 말고 **기존 내용에 병합**한다. (예: `eslint.config`에 규칙이 이미 있으면 새로 덮지 말고 빠진 것만 추가. 이미 Prettier가 있으면 재설치하지 않고 설정 충돌만 점검.) 재실행해도 안전해야 한다.

---

## 흐름 요약

```
0️⃣ 시작 전 안전 확인  →  ① 검사 리포트  →  ② "설치할까요?" 묻기  →  ③ (승인 시) 실제 설치·적용
                                              →  ④ "Stop 훅 넣을까요?" 묻기  →  ⑤ (승인 시) 적용
                                              →  ⑥ 피드백 & 자기개선 (references 업데이트)
```

---

## 0️⃣ 시작 전 안전 확인 (항상 먼저)

이 스킬은 나중에 **파일을 대량으로 바꾸고 설치도** 하므로, 언제든 되돌릴 수 있게 먼저 git 상태를 확인한다.

```bash
git status --short
```
- **깨끗함(변경 없음):** 그대로 진행. (나중에 문제 생기면 `git restore`로 전부 원복 가능하다고 안내.)
- **커밋 안 된 변경이 있음:** 사용자에게 알리고 **선택지 제시** — 진행 전에 커밋할지 / `git stash`로 잠깐 치울지 / 그냥 진행할지. 승인 없이 진행하지 않는다.
- **git 저장소가 아님:** "되돌리기가 어려우니 git 초기화를 권합니다"라고 안내하고 진행 여부를 물어본다.

> 왜: 대량 포맷·삭제 후 "되돌리고 싶다"가 되면, 시작 시점이 커밋돼 있어야 안전하게 원복된다.

---

## ① 검사 리포트

### 1-1. 대상 감지
- `$ARGUMENTS`로 폴더가 주어지면 그 폴더. 없으면 `package.json`을 찾아 프론트엔드 워크스페이스 자동 감지.
- 모노레포면 프론트엔드 패키지를 고른다 (`next`, `react`, `vite` 의존성 기준).
- 감지 결과를 사용자에게 **먼저 한국어로 요약**하고 확인받는다.

### 1-2. 현재 상태 진단
`package.json` + 설정 파일 + lockfile을 읽어 아래를 파악:
1. ESLint 설정 (`eslint.config.*` / `.eslintrc.*`) — 이미 있는 플러그인
2. 포매터 (prettier / biome / 없음)
3. 테스트 러너 (vitest / jest / playwright / 없음)
4. 커밋 훅 (husky / lint-staged / pre-commit / 없음)
5. 정적분석 (knip 등)
6. **패키지 매니저** — lockfile로 감지: `pnpm-lock.yaml`→pnpm, `package-lock.json`→npm, `yarn.lock`→yarn, `bun.lockb`→bun. **이후 모든 설치 명령을 이 매니저에 맞춘다.**
7. **Tailwind 사용 여부** — `package.json`에 `tailwindcss` 있는지 + CSS 진입점(`globals.css` 등) 위치. **없으면 Tailwind 관련 플러그인/설정은 전부 건너뛴다.**
8. **CI가 lint/build를 돌리는지** — `.github/workflows/*.yml` 등에서 `lint`·`build` 실행 여부 확인. 돌린다면 3단계에서 규칙을 `warn`으로 시작해 CI가 갑자기 막히는 사고를 예방.

### 1-3. 리서치 (병렬 에이전트 3개)
`references/web-react.md`, `references/cross-cutting.md`를 기반으로, **최신 버전·호환성·실제 채택률**을 웹 검색으로 검증:
- **Agent 1 (프레임워크 전문):** `web-react.md` 로드 + 최신 버전/ESLint 9 flat config 호환/React·Next 버전 호환 확인
- **Agent 2 (채택률 검증):** 유명 OSS 5곳 이상의 실제 eslint 설정 확인 → 채택 빈도표
- **Agent 3 (범용 도구):** `cross-cutting.md` 로드 + Knip/OXLint/Biome 등 비-ESLint 도구 검토

### 1-4. 리포트 제시 (한국어·친절)
각 도구를 **MUST-HAVE / NICE-TO-HAVE / SKIP**으로 분류하고, **각각이 뭘 하는지 쉬운 비유로 설명**한다. 표에 주간 다운로드·실제 채택 근거를 함께 표기.

> 📌 이 단계까지는 **아무것도 설치/수정하지 않는다.** 순수 리포트.

---

## ② "설치할까요?" 묻기

리포트를 보여준 뒤, `AskUserQuestion`으로 물어본다:
- **전체 설치** / **일부만 선택** / **아직 안 함**
- 전체 코드 일괄 정리(포맷)는 파일이 대량으로 바뀌므로 **별도로 한 번 더 확인**한다.

---

## ③ 실제 설치·적용 (승인 시에만)

아래는 이번에 검증된 표준 세팅. 프로젝트에 맞게 조정하되 기본값으로 사용.

### 3-1. 패키지 설치
1-2에서 감지한 **매니저**로 설치 (아래는 pnpm 예시):
```bash
pnpm add -D prettier eslint-config-prettier \
  eslint-plugin-simple-import-sort eslint-plugin-unused-imports
# Tailwind 를 쓰는 경우에만 추가:
pnpm add -D prettier-plugin-tailwindcss
```
- 매니저별 설치 명령: pnpm→`pnpm add -D`, npm→`npm i -D`, yarn→`yarn add -D`, bun→`bun add -d`.
- **Tailwind 없으면** `prettier-plugin-tailwindcss`를 설치하지 않고, 아래 Prettier 설정에서도 tailwind 관련 항목을 뺀다.

### 3-2. Prettier 설정 (`.prettierrc.json`)
```json
{
  "plugins": ["prettier-plugin-tailwindcss"],
  "tailwindStylesheet": "./src/app/globals.css",
  "tailwindFunctions": ["cn", "clsx", "cva"]
}
```
> ⚠️ Tailwind v4는 `tailwindStylesheet`에 **실제 CSS 진입점 경로**를 넣어야 클래스 정렬이 작동한다. 프로젝트에서 globals.css 위치를 찾아 넣을 것.

### 3-3. `.prettierignore` — 빌드/생성물 제외
`.next/`, `out/`, `build/`, `node_modules/`, `pnpm-lock.yaml`, `next-env.d.ts`, 생성된 docs/번들 등 앱 코드가 아닌 것들.

### 3-4. ESLint 설정 (flat config에 추가)
- 플러그인: `simple-import-sort`(import 정렬), `unused-imports`(미사용 제거), `@typescript-eslint/consistent-type-imports`(`import type` 강제)
- `eslint-config-prettier`는 **맨 마지막에 spread** (포맷 규칙 충돌 방지)
- import 그룹 예시: `[["^react","^next","^@?\\w"], ["^@(/|src|app|features|common)(/|$)"], ["^\\."], ["^.+\\.s?css$"]]`
- 생성/벤더 JS(빌드 산출물)는 `globalIgnores`에 추가해 lint 소음 제거

**복사-붙여넣기용 완성 예시 (Next.js + ESLint 9 flat config):**
```js
import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";
import prettier from "eslint-config-prettier/flat";
import simpleImportSort from "eslint-plugin-simple-import-sort";
import unusedImports from "eslint-plugin-unused-imports";

export default defineConfig([
  ...nextVitals,
  ...nextTs,
  {
    plugins: {
      "simple-import-sort": simpleImportSort,
      "unused-imports": unusedImports,
    },
    rules: {
      // 도입 단계엔 "warn", 전체 정리(3-6) 후 "error"로 승격.
      "simple-import-sort/imports": [
        "error",
        {
          groups: [
            ["^react", "^next", "^@?\\w"],
            ["^@(/|src|app|features|common)(/|$)"],
            ["^\\."],
            ["^.+\\.s?css$"],
          ],
        },
      ],
      "simple-import-sort/exports": "error",
      "@typescript-eslint/consistent-type-imports": [
        "error",
        { prefer: "type-imports", fixStyle: "separate-type-imports" },
      ],
      "no-unused-vars": "off",
      "@typescript-eslint/no-unused-vars": "off",
      "unused-imports/no-unused-imports": "error",
      "unused-imports/no-unused-vars": [
        "warn",
        { vars: "all", varsIgnorePattern: "^_", args: "after-used", argsIgnorePattern: "^_" },
      ],
    },
  },
  // 빌드/생성물 lint 제외 — 프로젝트에 맞게 경로 추가.
  globalIgnores([".next/**", "out/**", "build/**", "next-env.d.ts"]),
  // Prettier 충돌 규칙 비활성화 — 반드시 맨 마지막.
  prettier,
]);
```
**순수 Vite/React (Next 아님) 예시 — base만 다르고 규칙은 동일:**
```js
import js from "@eslint/js";
import tseslint from "typescript-eslint";
import react from "eslint-plugin-react";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh"; // Vite 전용 (HMR)
import prettier from "eslint-config-prettier/flat";
import simpleImportSort from "eslint-plugin-simple-import-sort";
import unusedImports from "eslint-plugin-unused-imports";

export default tseslint.config(
  { ignores: ["dist/**", "build/**"] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["**/*.{ts,tsx}"],
    plugins: {
      react,
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
      "simple-import-sort": simpleImportSort,
      "unused-imports": unusedImports,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": "warn",
      // 아래 4개 규칙 블록은 Next 예시와 동일 (import 정렬·type import·미사용 제거).
      "simple-import-sort/imports": "error",
      "simple-import-sort/exports": "error",
      "@typescript-eslint/consistent-type-imports": ["error", { prefer: "type-imports", fixStyle: "separate-type-imports" }],
      "no-unused-vars": "off",
      "@typescript-eslint/no-unused-vars": "off",
      "unused-imports/no-unused-imports": "error",
      "unused-imports/no-unused-vars": ["warn", { vars: "all", varsIgnorePattern: "^_", args: "after-used", argsIgnorePattern: "^_" }],
    },
    settings: { react: { version: "detect" } },
  },
  prettier, // 반드시 맨 마지막
);
```
> Vite/React는 추가 설치 필요: `eslint-plugin-react eslint-plugin-react-hooks eslint-plugin-react-refresh typescript-eslint @eslint/js`.

> **공통:** CI가 lint/build를 돌리면(1-2의 8번) **처음엔 위 `error`들을 `warn`으로** 두고 3-6 정리 후 `error`로 올린다. 이미 config가 있으면(절대규칙 6) 덮지 말고 빠진 규칙만 병합.

### 3-5. package.json 스크립트
```json
"lint:fix": "eslint --fix",
"format": "prettier --write .",
"format:check": "prettier --check ."
```

### 3-6. 전체 코드 정리 (별도 확인 후)
```bash
pnpm lint:fix   # import 정렬 + 미사용 제거
pnpm format     # 포맷 통일
```
- **주의:** 파일이 대량(수백 개) 바뀔 수 있음 → 실행 전 반드시 재확인. 로직은 안 바뀌는 기계적 변경임을 설명.
- **도입 팁:** 처음엔 규칙을 `warn`으로 두면 CI가 안 막힘 → 위 일괄 정리 후 `error`로 승격.

### 3-7. (선택) Knip — 안 쓰는 파일/의존성 찾기
```bash
pnpm add -D knip
```
- `knip.json`에 생성물 디렉토리(`ignore`)와 진입점(Playwright e2e 등) 설정.
- **탐지 전용.** 삭제는 반드시 **개별 검증**(동적 import·CI 참조 확인) 후 사용자 승인받아 진행. CI에서 쓰는 스크립트가 "미사용"으로 오탐될 수 있으니 주의.

### 3-8. 검증
```bash
pnpm lint    # 에러 0 확인
pnpm build   # 빌드 깨지지 않는지 확인
```
결과를 한국어로 보고. 실패 시 원인과 함께 알린다.

---

## ④ "Stop 훅 넣을까요?" 묻기

전체 적용이 끝나면 물어본다: **"작업 중 자동 lint 검사(Stop 훅)를 넣을까요?"**
- Stop 훅이 뭔지 **쉽게** 설명: "Claude가 응답을 끝낼 때마다, 방금 바꾼 프론트 파일에 lint 검사를 돌려서 에러가 있으면 멈추고 고치게 하는 자동 검사대."
- 타이밍 오해 방지: **매 턴 돈다**(세션 끝 한 번이 아님). 단 바뀐 파일에만 돌아 대부분 즉시 통과(~0.05초), 프론트 바뀐 턴만 ~1.7초.
- git 커밋 훅과는 **별개**임을 설명.

---

## ⑤ Stop 훅 적용 (승인 시에만)

### 5-1. 훅 스크립트 설치
`assets/frontend-lint-stop.sh`를 프로젝트의 `.claude/hooks/frontend-lint-stop.sh`로 복사하고 실행권한 부여(`chmod +x`).
- 이 스크립트는 변경된 프론트 파일에 eslint 검사 → **에러 있으면 exit 2로 세션 종료를 막고** 사유를 Claude에 전달. 경고는 안 막음. bash 3.2 호환, 무한루프 가드 포함.
- 프로젝트 구조가 다르면(폴더명 `frontend`가 아니면) 스크립트 안의 경로를 맞게 수정.

### 5-2. 훅 등록 (`.claude/settings.local.json` — 개인용, gitignore)
```json
{
  "hooks": {
    "Stop": [
      { "hooks": [
        { "type": "command",
          "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/frontend-lint-stop.sh\"",
          "timeout": 60,
          "statusMessage": "프론트엔드 lint 검사 중..." }
      ] }
    ]
  }
}
```
- `.claude/settings.local.json`을 `.gitignore`에 추가(팀에 강제 안 함).
- **활성화 안내:** 이 파일을 세션 도중 만들면 **지금 세션엔 안 뜬다** → `/hooks` 한 번 열거나 재시작. **다음 세션부터는 자동 로드.**

### 5-3. 테스트
스크립트를 pipe-test로 검증: (1) 변경 없음→exit 0, (2) 미사용 import 넣고→exit 2, (3) `{"stop_hook_active":true}`→exit 0(루프가드). 테스트 파일은 반드시 정리.

---

## ⑥ 피드백 & 자기개선 (마무리)

작업이 끝나면 사용자에게 물어본다: **"이 추천/결과에 동의하시나요? 뺄 것·넣을 것 있나요?"**

사용자가 교정·선호를 주면 (예: "이 플러그인은 우리 팀에선 안 써", "이건 항상 넣자"), 그 내용을 **해당 레퍼런스 파일에 반영**한다:
- 프론트 플러그인 관련 → `references/web-react.md` 업데이트 (MUST/NICE/SKIP 재분류, 새 버전·대체재 반영)
- 범용 도구 관련 → `references/cross-cutting.md` 업데이트

> 이렇게 하면 **쓸수록 추천 데이터가 최신화**되어 다음 실행이 더 정확해진다 (자기개선 루프).
> 단, 레퍼런스 파일 수정도 "파일 변경"이므로 **무엇을 어떻게 바꿀지 사용자에게 확인**받고 반영한다.

---

## 커밋
설치·적용·삭제를 **의미 단위로 나눠서 커밋**하면 리뷰·되돌리기에 유리:
- `chore: add prettier + eslint tooling` (설정만)
- `style: apply prettier + import sort` (대량 포맷)
- `refactor: remove unused files (knip)` (검증된 삭제)
- `chore: add Stop hook` (훅)

커밋/push는 **사용자가 요청할 때만** 한다.

---

## 참조 파일 (필요할 때만 로드)
- 프론트(React/Next/Vite) 플러그인 표 → `references/web-react.md`
- 범용/모노레포 도구(Knip·OXLint·Biome 등) → `references/cross-cutting.md`
- Stop 훅 스크립트 원본 → `assets/frontend-lint-stop.sh`

## 출력 규칙
- 설명은 **항상 한국어 + 초심자 친화**.
- 플러그인엔 주간 다운로드·실제 채택 근거를 붙인다.
- deprecated/archived 플러그인은 명시하고 후속 대체재를 안내.
- 각 단계마다 **다음에 뭘 할지** 사용자에게 선택지를 준다.
