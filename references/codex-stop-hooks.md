# Codex Stop 훅

Codex에서 마무리 검사 훅을 설치할 때 읽는다. 공식 사양: https://learn.chatgpt.com/docs/hooks

## 지원 확인과 등록

1. `codex --version`, `codex features list`와 현재 공식 Hooks 문서를 확인한다. CLI 0.160.1에서 `hooks` stable/true를 확인했다. 다른 실행 환경까지 같은 버전·지원이라고 가정하지 않는다. 미지원이면 그 이유를 설명하고 AGENTS.md 지침을 대안으로 제공한다.
2. 활성 설정의 기존 훅을 먼저 확인한다. 프로젝트의 `.codex/hooks.json`과 `.codex/config.toml` inline `[hooks]`는 함께 로드되므로 두 곳에 같은 훅을 넣지 않는다. 사용자·플러그인 훅에 같은 검사가 있는지도 확인한다. 기존 파일 전체를 출력해 비밀값을 노출하지 않는다.
3. `assets/frontend-lint-stop.sh`를 대상 저장소의 `.codex/hooks/frontend-lint-stop.sh`로 복사한다. 경로가 `frontend/`가 아니면 스크립트의 디렉터리 확인·Git 경로·상대경로 변환·실행 디렉터리를 모두 맞춘다. Yarn PnP 등에서는 로컬 ESLint 실행기도 맞춘다. 자동 수정 옵션은 넣지 않는다.
4. 새 설정은 아래 JSON을 사용하되 기존 JSON이 있으면 `hooks.Stop`에 병합한다. 이미 inline TOML 훅을 쓰면 같은 구조로 그 파일에 병합한다. 기존 이벤트·명령·메타데이터를 보존하고 동일 명령은 한 번만 등록한다.

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash \"/ABSOLUTE/REPO/.codex/hooks/frontend-lint-stop.sh\" --codex",
            "timeout": 60,
            "statusMessage": "변경된 프론트엔드 ESLint 검사 중..."
          }
        ]
      }
    ]
  }
}
```

`/ABSOLUTE/REPO`는 실제 저장소 경로로 치환한다. command는 셸 코드이므로 실제 경로의 공백·따옴표·`$`·백틱을 셸 규칙에 맞게 이스케이프한 뒤 JSON 직렬화한다. JSON 이스케이프만으로 셸 인용을 대신하지 않는다. 개인별 절대 경로를 팀 공용 설정으로 그대로 배포하지 않는다. 팀 공유를 원하면 각 checkout에 맞춰 등록하거나, 시작 경로에서 Git 루트를 찾는 명령을 실제 하위 디렉터리·worktree에서도 검증한다.

## 검토·신뢰와 활성화

- 프로젝트 `.codex/` 설정은 프로젝트가 신뢰된 경우에 로드된다. 새로 만들거나 바꾼 비관리형 훅은 정의의 해시별로 사용자의 검토·신뢰가 필요하다.
- 새 Codex 세션에서 `/hooks`를 열고 등록된 명령을 검토·신뢰하도록 안내한다. 파일을 생성했다고 훅 실행까지 완료됐다고 보고하지 않는다.
- 사용자의 신뢰 저장소를 대신 변경하지 않는다. 일반 설치에 `--dangerously-bypass-hook-trust`를 넣지 않는다. 이 옵션은 훅 소스를 별도로 검토한 격리된 일회성 자동 테스트에만 사용할 수 있으며, 사용한 경우 검증 보고에 명시한다.
- 사용자가 해야 하는 단계가 남으면 설치·직접 스크립트 검사까지 먼저 끝내고, 마지막에 사용자 신뢰 단계가 남았다고 정확히 설명한다.

## 입출력과 검사 범위

- 반드시 `--codex`로 실행한다. 공통 스크립트는 stdin JSON의 `cwd`에서 Git 루트를 찾는다. Claude 환경 변수에 의존하지 않는다.
- 성공: exit 0 + stdout `{}`. ESLint 출력은 캡처하므로 Codex의 JSON 출력을 오염시키지 않는다.
- 실패: exit 2 + stderr 검사 결과. Codex는 이 내용을 후속 프롬프트로 받아 작업을 계속한다. ESLint 설정 오류도 통과시키지 않는다.
- `stop_hook_active: true`이면 exit 0 + `{}`로 재진입을 건너뛴다. 무한 루프를 막기 위한 제한이며 **통과할 때까지 계속 차단하는 보장**은 아니다. 에이전트가 수정 후 직접 재검사하도록 실패 메시지를 전달한다.
- 기본 대상은 Git의 staged/unstaged/untracked 변경 파일 중 JS·TS 계열이다. `tsc`, 전체 프로젝트 검사, 포매터, 자동 수정은 기본 훅에 포함되지 않는다. 경고도 실패시키려면 실제 CI 정책과 맞춰 `--max-warnings 0`을 추가하고 검증한다. 기본 훅은 ESLint의 오류만 실패로 취급한다.
- AGENTS.md의 기존 검사 지침과 CI는 유지한다. 기존에 충분한 지침이 있으면 중복 추가하지 않는다.

## 검증

실제 사용자 작업을 훼손하지 않는 임시 파일 또는 격리 저장소에서 확인한다.

1. 변경 없음 → exit 0, stdout이 유효한 `{}` JSON.
2. 변경 파일에 현재 규칙의 확실한 오류 → exit 2, stderr에 파일·규칙.
3. 오류 수정 후 다시 실행 → exit 0, `{}`.
4. 입력에 `stop_hook_active: true` → ESLint를 재호출하지 않고 통과.
5. 셸 cwd와 입력 cwd가 달라도 입력 cwd의 저장소 검사. 공백 경로·staged·untracked 파일 포함.
6. 신뢰된 훅을 실제 Codex 세션에서 실행해 Stop 실패 피드백 → 수정 → 명시적 재검사를 확인한다. 직접 스크립트 실행과 실제 lifecycle 검증 결과를 구분한다. 테스트 파일은 정리한다.

검증 결과에는 사용한 Codex/ESLint 버전, 직접 스크립트 검사인지 실제 Stop 이벤트인지, 신뢰 방식, 남은 제한을 기록한다.
