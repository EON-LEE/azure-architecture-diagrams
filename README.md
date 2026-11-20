# azure-architecture-diagrams

Microsoft 공식 아이콘과 Microsoft Learn의 다이어그램 지침에 따라 Azure 서비스 아키텍처 다이어그램을 그리는 에이전트 스킬입니다. 에이전트가 YAML 사양을 작성하면 렌더러가 draw.io, SVG, PNG 파일을 만들고 레이아웃과 디자인을 검증합니다.

## 기능

- **공식 아이콘:** Azure, Microsoft Fabric, Microsoft 365, Power Platform, Microsoft Entra, Dynamics 365의 6개 아이콘 팩을 씁니다. 아이콘은 Microsoft 공식 배포처에서 내려받아 사용자 캐시에 저장합니다.
- **참조 아키텍처 스타일:** 기본 스타일 `reference`는 얇은 직각 범위 경계, 64px 공식 아이콘, 직교선, 선 옆의 번호 배지, 오른쪽 단계 패널, 아래쪽 공통 서비스 밴드로 그립니다. `card` 스타일은 노드를 상자형 카드로 그립니다.
- **번호 단계:** 그림의 번호 배지와 오른쪽 패널의 단계 설명을 1:1로 맞춥니다. 번호가 맞지 않으면 경고합니다.
- **자동 검증:** 겹침, 캔버스 이탈, 글자 잘림, 엣지 교차, 큰 빈 공간, 정렬 어긋남을 검사합니다. 대비가 WCAG 2.1 기준보다 낮거나 흐름을 색으로만 구분하면 경고합니다.
- **출처 기록:** `icon-provenance.json`에 아이콘별 출처 URL, 이용 조건, SHA-256 해시, 사용 위치를 기록합니다.

## 구성

모든 경로는 `skills/azure-architecture-diagram/` 아래에 있습니다. 스킬 문서는 한국어로 작성했습니다.

| 경로 | 내용 |
| --- | --- |
| [`SKILL.md`](skills/azure-architecture-diagram/SKILL.md) | 작업 절차, 다이어그램 규칙, 디자인 기준, 명령 |
| [`scripts/`](skills/azure-architecture-diagram/scripts) | 렌더러 `render.py`와 아이콘 도구 `icon_tool.py` |
| [`references/spec-format.md`](skills/azure-architecture-diagram/references/spec-format.md) | YAML 사양의 모든 키, 좌표 표현식, 엣지 경로 지정 방법 |
| [`references/style-guide.md`](skills/azure-architecture-diagram/references/style-guide.md) | 배치 순서, 디자인 기능, 검증 코드별 수정 방법, PNG 점검 목록 |
| [`references/icon-catalog.md`](skills/azure-architecture-diagram/references/icon-catalog.md) | 아이콘 팩, 키 형식, 자주 쓰는 키, 대체 아이콘, 이용 조건 |
| [`references/learn-sources.md`](skills/azure-architecture-diagram/references/learn-sources.md) | 근거로 쓰는 Microsoft Learn 문서와 각 문서에서 가져온 규칙 |
| [`examples/baseline-web-app.yaml`](skills/azure-architecture-diagram/examples/baseline-web-app.yaml) | 영역 중복 App Service 기준 아키텍처의 예시 사양 |

## 요구 사항

- Python 3. Windows의 Python 3.12에서 확인했습니다.
- Python 패키지 `pyyaml`, `pillow`, `playwright`.
- PNG 출력용 브라우저. 렌더러는 Microsoft Edge, Google Chrome, Playwright Chromium 순서로 찾습니다.
- 한글 글꼴. 렌더러는 Windows의 맑은 고딕, macOS의 Apple SD Gothic Neo, Linux의 Noto Sans CJK KR을 찾습니다.

## 설치

GitHub Copilot은 개인 스킬을 홈 디렉터리의 `~/.copilot/skills`에 저장합니다. 자세한 내용은 [GitHub 문서의 Agent skills](https://docs.github.com/en/copilot/concepts/customizations/agent-skills)에 있습니다. 다음 두 방법 중 하나로 설치합니다.

### GitHub CLI로 설치

GitHub CLI의 `gh skill`은 미리 보기 기능입니다. 명령과 동작은 바뀔 수 있습니다.

```
gh skill install EON-LEE/azure-architecture-diagrams azure-architecture-diagram --agent github-copilot --scope user
```

### 직접 복사

1. 저장소를 복제합니다.

   ```
   git clone https://github.com/EON-LEE/azure-architecture-diagrams.git
   ```

2. 스킬 폴더를 개인 스킬 폴더에 복사합니다.

   Windows PowerShell:

   ```powershell
   New-Item -ItemType Directory -Force "$HOME\.copilot\skills" | Out-Null
   Copy-Item -Recurse azure-architecture-diagrams\skills\azure-architecture-diagram "$HOME\.copilot\skills\"
   ```

   macOS, Linux:

   ```bash
   mkdir -p ~/.copilot/skills
   cp -R azure-architecture-diagrams/skills/azure-architecture-diagram ~/.copilot/skills/
   ```

한 저장소에서만 쓰려면 그 저장소의 `.github/skills` 폴더에 스킬 폴더를 복사합니다.

## 준비

설치한 스킬 폴더에서 다음 명령을 실행합니다.

1. 패키지를 설치합니다.

   ```
   python -m pip install pyyaml pillow playwright
   ```

2. Edge와 Chrome이 모두 없으면 Playwright Chromium을 설치합니다.

   ```
   python -m playwright install chromium
   ```

3. 공식 아이콘을 내려받습니다. 아이콘은 사용자 캐시에 저장됩니다.

   ```
   python scripts/icon_tool.py fetch
   ```

Windows PowerShell에서 한글 메시지가 깨지면 명령 전에 `$env:PYTHONIOENCODING='utf-8'`을 실행합니다.

## 사용

스킬을 설치한 뒤 에이전트에게 Azure 아키텍처 다이어그램을 요청합니다. 예를 들면 다음과 같습니다.

- "Azure 아키텍처 그려줘. Front Door, App Service, SQL Database로 구성한 웹 앱이야."
- "Draw a reference architecture for a zone-redundant App Service web app."

스킬이 안내하는 주요 단계는 다음과 같습니다. 전체 절차는 [`SKILL.md`](skills/azure-architecture-diagram/SKILL.md)에 있습니다.

1. Microsoft Learn에서 가장 가까운 참조 아키텍처를 찾아 서비스, 흐름, 범위 경계를 확인합니다.
2. 공식 아이콘 키를 찾아 YAML 사양을 작성합니다.
3. `--strict` 옵션으로 렌더링하고 오류와 경고가 없어질 때까지 사양을 고칩니다.
4. PNG를 직접 열어 글자 잘림, 겹침, 배지 위치, 흐름 방향을 확인합니다.

### 렌더러 직접 실행

스킬 폴더에서 다음 명령을 실행하면 예시 사양을 렌더링합니다.

```
python scripts/render.py examples/baseline-web-app.yaml --out out/baseline-web-app --strict
```

| 결과물 | 내용 |
| --- | --- |
| `{name}.drawio` | 편집할 수 있는 원본 |
| `{name}.png`, `{name}.svg` | 문서와 발표에 쓰는 이미지 |
| `{name}-validation.json` | 페이지별 검증 결과 |
| `icon-provenance.json` | 사용한 아이콘의 출처 URL, 이용 조건, SHA-256 해시, 사용 위치 |

| 종료 코드 | 의미 |
| --- | --- |
| 0 | 오류가 없습니다. `--strict`에서는 경고도 없습니다. |
| 1 | 레이아웃 오류가 있습니다. `--strict`에서는 경고도 포함합니다. |
| 2 | 사양 오류나 아이콘 오류가 있습니다. |

## 라이선스와 아이콘 이용 조건

- 이 저장소의 코드와 문서는 [MIT 라이선스](LICENSE)를 따릅니다.
- 이 저장소에는 아이콘 파일이 없습니다. `icon_tool.py fetch`가 Microsoft 공식 배포처에서 아이콘을 내려받습니다.
- 이 저장소의 MIT 라이선스는 아이콘에 적용되지 않습니다. 아이콘에는 팩마다 정한 이용 조건이 적용됩니다. 예를 들어 Microsoft는 Azure 아이콘을 아키텍처 다이어그램, 교육 자료, 문서에 쓰도록 허용합니다.
- 렌더러가 만든 PNG, SVG, draw.io 파일에는 아이콘이 들어 있습니다. 결과물을 배포하기 전에 [아이콘 카탈로그의 이용 조건](skills/azure-architecture-diagram/references/icon-catalog.md#이용-조건)을 확인합니다.
