# React 웹 (Next.js / Vite) — ESLint & 도구 추천

> 기준: 2026-09 검증. Next.js 16 + React 19 + TypeScript 5 + ESLint 9(flat config) 실제 도입 경험 반영.
> 검증 소스: 실제 프로젝트 적용 + OSS 10곳 설정 조사(cal.com, formbricks, supabase/studio, trpc, shadcn-ui/ui, vercel/commerce, documenso, dub, midday, twenty).

이 표는 "정답 후보"의 출발점이다. 실행 시 웹 검색으로 **최신 버전·호환성**을 다시 확인할 것.

---

## MUST-HAVE — 없으면 채워야 할 것

| 도구 | 최신(확인 필요) | 역할 (쉬운 설명) | 근거 |
|---|---|---|---|
| **prettier** + **eslint-config-prettier** | prettier 3.x | 자동 문서 정렬기 + ESLint와 교통정리 | 포매터 부재가 가장 큰 공백. Next 16 공식 권장 경로 |
| **prettier-plugin-tailwindcss** | 0.8.x | Tailwind 클래스 자동 정렬 (v4 대응) | Tailwind Labs 공식. **Tailwind 안 쓰면 제외** |
| **eslint-plugin-simple-import-sort** | 14.x | import "재료 목록" 자동 정렬 | 결정론적·자동수정. OSS 대부분이 어떤 형태로든 import 정렬 사용 |
| **eslint-plugin-unused-imports** | 4.x | 안 쓰는 import 자동 삭제 | `no-unused-vars`는 경고만 함 — 이건 자동 제거 |

> ⚠️ import 정렬은 **한 가지 방식만** 쓴다. `unused-imports`(제거)는 Prettier 대응물이 없으니 위 ESLint 페어를 쓰고, Prettier import-sort 플러그인은 같이 넣지 않는다(이중 정렬 충돌).

## NICE-TO-HAVE — 팀 판단

| 도구 | 역할 | 언제 |
|---|---|---|
| **@typescript-eslint/consistent-type-imports** | 타입은 `import type`로 명시 | 저렴(문법 규칙, 타입체크 불필요)·자동수정. 지금 넣기 좋음 |
| **eslint-plugin-jsx-a11y** | 접근성 검사 | **eslint-config-next 16엔 미포함** — 필요하면 직접 추가. 고객용 화면 많을 때 |
| **@tanstack/eslint-plugin-query** | TanStack Query 실수 감지 | TanStack Query 사용 시. 단 조사한 10곳 채택 0 — 선택 |
| **eslint-plugin-unicorn** | 140+ 유용 규칙 | recommended가 공격적 → React용 override 필요(no-null 등). trpc 사용 |

## SKIP — 넣지 말 것

| 도구 | 이유 |
|---|---|
| 단독 `eslint-plugin-react` / `react-hooks` (Next 프로젝트) | `eslint-config-next`에 이미 번들 — 추가 시 충돌 |
| `eslint-plugin-tailwindcss` | Tailwind v4에서 깨짐 → `prettier-plugin-tailwindcss` 사용 |
| `@typescript-eslint/no-deprecated` | 유용하나 **타입체크 config 필요**(~30배 느림). 타입 CI 패스 도입 전엔 스킵 |
| `eslint-plugin-react-compiler`(단독) | deprecated → `eslint-plugin-react-hooks` 최신에 병합됨 |

---

## 베이스 config 선택

- **Next.js:** `eslint-config-next`(core-web-vitals + typescript). react·react-hooks·next 플러그인 번들. jsx-a11y는 **미포함**. typescript 프리셋은 **타입체크 미적용**.
- **순수 Vite/React:** `typescript-eslint` + `eslint-plugin-react` + `eslint-plugin-react-hooks` + (Vite면)`eslint-plugin-react-refresh`.
- 위 어느 쪽이든 그 위에 MUST-HAVE(simple-import-sort·unused-imports·prettier)를 얹는다.

## 실제 채택 경향 (2026, OSS 10곳)

```
린터:   ESLint 5/10 · Biome 3/10(cal.com·midday·documenso) · OXLint 1(twenty) · Prettier만 1(vercel/commerce)
포매터: Prettier 7/10 · Biome 3/10
import 정렬: ~9/10   Tailwind 정렬: 7/10   typescript-eslint: ESLint 사용자 5/5
jsx-a11y 명시: 1/10   @tanstack/query 플러그인: 0/10   Knip: 1/10
```
→ **신호:** ESLint 합의가 갈라지는 중(Biome·OXLint로 이동). 하지만 "ESLint 유지 + Prettier + import 정렬"이 여전히 가장 안전한 기본. Biome/OXLint 전환은 관망 권장(아래 cross-cutting 참고).

## Tailwind v4 주의

- `prettier-plugin-tailwindcss`는 **`tailwindStylesheet`에 실제 CSS 진입점**(예: `./src/app/globals.css`)을 넣어야 정렬 작동. Tailwind v4는 JS config가 없어서 이 경로가 필수.
- `tailwindFunctions: ["cn","clsx","cva"]`를 넣으면 helper 안의 클래스도 정렬됨.
