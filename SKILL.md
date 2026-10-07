---
name: frontend-lint-setup
description: |
  프론트엔드(Next.js / React / Vite) 프로젝트에 lint·formatter·정적분석 도구를 검사→설치→적용까지 해주는 실행형 스킬.
  Triggers on: "프론트 린트 세팅", "eslint 세팅해줘", "포매터 넣어줘", "prettier 설정",
  "frontend lint setup", "정적분석 도구 설치", "lint 도구 세팅".
  Claude Code와 Codex에서 사용. 검사 리포트 → 설치·적용 → 환경별 마무리 검사 설정.
---

# 프론트엔드 Lint/Format 세팅 (실행형)

프론트엔드 프로젝트를 검사해서 필요한 lint·formatter·정적분석 도구를 **추천하고, 확인받아 실제로 설치·적용**까지 해준다.
`recommend-static-test-tools`의 "감지→추천" 개념에서 영감을 받아, 실제 설치·적용 + Stop 훅 + 피드백 단계를 더해 새로 작성한 개인용 스킬. 레퍼런스·워크플로는 자체 작성.

---

## 실행 환경과 입력

- **Claude Code:** `/frontend-lint-setup [대상 폴더]`로 실행. 전달된 대상 폴더: `$ARGUMENTS`. 비어 있으면 자동 감지한다.
- **Codex:** `$frontend-lint-setup`으로 실행하고, 같은 메시지에 `apps/web에 적용해줘`처럼 대상 폴더를 적는다. Claude 전용 인자 치환을 기대하지 않는다.
- 대상이 없으면 아래 감지 절차를 따른다. 도구 이름·환경 정보로 현재 실행 환경을 판단하고, 폴더에 `.claude`가 있다는 이유만으로 Claude Code라고 판단하지 않는다.
- 사용자 확인이 필요하면 현재 환경에서 사용 가능한 질문 도구를 그 도구의 허용 용도에 맞게 사용한다. 없거나 해당 용도로 쓸 수 없으면 일반 대화로 묻고 답을 기다린다. Claude 전용 `AskUserQuestion`을 Codex에서 필수로 호출하지 않는다.
- 이 문서의 `references/`, `assets/` 경로는 **설치된 스킬 폴더 기준**이다. 프로젝트 작업 경로와 구분한다.
- ①~③은 공통이다. ④~⑤는 두 환경 모두 Stop 훅을 지원한다. Claude Code 설정과 Codex 설정·신뢰 절차를 구분한다. Codex의 `AGENTS.md`는 보조 지침 또는 훅 미지원 환경의 대안이다.

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
                                              →  ④ "마무리 검사 설정할까요?" 묻기  →  ⑤ (승인 시) 적용
                                              →  ⑥ 피드백 & 자기개선 (references 업데이트)
```

---

## 0️⃣ 시작 전 안전 확인 (항상 먼저)

이 스킬은 나중에 **파일을 대량으로 바꾸고 설치도** 하므로, 언제든 되돌릴 수 있게 먼저 git 상태를 확인한다.

```bash
git status --short
```
- **깨끗함(변경 없음):** 그대로 진행. (추적 중인 파일은 Git으로 되돌릴 수 있지만 새 파일·설치된 패키지까지 자동 원복되지는 않는다고 안내.)
- **커밋 안 된 변경이 있음:** 사용자에게 알리고 **선택지 제시** — 진행 전에 커밋할지 / `git stash`로 잠깐 치울지 / 그냥 진행할지. 승인 없이 진행하지 않는다.
- **git 저장소가 아님:** "되돌리기가 어려우니 git 초기화를 권합니다"라고 안내하고 진행 여부를 물어본다.

> 왜: 대량 포맷·삭제 후 "되돌리고 싶다"가 되면, 시작 시점이 커밋돼 있어야 안전하게 원복된다.

---

## ① 검사 리포트

### 1-1. 대상 감지
- 요청에 대상 폴더가 주어지면 그 폴더(위 실행 환경과 입력 참고). 없으면 `package.json`을 찾아 프론트엔드 워크스페이스 자동 감지.
- 모노레포면 프론트엔드 패키지를 고른다 (`next`, `react`, `vite` 의존성 기준).
- 감지 결과를 사용자에게 **먼저 한국어로 요약**하고 확인받는다.

### 1-2. 현재 상태 진단
`package.json` + 설정 파일 + lockfile을 읽어 아래를 파악:
1. ESLint 설정 (`eslint.config.*` / `.eslintrc.*`) — 이미 있는 플러그인
2. 포매터 (prettier / biome / 없음)
3. 테스트 러너 (vitest / jest / playwright / 없음)
4. 커밋 훅 (husky / lint-staged / pre-commit / 없음)
5. 정적분석 (knip 등)
6. **패키지 매니저** — lockfile로 감지: `pnpm-lock.yaml`→pnpm, `package-lock.json`→npm, `yarn.lock`→yarn, `bun.lock` / `bun.lockb`→bun. **이후 모든 설치 명령을 이 매니저에 맞춘다.**
7. **Tailwind 사용 여부** — `package.json`에 `tailwindcss` 있는지 + CSS 진입점(`globals.css` 등) 위치. **없으면 Tailwind 관련 플러그인/설정은 전부 건너뛴다.**
8. **CI가 lint/build를 돌리는지** — `.github/workflows/*.yml` 등에서 `lint`·`build` 실행 여부 확인. 돌린다면 3단계에서 규칙을 `warn`으로 시작해 CI 영향을 줄인다. 다만 `--max-warnings=0`이면 warn도 실패하므로 실제 CI 명령을 함께 확인한다.

### 1-3. 리서치 (기본은 가볍게, 필요할 때만 에이전트)
**기본 (대부분의 경우):** `references/web-react.md`, `references/cross-cutting.md`를 로드해 추천 후보를 잡고, 핵심 패키지 몇 개만 최신 버전·호환성을 웹 검색으로 가볍게 확인한다. 단순 요청(예: "prettier만 넣어줘")에 에이전트를 띄우지 않는다.

**병렬 에이전트는 지원되는 환경에서 아래 상황에만** 활용한다 (지원되지 않으면 같은 조사를 순차 수행) (불필요한 과다 생성 금지):
- 최신·실험적 스택이라 호환성이 불확실할 때 (예: 갓 나온 메이저 버전, React 19/Next 16 초기 등)
- 사용자가 "제대로 조사해줘"라고 명시적으로 요청할 때
- 레퍼런스가 오래돼 신뢰도가 낮다고 판단될 때

  - **Agent 1 (프레임워크 전문):** 최신 버전 / ESLint 9 flat config 호환 / React·Next 버전 호환 확인
  - **Agent 2 (채택률 검증):** 유명 OSS 5곳 이상의 실제 eslint 설정 → 채택 빈도표
  - **Agent 3 (범용 도구):** Knip/OXLint/Biome 등 비-ESLint 도구 검토

### 1-4. 리포트 제시 (한국어·친절)
각 도구를 **MUST-HAVE / NICE-TO-HAVE / SKIP**으로 분류하고, **각각이 뭘 하는지 쉬운 비유로 설명**한다. 표에 주간 다운로드·실제 채택 근거를 함께 표기.

> 📌 이 단계까지는 **아무것도 설치/수정하지 않는다.** 순수 리포트.

---

## ② "설치할까요?" 묻기

리포트를 보여준 뒤, 현재 환경에 맞는 질문 방식으로 물어본다:
- **전체 설치** / **일부만 선택** / **아직 안 함**
- 전체 코드 일괄 정리(포맷)는 파일이 대량으로 바뀌므로 **별도로 한 번 더 확인**한다.

---

## ③ 실제 설치·적용 (승인 시에만)

아래는 Next.js 16 / ESLint 9 및 React + TypeScript용 예시다. 실제 Node·프레임워크·플러그인 버전과 peerDependencies를 확인하고 기존 설정에 맞춰 적용한다. JavaScript 전용 프로젝트에 TypeScript 도구나 규칙을 강제로 추가하지 않는다.

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
- Next에서 ESLint 설정이 없다면 현재 Next 버전에 맞는 `eslint-config-next`와 호환 ESLint를 설치한다. 아래 Vite 베이스로 대체하지 않는다.
- **베이스 ESLint가 없으면**(순수 Vite·맨바닥 프로젝트 — `eslint-config-next`도 없는 경우) 먼저 base부터 설치: `eslint @eslint/js globals eslint-plugin-react eslint-plugin-react-hooks`(+ TypeScript면 `typescript-eslint`, + Vite면 `eslint-plugin-react-refresh`). Next는 보통 `create-next-app`이 이미 깔아둠. (위 MUST-HAVE 설치는 base 위에 얹는 것)

### 3-2. Prettier 설정 (`.prettierrc.json`)
**Tailwind v4 사용 시:**
```json
{
  "plugins": ["prettier-plugin-tailwindcss"],
  "tailwindStylesheet": "./src/app/globals.css",
  "tailwindFunctions": ["cn", "clsx", "cva"]
}
```
> ⚠️ Tailwind v4는 `tailwindStylesheet`에 **실제 CSS 진입점 경로**를 넣어야 클래스 정렬이 작동한다. 프로젝트에서 globals.css 위치를 찾아 넣을 것.

**Tailwind v3 사용 시:** `tailwindStylesheet` 대신 `tailwindConfig`에 실제 `tailwind.config.*` 경로를 지정한다. 커스텀 preset·색상 등이 로드되는지도 작은 샘플로 확인한다.

**Tailwind 미사용 시:** tailwind 항목을 전부 빼고, 필요한 기본값만. (없으면 Prettier 기본값이 적용되므로 최소 설정으로 충분)
```json
{
  "semi": true,
  "singleQuote": false
}
```

### 3-3. `.prettierignore` — 빌드/생성물 제외
`.next/`, `out/`, `build/`, `node_modules/`, `pnpm-lock.yaml`, `next-env.d.ts`, 생성된 docs/번들 등 앱 코드가 아닌 것들.

### 3-4. ESLint 설정 (기존 형식 유지)
- `.eslintrc.*`를 사용하는 ESLint 8 프로젝트는 legacy 형식을 유지한다. `extends` 끝에 `prettier`를 추가하고 `plugins`는 이름 배열로 병합한다. 스킬 예시를 적용하려고 ESLint 메이저를 올리거나 flat config를 병행 생성하지 않는다.
- 아래 flat config 예시는 flat config 프로젝트에만 적용한다. 설치할 플러그인의 peerDependencies를 실제 ESLint·TypeScript 플러그인 버전과 대조한다.
- `--max-warnings 0` 환경에서 검증만 요청받았다면 새 규칙을 별도 검증 설정과 임시 fixture에 적용한다. 기존 코드 전체에 warn을 추가하고 정상 도입이라고 보고하지 않는다.

- 플러그인: `simple-import-sort`(import 정렬), `unused-imports`(미사용 제거), `@typescript-eslint/consistent-type-imports`(`import type` 강제)
- `eslint-config-prettier`는 **맨 마지막 요소로 추가** (`prettier`는 배열이 아닌 설정 객체이므로 `...prettier`로 펼치지 않는다) (포맷 규칙 충돌 방지)
- import 그룹 예시: `[["^react","^next","^@?\\w"], ["^@(/|src|app|features|common)(/|$)"], ["^\\."], ["^.+\\.s?css$"]]`
- 생성/벤더 JS(빌드 산출물)는 `globalIgnores`에 추가해 lint 소음 제거

**Next.js + TypeScript + ESLint 9 flat config 예시:**
JavaScript 전용 Next 프로젝트는 `nextTs` import·spread와 `@typescript-eslint/*` 규칙을 생략한다.
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
import { defineConfig } from "eslint/config";
import js from "@eslint/js";
import globals from "globals";
import tseslint from "typescript-eslint";
import react from "eslint-plugin-react";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh"; // Vite 전용 (HMR)
import prettier from "eslint-config-prettier/flat";
import simpleImportSort from "eslint-plugin-simple-import-sort";
import unusedImports from "eslint-plugin-unused-imports";

export default defineConfig([
  { ignores: ["dist/**", "build/**"] },
  js.configs.recommended,
  ...tseslint.configs.recommended.map((config) => ({
    ...config,
    files: ["**/*.{ts,tsx,mts,cts}"],
  })),
  {
    files: ["**/*.{js,jsx,mjs,cjs,ts,tsx,mts,cts}"],
    languageOptions: {
      globals: globals.browser,
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
    plugins: {
      react,
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
      "simple-import-sort": simpleImportSort,
      "unused-imports": unusedImports,
    },
    rules: {
      ...react.configs.recommended.rules,
      ...react.configs["jsx-runtime"].rules,
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": "warn",
      // 아래 4개 규칙 블록은 Next 예시와 동일 (import 정렬·type import·미사용 제거).
      "simple-import-sort/imports": "error",
      "simple-import-sort/exports": "error",
      "no-unused-vars": "off",
      "unused-imports/no-unused-imports": "error",
      "unused-imports/no-unused-vars": ["warn", { vars: "all", varsIgnorePattern: "^_", args: "after-used", argsIgnorePattern: "^_" }],
    },
    settings: { react: { version: "detect" } },
  },
  {
    files: ["**/*.{ts,tsx,mts,cts}"],
    rules: {
      "@typescript-eslint/consistent-type-imports": ["error", { prefer: "type-imports", fixStyle: "separate-type-imports" }],
      "@typescript-eslint/no-unused-vars": "off",
      "react/prop-types": "off", // TypeScript로 props 검증
    },
  },
  prettier, // 반드시 맨 마지막
]);
```
> Vite/React는 추가 설치 필요: `eslint-plugin-react eslint-plugin-react-hooks eslint-plugin-react-refresh typescript-eslint @eslint/js globals`. JavaScript 전용이면 `typescript-eslint` import·추천 설정·TS 전용 규칙 블록을 생략한다. `defineConfig`는 ESLint에서 가져오므로 그대로 유지한다. Vite가 아닌 React 프로젝트는 `reactRefresh` import·플러그인 등록·규칙도 생략한다.

> **공통:** CI가 lint/build를 돌리면(1-2의 8번) **처음엔 위 `error`들을 `warn`으로** 두고 3-6 정리 후 `error`로 올린다. 이미 config가 있으면(절대규칙 6) 덮지 말고 빠진 규칙만 병합.

### 3-5. package.json 스크립트
기존 스크립트를 보존하고 **없는 항목만** 대상 패키지에 추가한다. 기존 lint가 Biome·OXLint 등 다른 유효한 도구를 실행하면 유지하고 전환을 강제하지 않는다. `next lint`처럼 현재 프로젝트 버전에서 더 이상 지원하지 않는 명령만 버전에 맞춰 수정한다.
```json
"lint": "eslint .",
"lint:fix": "eslint . --fix",
"format": "prettier --write .",
"format:check": "prettier --check ."
```

### 3-6. 전체 코드 정리 (별도 확인 후)
```bash
pnpm lint:fix   # import 정렬 + 미사용 제거
pnpm format     # 포맷 통일
```
- **주의:** 파일이 대량(수백 개) 바뀔 수 있음 → 실행 전 반드시 재확인. 포맷 외에 import 제거·정렬도 포함되므로 부수효과가 있는 모듈 로딩에 영향을 줄 수 있음을 설명하고 diff와 테스트를 확인한다.
- **도입 팁:** CI가 warning을 허용하는 경우 처음엔 규칙을 `warn`으로 도입 → 위 일괄 정리 후 `error`로 승격.

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
실제로 정의된 lint/build 스크립트와 감지한 매니저로 검증한다. build가 없는 프로젝트에서는 임의 명령을 실행하거나 성공했다고 보고하지 말고 미실행 사유를 적는다. 결과를 한국어로 보고하고 실패 시 원인과 함께 알린다.

---

## ④ "마무리 검사 설정할까요?" 묻기

**Codex:** "작업을 마칠 때 변경 파일에 ESLint를 실행하고, 실패하면 추가 수정을 요청하는 Stop 훅을 넣을까요?"라고 묻는다. 이미 훅 설치를 요청했다면 다시 묻지 않고 ⑤-B로 간다. Codex에도 `/hooks`가 있으며, 새 훅은 사용자 검토·신뢰 전에는 실행되지 않는다고 안내한다.

**Claude Code:** 전체 적용이 끝나면 물어본다: **"작업 중 자동 lint 검사(Stop 훅)를 넣을까요?"**
- Stop 훅이 뭔지 **쉽게** 설명: "Claude가 응답을 끝낼 때마다, 방금 바꾼 프론트 파일에 lint 검사를 돌려서 에러가 있으면 멈추고 고치게 하는 자동 검사대."
- 타이밍 오해 방지: **매 턴 돈다**(세션 끝 한 번이 아님). 작업 트리에서 변경된 대상 파일만 검사하며, 실행 시간은 프로젝트 크기와 규칙에 따라 달라진다.
- git 커밋 훅과는 **별개**임을 설명.

---

## ⑤-A Claude Code Stop 훅 적용 (승인 시에만)

### 5-1. 훅 스크립트 설치
`assets/frontend-lint-stop.sh`를 프로젝트의 `.claude/hooks/frontend-lint-stop.sh`로 복사하고 실행권한 부여(`chmod +x`).
- 이 스크립트는 변경된 프론트 파일에 eslint 검사 → **에러 있으면 exit 2로 추가 수정을 요청하고** 사유를 Claude에 전달. 경고는 안 막음. bash 3.2 호환, 무한루프 가드 포함.
- 프로젝트 구조가 다르면(폴더명 `frontend`가 아니면) 스크립트 안의 디렉터리 확인·Git 경로·상대경로 변환·실행 디렉터리를 모두 실제 대상에 맞춘다. 기본 실행기는 `npx --no-install`이다. Yarn PnP 등 npm 실행기로 로컬 ESLint를 찾을 수 없는 환경은 해당 매니저의 로컬 실행 명령으로 바꾸고 실검증한다.

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
- 위 JSON은 구조 예시다. 기존 settings와 다른 Stop 훅을 보존하고 동일 command가 없을 때만 배열에 추가한다.
- `.claude/settings.local.json`을 `.gitignore`에 추가(팀에 강제 안 함).
- **활성화 안내:** 이 파일을 세션 도중 만들면 **지금 세션엔 안 뜬다** → `/hooks` 한 번 열거나 재시작. **다음 세션부터는 자동 로드.**

### 5-3. 테스트
스크립트를 pipe-test로 검증: (1) 변경 없음→exit 0, (2) 미사용 import 넣고→exit 2, (3) `{"stop_hook_active":true}`→exit 0(루프가드). 테스트 파일은 반드시 정리. 재개된 턴은 루프 가드로 검사를 건너뛰므로 에이전트가 수정 후 직접 재검사해야 한다. 이 훅은 통과할 때까지 무조건 차단하는 장치가 아니며 CI를 대체하지 않는다.

---

## ⑤-B Codex Stop 훅 적용 (승인 시에만)

설치·신뢰·검증 절차는 **`references/codex-stop-hooks.md`를 읽고 따른다.** 공통 스크립트 `assets/frontend-lint-stop.sh`를 `.codex/hooks/`에 복사하고 `--codex`로 등록한다. 이 모드는 입력 JSON의 `cwd`를 사용하고 성공 시 `{}`를 출력한다.

- 기존 `.codex/hooks.json` 또는 `config.toml`의 훅을 보존·병합하고 중복 등록하지 않는다.
- 파일 설치, 사용자의 훅 신뢰, 실제 Stop 이벤트 검증을 구분해서 보고한다. 설치만으로 활성화됐다고 말하지 않는다.
- 기본 훅은 변경 파일 ESLint만 검사한다. `tsc`·포매터를 실행했다고 보고하지 않는다. 타입 검사를 추가 요청받으면 실제 프로젝트 명령과 실행 시간을 확인해 별도로 연결한다.
- 재개된 턴에는 루프 가드가 적용된다. 수정 후 명시적 재검사와 기존 CI를 유지한다.

### AGENTS.md 보조 지침 / 훅 미지원 시 대안

사용자가 지침만 요청했거나 실행 환경에서 훅을 지원하지 않는 경우에는 아래 절차를 사용한다. 훅 설치를 지침으로 조용히 대체하지 말고 제한과 적용 방식을 설명한다.


1. 대상 패키지와 상위 경로의 `AGENTS.md`, `AGENTS.override.md`를 읽어 적용 범위와 기존 검사 지침을 확인한다. 기존 내용을 보존하고 중복 지침은 추가하지 않는다. override가 우선되는 경우 새 지침이 실제로 읽힐 파일에 병합한다.
2. `assets/codex-lint-instructions.md`를 참고해 **저장소 루트의 AGENTS.md**(비어 있지 않은 override가 우선되면 해당 파일)에 대상 패키지 경로를 명시한 검사 지침을 병합한다. Codex는 시작 시 저장소 루트에서 현재 작업 디렉터리까지 지침을 읽으므로, 모노레포의 하위 패키지에만 추가하면 루트에서 시작할 때 빠질 수 있다. 기존 하위 지침과도 충돌·중복을 확인한다. 파일 전체를 덮어쓰지 않는다. git 저장소가 아니면 실제 시작 디렉터리를 기준으로 한다.
3. 템플릿의 경로·명령을 감지된 패키지 매니저와 실제 `package.json` 스크립트에 맞춘다. 템플릿은 저장소 루트 기준 `frontend` 패키지의 pnpm 프로젝트용이며, 없는 스크립트를 그대로 안내하지 않는다.
4. 실제 lint 명령을 실행하고 결과를 보고한다. 실패를 숨기거나 검사 생략을 성공으로 보고하지 않는다. 이 설정만으로 CI·git 훅·런타임 종료 차단이 생기지는 않는다.
5. 새 Codex 세션을 대상 프로젝트에서 시작해 적용된 지침을 확인하도록 안내한다.

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
- Codex 마무리 검사 지침 템플릿 → `assets/codex-lint-instructions.md`
- Claude Code·Codex 공통 Stop 훅 스크립트 → `assets/frontend-lint-stop.sh`
- Codex Stop 훅 설치·신뢰·검증 → `references/codex-stop-hooks.md`

## 출력 규칙
- 설명은 **항상 한국어 + 초심자 친화**.
- 플러그인엔 주간 다운로드·실제 채택 근거를 붙인다.
- deprecated/archived 플러그인은 명시하고 후속 대체재를 안내.
- 각 단계마다 **다음에 뭘 할지** 사용자에게 선택지를 준다.
