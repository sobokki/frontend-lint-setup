# 범용/모노레포 도구 (ESLint 외)

> 기준: 2026-09 검증. 프레임워크 무관하게 프론트엔드에 쓸 수 있는 도구들.
> 실행 시 웹 검색으로 최신 상태를 재확인할 것.

---

## MUST-HAVE / NICE-TO-HAVE

| 도구 | 분류 | 역할 (쉬운 설명) | 메모 |
|---|---|---|---|
| **Knip** | NICE-TO-HAVE | 안 쓰는 파일·export·의존성 찾는 창고 정리기 | archived된 depcheck/ts-prune의 후계. Next·pnpm workspace 인식. **탐지 전용, 자동삭제 아님**. CI/가끔 실행 |
| **@typescript-eslint/consistent-type-imports** | NICE-TO-HAVE | `import type` 강제 | 문법 규칙 → 느린 타입체크 config 불필요. 저렴·자동수정 |
| **lint-staged + 훅 러너** | 선택 | 커밋 직전 staged 파일만 검사 | 기존 pre-commit 프레임워크가 있으면 거기에 얹는 게 깔끔(husky 중복 피함) |

## WATCH (관망 — 아직 전환 권장 안 함)

| 도구 | 상태 | 왜 아직인가 |
|---|---|---|
| **Biome** | 2.x, 빠름(포맷+린트 통합) | **Tailwind 클래스 정렬이 미완성**(config 못 읽고 공백 뭉갬) — Tailwind 팀엔 퇴보. 포매터로만 쓰는 건 고려 가능 |
| **OXLint** | 1.x stable(코어), JS/타입 플러그인 alpha | 코어는 50~100배 빠르나, 커스텀/타입인식 플러그인이 아직 미성숙. `eslint-plugin-oxlint`로 CI 선행검사 정도는 가능 |

## SKIP / 대체됨

| 도구 | 대체재 |
|---|---|
| depcheck / ts-prune / unimported | **Knip** (모두 archived) |
| eslint-plugin-deprecation | `@typescript-eslint/no-deprecated` (단 타입체크 필요) |

---

## Knip 도입 시 주의 (실전 경험)

첫 실행은 **오탐이 많다.** 아래를 설정으로 걸러야 진짜 findings가 보인다:
- 생성물/벤더 디렉토리 `ignore` 처리: 빌드 산출물, 문서 생성물, 벤더 번들(minified JS) 등
- 진입점 등록: Playwright e2e, 매뉴얼 실행 스크립트 등
- **CI에서 쓰는 스크립트가 "미사용"으로 오탐될 수 있음** — GitHub 워크플로를 Knip이 안 읽기 때문. `entry`에 등록하거나 `ignoreDependencies`로 예외.

삭제는 반드시 **파일별 개별 검증** 후:
- 정적 import뿐 아니라 **동적 import(`next/dynamic`, `import()`)**·문자열 참조·CI 참조까지 확인
- "이름만 같은 다른 파일"에 속지 말 것 (grep 매치 ≠ 실제 import)
- 검증 후 사용자 승인받아 삭제. `pnpm build`로 안 깨지는지 확인.

## 커밋 훅: lint-staged vs 기존 pre-commit

이미 Python `pre-commit` 프레임워크를 쓰는 모노레포라면, husky를 새로 넣기보다 **기존 `.pre-commit-config.yaml`에 `local` 훅으로 lint-staged를 얹는 것**이 낫다. 훅 매니저 2개가 `.git/hooks`를 두고 다투는 문제를 피할 수 있다. 훅 없이 **CI에서만** 검사하는 것도 유효한 선택.

## 성능 팁

- ESLint 캐시: `eslint . --cache`
- 타입체크 규칙은 ~30배 느림 → CI 전용으로 돌리는 것 고려
- `import/no-cycle` 규칙은 단독으로도 lint를 크게 느리게 함 → 필요시 CI 전용
