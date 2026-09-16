#!/usr/bin/env bash
# Claude Code Stop 훅 — 세션 종료 시 변경된 frontend 파일에 ESLint 검사.
# 에러가 있으면 exit 2 로 종료를 막고 stderr 로 사유를 Claude 에 전달.
# 경고(warning)는 종료를 막지 않음 (ESLint 는 에러에서만 exit≠0).
# bash 3.2 호환 (macOS 기본 bash) — mapfile 미사용.
set -uo pipefail

input=$(cat)

# 무한 루프 방지: 이미 Stop 훅 재개로 진입한 상태면 통과.
case "$input" in
*'"stop_hook_active":true'* | *'"stop_hook_active": true'*) exit 0 ;;
esac

repo_root=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
[ -d "$repo_root/frontend" ] || exit 0

# 변경(스테이지/미스테이지) + 미추적 frontend 파일 중 lint 대상 확장자.
files=()
while IFS= read -r line; do
  [ -n "$line" ] && files+=("${line#frontend/}")
done < <(
  {
    git -C "$repo_root" diff --name-only --diff-filter=ACMR HEAD -- 'frontend/'
    git -C "$repo_root" ls-files --others --exclude-standard -- 'frontend/'
  } 2>/dev/null | sort -u | grep -E '\.(ts|tsx|js|jsx|mjs)$'
)

if [ "${#files[@]}" -eq 0 ]; then exit 0; fi

cd "$repo_root/frontend" || exit 0
out=$(npx --no-install eslint --no-warn-ignored "${files[@]}" 2>&1)
if [ $? -eq 0 ]; then exit 0; fi

{
  echo "세션 종료 전 ESLint 에러를 수정하세요 (변경된 frontend 파일):"
  echo "$out"
} 1>&2
exit 2
