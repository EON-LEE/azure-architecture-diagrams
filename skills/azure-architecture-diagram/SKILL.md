---
name: azure-architecture-diagram
description: Microsoft 공식 아이콘과 Microsoft Learn의 다이어그램 지침을 따라 실제 Azure 서비스 아키텍처 다이어그램을 그린다. YAML 사양을 작성하고 렌더러로 draw.io, SVG, PNG를 만든 뒤 레이아웃·디자인 검증과 PNG 확인을 통과시킨다. "Azure 아키텍처 그려줘", "아키텍처 다이어그램", "구성도", "서비스 아키텍처 그림", "draw.io로 그려줘", "Azure architecture diagram", "draw a reference architecture" 요청에 적용한다.
license: MIT
metadata:
  version: "1.0.0"
---

# Azure 아키텍처 다이어그램

이 스킬은 Microsoft 공식 아이콘으로 실제 Azure 서비스 아키텍처를 그린다. 결과물은 Microsoft Learn 참조 아키텍처 수준이어야 한다. 그림에는 근거 문서와 일치하는 서비스, 범위 경계, 흐름, 번호 단계 설명이 있어야 한다.

다이어그램은 YAML 사양으로 작성한다. `scripts/render.py`가 사양을 읽어 그림을 만들고 레이아웃과 디자인을 검증한다. 이 문서에서 `$SKILL`은 이 SKILL.md가 있는 폴더를 뜻한다.

## 결과물

| 파일 | 내용 |
| --- | --- |
| `{name}.drawio` | 편집할 수 있는 원본이다. 여러 페이지 사양은 모든 페이지를 한 파일에 넣는다. |
| `{name}.png`, `{name}.svg` | 문서와 발표에 쓰는 이미지다. 여러 페이지 사양은 페이지마다 `{name}-{page id}.png`와 `.svg`를 만든다. |
| `{name}-validation.json` | 페이지별 검증 결과다. 항목마다 `level`, `code`, `message`, `ids`가 있다. |
| `icon-provenance.json` | 사용한 아이콘의 출처 URL, 이용 조건, SHA-256 해시, 사용 위치다. |

- `name`은 사양의 `name` 값이다. 값이 없으면 사양 파일 이름을 쓴다.
- SVG와 draw.io 파일은 아이콘을 내장한다. 아이콘 캐시가 없는 컴퓨터에서도 열 수 있다.
- PNG 배율의 기본값은 1.25다. 1920×1080 캔버스는 2400×1350 이미지가 된다.

## 준비

1. 패키지를 설치한다.

   ```
   python -m pip install pyyaml pillow playwright
   ```

2. PNG 출력용 브라우저를 확인한다. 렌더러는 Microsoft Edge, Google Chrome, Playwright Chromium 순서로 찾는다. Edge와 Chrome이 모두 없으면 다음 명령을 실행한다.

   ```
   python -m playwright install chromium
   ```

3. 공식 아이콘을 내려받는다. 아이콘은 사용자 캐시에 저장된다.

   ```
   python $SKILL/scripts/icon_tool.py fetch
   ```

4. 한글 글꼴을 확인한다. 렌더러는 Windows의 맑은 고딕, macOS의 Apple SD Gothic Neo, Linux의 Noto Sans CJK KR을 찾는다. 다른 글꼴을 쓰려면 `AZDIAGRAM_FONT`와 `AZDIAGRAM_FONT_BOLD`에 `.ttf` 또는 `.ttc` 파일 경로를 지정한다. 이때 `theme.font_family`도 같은 글꼴로 지정한다.

Windows PowerShell에서 한글 메시지가 깨지면 명령 전에 `$env:PYTHONIOENCODING='utf-8'`을 실행한다.

## 작업 절차

1. **범위를 정한다.** 독자, 목적, 다이어그램 종류를 확인한다. 한 그림에는 한 수준만 그린다. 워크로드 구성, 네트워크 경계, 데이터 흐름처럼 수준이 다르면 `pages`로 나눈다.
2. **근거를 확인한다.** Microsoft Learn에서 가장 가까운 참조 아키텍처를 찾는다. 서비스 이름, 흐름 순서, 범위 경계, 프라이빗 엔드포인트와 관리 ID 같은 기준 구성을 확인한다. 출처 목록은 `references/learn-sources.md`에 있다. 확인하지 못한 구성 요소는 그리지 않거나 사용자에게 확인한다.
3. **아이콘을 고른다.** `icon_tool.py search`로 아이콘 키를 찾는다. 공식 아이콘이 없는 서비스에만 대체 아이콘을 쓰고 `stand_in: true`를 지정한다. 자세한 내용은 `references/icon-catalog.md`에 있다.
4. **사양을 작성한다.** `$SKILL/examples/baseline-web-app.yaml`을 작업 폴더로 복사해서 시작한다. 사양 파일은 스킬 폴더가 아니라 워크로드 저장소나 작업 폴더에 둔다. 키 설명은 `references/spec-format.md`에 있다.
5. **렌더링한다.**

   ```
   python $SKILL/scripts/render.py diagram.yaml --out out --strict
   ```

6. **검증 결과를 고친다.** 종료 코드가 0이 될 때까지 오류와 경고를 고친다. 코드별 수정 방법은 `references/style-guide.md`에 있다. 정보(`info`) 항목은 의도한 설계인지 확인한다.
7. **PNG를 직접 확인한다.** 이미지 보기 도구로 PNG를 연다. 글자 잘림, 겹침, 빈 공간, 배지 위치, 흐름 방향, 정렬을 확인한다. 검증 통과만으로 완료를 판단하지 않는다.
8. **전달한다.** PNG와 `.drawio` 파일을 전달한다. 근거 문서 URL, 대체 아이콘, 확인하지 못한 가정을 함께 밝힌다.

## 다이어그램 규칙

다음 규칙은 대부분 Microsoft Learn의 다이어그램 지침과 Azure 아이콘 이용 조건에서 가져왔다. 규칙별 출처는 `references/learn-sources.md`에 있다.

- 화살표는 요청을 시작하는 구성 요소에서 의존 대상으로 그린다. 양방향 화살표를 쓰지 않는다. 양방향 통신은 엣지 두 개로 그린다.
- 모든 아이콘, 그룹, 엣지에 의미 있는 레이블을 붙인다. 약어는 범례 주석에서 정의한다.
- 제목, 설명, 범례, 근거 문서를 넣는다. 작성일과 버전이 필요하면 푸터에 넣는다.
- 최신 공식 아이콘과 공식 서비스 이름을 쓴다. 아이콘을 자르거나 뒤집거나 회전하거나 변형하지 않는다.
- 사실과 다르게 단순화하지 않는다. 예를 들어 프라이빗 엔드포인트로 접근하는 PaaS 서비스를 서브넷 안에 그리지 않는다.
- 색만으로 의미를 구분하지 않는다. 구분해야 하는 흐름은 선 모양(`dash`)을 다르게 한다. 범례는 선 모양을 자동으로 보여 준다. 같은 선 모양을 색만 바꿔 쓰면 `design-color-only` 경고가 난다.
- 글자, 선, 테두리, 배지는 배경과 충분히 대비되게 한다. 대비가 WCAG 2.1 기준보다 낮으면 `design-contrast` 경고가 난다. 선 레이블은 렌더러가 읽을 수 있는 색으로 자동으로 바꾼다.
- 한 그림에 모든 것을 넣지 않는다. 컨텍스트, 워크로드, 세부 흐름 순서로 나눈다.
- 범위 경계는 실제 범위대로 중첩한다. 서브넷은 가상 네트워크 안에, 가상 네트워크는 한 지역과 한 구독 안에 그린다. 지역과 구독 중 바깥 경계는 실제 구성에 맞춘다.
- 흐름은 왼쪽에서 오른쪽으로, 위에서 아래로 읽히게 배치한다.
- 그림의 번호 배지와 오른쪽 패널의 단계 설명을 1:1로 맞춘다.
- 사양 파일과 `.drawio` 파일은 워크로드의 다른 자산과 같은 저장소에서 버전을 관리한다.

## 디자인 기준

- 기본 캔버스는 1920×1080이고 기본 스타일은 `reference`다. 더 넓은 캔버스에서는 부품 크기를 하나씩 바꾸지 말고 `theme.scale`을 올린다.
- 화면 영역을 나눈다. 위쪽은 제목과 설명, 왼쪽은 다이어그램, 오른쪽 약 460px은 단계 패널, 아래쪽은 공통 서비스 밴드와 푸터다.
- 같은 행과 열에 있는 아이콘은 중심 좌표를 정확히 맞춘다.
- 한 노드에서 여러 대상으로 가는 엣지는 `via`로 공통 줄기를 공유한다.
- ID, 모니터링, 거버넌스 같은 공통 서비스는 `bands`에 모은다. 원격 분석 엣지는 밴드 항목까지 연결한다.
- 엣지의 꺾임은 3번 이하로 유지한다.
- 그룹 안에 큰 빈 공간을 남기지 않는다. 의미 있는 노드를 배치하거나 그룹을 줄인다.
- 다이어그램 영역 전체에도 큰 빈 공간을 남기지 않는다. 노드가 적으면 캔버스 높이를 줄이거나 배치를 넓힌다.

자세한 기준과 검증 코드별 수정 방법은 `references/style-guide.md`에 있다.

## 명령

### 렌더링

```
python $SKILL/scripts/render.py SPEC.yaml --out DIR [--icons DIR] [--no-png] [--scale 1.25] [--strict] [--debug]
```

| 옵션 | 설명 |
| --- | --- |
| `--out DIR` | 결과물 폴더다. 필수다. |
| `--icons DIR` | 아이콘 캐시 폴더를 지정한다. |
| `--no-png` | PNG를 만들지 않는다. 글자 폭은 브라우저 대신 Pillow로 잰다. |
| `--scale` | PNG 배율이다. 기본값은 1.25다. |
| `--strict` | 경고도 실패로 처리한다. 완성본은 이 옵션으로 확인한다. |
| `--debug` | 사양 오류의 전체 추적 정보를 출력한다. |

| 종료 코드 | 의미 |
| --- | --- |
| 0 | 오류가 없다. `--strict`에서는 경고도 없다. |
| 1 | 레이아웃 오류가 있다. `--strict`에서는 경고도 포함한다. |
| 2 | 사양 오류나 아이콘 오류가 있다. 메시지는 `spec error:`로 시작한다. |

### 아이콘

```
python $SKILL/scripts/icon_tool.py packs
python $SKILL/scripts/icon_tool.py fetch [--packs azure,fabric] [--force]
python $SKILL/scripts/icon_tool.py search "key vault" [--pack azure] [--limit 40]
python $SKILL/scripts/icon_tool.py import PACK PATH
```

캐시 폴더를 바꾸려면 하위 명령 앞에 `--icons DIR`을 넣는다.

## 참고 자료

| 파일 | 내용 |
| --- | --- |
| `references/spec-format.md` | YAML 사양의 모든 키, 좌표 표현식, 엣지 경로 지정 방법 |
| `references/style-guide.md` | 배치 순서, 디자인 기능, 검증 코드별 수정 방법, PNG 점검 목록 |
| `references/icon-catalog.md` | 아이콘 팩, 키 형식, 자주 쓰는 키, 대체 아이콘, 이용 조건 |
| `references/learn-sources.md` | 근거로 쓰는 Microsoft Learn 문서와 각 문서에서 가져온 규칙 |
| `examples/baseline-web-app.yaml` | 영역 중복 App Service 기준 아키텍처의 예시 사양 |

## 금지 사항

- 비공식 사이트나 제3자 아이콘 모음에서 아이콘을 가져오지 않는다.
- 아이콘 파일을 저장소에 커밋하지 않는다. 각 사용자가 `icon_tool.py fetch`로 내려받는다.
- 근거 없이 서비스나 연결을 추가하지 않는다.
- 결과 PNG를 보지 않고 완료라고 보고하지 않는다.
- 사용자가 요청하지 않으면 고객 사양과 결과물을 공개 저장소에 올리지 않는다.
