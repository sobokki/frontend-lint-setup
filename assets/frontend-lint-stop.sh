#!/usr/bin/env bash
# Claude Code / Codex Stop 훅 — 턴 종료 시 변경된 frontend 파일에 ESLint 검사.
# Codex에서는 --codex로 실행: 입력 cwd 사용, 성공 시 JSON 출력.
# 에러가 있으면 exit 2 와 stderr 로 에이전트에 추가 수정을 요청.
# 경고(warning)는 종료를 막지 않음 (ESLint 는 에러에서만 exit≠0).
# bash 3.2 호환 (macOS 기본 bash) — mapfile 미사용.
set -uo pipefail

mode="${1:---claude}"
case "$mode" in
  --claude) ;;
  --codex)
    # Codex Stop은 성공 시 stdout에 JSON을 요구한다.
    trap 'status=$?; if [ "$status" -eq 0 ]; then printf "{}\n"; fi' EXIT
    ;;
  *) echo "사용법: $0 [--claude|--codex]" >&2; exit 2 ;;
esac

input=$(cat)

# 무한 루프 방지: 이미 Stop 훅 재개로 진입한 상태면 통과.
# Node는 ESLint 실행에도 필요하다. JSON 문자열 검색은 공백·중첩 값에 취약하다.
active=$(printf '%s' "$input" | node -e '
  try {
    const data = JSON.parse(require("fs").readFileSync(0, "utf8"));
    if (!data || typeof data !== "object" || Array.isArray(data)) process.exit(1);
    console.log(data.stop_hook_active === true ? "true" : "false");
  } catch {
    process.exit(1);
  }
') || { echo "Stop 훅 입력 JSON 또는 Node 실행을 확인하세요." >&2; exit 2; }
[ "$active" = true ] && exit 0

project_dir="${CLAUDE_PROJECT_DIR:-$PWD}"
if [ "$mode" = --codex ]; then
  project_dir=$(printf '%s' "$input" | node -e '
    const data = JSON.parse(require("fs").readFileSync(0, "utf8"));
    if (typeof data.cwd !== "string" || !data.cwd) process.exit(1);
    process.stdout.write(data.cwd);
  ') || { echo "Codex Stop 입력에 유효한 cwd가 필요합니다." >&2; exit 2; }
fi
repo_root=$(git -C "$project_dir" rev-parse --show-toplevel 2>/dev/null) || exit 0
[ -d "$repo_root/frontend" ] || exit 0

# 변경(스테이지/미스테이지) + 미추적 frontend 파일 중 lint 대상 확장자.
files=()
while IFS= read -r -d '' line; do
  # NUL 구분으로 한글·공백·개행 파일명을 그대로 전달한다.
  case "$line" in
    *.ts|*.tsx|*.js|*.jsx|*.mjs|*.cjs|*.mts|*.cts) ;;
    *) continue ;;
  esac
  [ -f "$repo_root/$line" ] || continue
  relative="./${line#frontend/}"
  duplicate=false
  if [ "${#files[@]}" -gt 0 ]; then
    for existing in "${files[@]}"; do
      if [ "$existing" = "$relative" ]; then duplicate=true; break; fi
    done
  fi
  if [ "$duplicate" = false ]; then files+=("$relative"); fi
done < <(
  {
    git -C "$repo_root" diff --name-only -z --diff-filter=ACMR -- 'frontend/'
    git -C "$repo_root" diff --cached --name-only -z --diff-filter=ACMR -- 'frontend/'
    git -C "$repo_root" ls-files -z --others --exclude-standard -- 'frontend/'
  } 2>/dev/null
)

if [ "${#files[@]}" -eq 0 ]; then exit 0; fi

cd "$repo_root/frontend" || exit 0
out=$(npx --no-install eslint "${files[@]}" 2>&1)
if [ $? -eq 0 ]; then exit 0; fi

{
  echo "턴 종료 전 ESLint 에러를 수정하고 다시 검사하세요 (변경된 frontend 파일):"
  echo "$out"
} 1>&2
exit 2
