# 사양 형식

다이어그램 사양은 YAML 매핑 하나다. 이 문서의 기본값은 `reference` 스타일 기준이다. 시작할 때는 `examples/baseline-web-app.yaml`을 복사해서 고친다.

그룹, 노드, 엣지, 배지에 알 수 없는 키가 있으면 렌더러가 사양 오류(종료 코드 2)를 낸다. 오류 메시지는 허용되는 키 목록을 보여 준다.

## 최상위 키

| 키 | 설명 |
| --- | --- |
| `name` | 결과 파일 이름이다. 없으면 사양 파일 이름을 쓴다. |
| `style` | `reference`(기본값) 또는 `card`다. |
| `canvas` | `{width, height}`다. 기본값은 1920×1080이다. |
| `theme` | 스타일 기본값을 덮어쓴다. [테마](#테마)를 참고한다. |
| `title`, `description` | 헤더의 제목과 설명이다. |
| `grid` | 좌표에 이름을 붙인다. |
| `groups` | 구독, 가상 네트워크, 서브넷 같은 범위 경계다. |
| `nodes` | 서비스 아이콘이다. |
| `edges` | 흐름 화살표다. |
| `badges` | 흐름 번호다. |
| `panel` | 오른쪽 단계 설명과 범례다. |
| `bands` | ID, 모니터링 같은 공통 서비스 띠다. |
| `texts` | 자유 텍스트다. |
| `footer` | 아래쪽 출처와 표제다. |
| `pages` | 한 사양에서 여러 페이지를 만든다. |
| `page_name` | draw.io 페이지 탭 이름이다. 없으면 `title`을 쓰고, `title`도 없으면 페이지 `id`를 쓴다. |

## ID 규칙

- 노드, 그룹, 밴드, 패널의 ID는 모두 달라야 한다. 중복 ID는 사양 오류다.
- 표현식에서 참조할 요소의 ID는 영문자, 숫자, 밑줄(`_`)로 짓는다. `pe-app.left`는 `pe` 빼기 `app.left`로 해석되어 오류가 난다. 하이픈이 든 ID는 엣지의 `from`과 `to`에는 쓸 수 있다.
- 열 이름(`grid.cols`)은 요소 ID와 겹치지 않게 짓는다. 이름이 같으면 열이 우선한다.

## 좌표와 표현식

모든 좌표는 캔버스 왼쪽 위를 원점으로 하는 픽셀 값이다. 숫자 대신 문자열 표현식을 쓸 수 있다.

| 표현 | 값 |
| --- | --- |
| `W`, `H` | 캔버스 너비와 높이 |
| 행·가이드 이름 | `grid.rows`와 `grid.guides`의 값 |
| `열.left`, `열.right`, `열.cx`, `열.w` | `grid.cols` 열의 왼쪽, 오른쪽, 가운데, 너비 |
| `id.left`, `id.right`, `id.top`, `id.bottom` | 요소 상자의 각 변 |
| `id.cx`, `id.cy`, `id.w`, `id.h` | 요소 상자의 가운데와 크기 |
| `id.foot` | 아이콘 노드의 레이블까지 포함한 아래쪽 끝 |

- 연산자는 `+ - * /`, 괄호, 음수 부호를 쓸 수 있다.
- 아이콘 노드의 상자는 아이콘(또는 아이콘 묶음)만 포함한다. 레이블까지 포함한 아래쪽 끝이 필요하면 `foot`을 쓴다.
- 밴드 항목은 표현식에서 참조할 수 없다.
- 순환 참조는 오류다. 너비나 높이가 0 이하인 상자도 오류다.

```yaml
grid:
  cols: {c1: [40, 300], c2: [300, 620]}
  rows: {main: 420, shared: 760}
  guides: {gap: 24}
nodes:
  - {id: app, at: [c2.cx, main], icon: "azure:app services/App-Services", title: Azure App Service}
  - {id: kv, at: [app.cx, "main + 180"], icon: "azure:security/Key-Vaults", title: Azure Key Vault}
```

## 헤더와 푸터

### 헤더

| 키 | 설명 |
| --- | --- |
| `title` | 굵은 40px 제목이다. 최대 2줄이며, 넘치면 22px까지 1px씩 줄인다. |
| `description` | 17px 설명 문단이다. `**굵게**`를 쓸 수 있다. 너비는 글자 80개 분량(1360px)으로 제한한다. |

헤더는 x=40부터 패널 왼쪽 40px 앞까지 차지한다. 패널이 없으면 캔버스 오른쪽 40px 앞까지 차지한다. 제목과 설명 아래에 짙은 가로줄을 그린다.

`card` 스타일은 `kicker`, `title`, `subtitle`, `tag`, `date`를 쓴다.

### 푸터

| 키 | 설명 |
| --- | --- |
| `footer.center` | 다이어그램 영역 아래 가운데의 강조 표제다. |
| `footer.right` | 다이어그램 영역 오른쪽 아래의 회색 문구다. 작성일과 버전을 넣을 때 쓴다. |
| `footer.left` | 왼쪽 아래의 회색 줄이다. 문자열 또는 목록이다. 마지막 줄이 기준선(H − 26)에 놓이고 앞 줄은 위로 쌓인다. 근거 문서와 아이콘 출처를 넣는다. |

`card` 스타일은 `footer.left`와 `footer.right`만 쓴다.

## 그룹

```yaml
groups:
  - {id: sub, label: Azure 구독, sublabel: 워크로드 리소스 그룹, icon: "azure:general/Subscriptions",
     kind: azure, box: [184, 163, 1420, 871]}
  - {id: vnet, parent: sub, label: 가상 네트워크, icon: "azure:networking/Virtual-Networks", kind: vnet,
     fit: [appgw, pe-app]}
```

| 키 | 설명 |
| --- | --- |
| `id` | 필수다. |
| `label`, `sublabel` | 왼쪽 위 레이블과 회색 보조 레이블이다. 보조 레이블은 공간이 40px 넘게 남을 때만 그린다. |
| `icon` | 왼쪽 위 40px 타일 안에 그릴 아이콘 키다. |
| `kind` | 그룹 종류다. 기본값은 `plain`이다. |
| `parent` | 바깥 그룹 ID다. |
| `box` | `[x1, y1, x2, y2]`다. |
| `fit` | 감쌀 노드나 그룹의 ID 목록이다. 아이콘 노드는 레이블까지 감싼다. |
| `pad` | `fit`의 여백이다. `[왼쪽, 위, 오른쪽, 아래]` 또는 숫자 하나다. 기본값은 `[28, 64, 28, 24]`다. |
| `left`, `top`, `right`, `bottom` | `box`나 `fit`으로 정한 변 하나를 덮어쓴다. |
| `fill`, `stroke`, `dash`, `label_color` | 이 그룹만 채움 색, 선 색, 점선 여부, 레이블 색을 바꾼다. |
| `label_align` | `left` 또는 `center`다. `center`이면 아이콘 타일과 보조 레이블을 그리지 않는다. |
| `stand_in` | 그룹 아이콘이 대체 아이콘이면 `true`로 지정한다. |

`box`와 `fit` 중 하나는 반드시 있어야 한다. 위쪽 여백 64px은 레이블 타일 자리다.

### 그룹 종류

| `kind` | 용도 | 모양 |
| --- | --- | --- |
| `azure` | 구독, 리소스 그룹 같은 최상위 Azure 경계 | 남색 실선, 옅은 채움 |
| `region` | Azure 지역 | 청록 점선 |
| `vnet` | 가상 네트워크 | 보라 실선 |
| `subnet` | 서브넷 | 녹색 실선 |
| `fabric` | Microsoft Fabric 작업 영역이나 용량 | 짙은 청록 실선, 옅은 채움 |
| `foundry` | Microsoft Foundry 리소스나 프로젝트 | 보라 실선, 옅은 채움 |
| `m365` | Microsoft 365 테넌트 | 파랑 실선, 옅은 채움 |
| `powerplatform` | Power Platform 환경 | 자주 실선, 옅은 채움 |
| `onprem` | 온-프레미스 데이터 센터 | 회색 실선, 옅은 채움 |
| `external` | 외부 시스템, 파트너 | 회색 점선 |
| `users` | 사용자나 클라이언트 묶음 | 회색 실선 |
| `plain` | 기타 묶음 | 회색 실선, 흰색 채움 |
| `workflow` | 레이블을 가운데 정렬하는 묶음이다. `reference` 스타일에만 있다. | 회색 실선, 흰색 채움 |
| `band` | 밴드 테두리다. | 회색 점선 |

## 노드

기본 노드 종류는 `reference` 스타일에서 `icon`이다. 아이콘 노드는 아이콘과 레이블로 구성된다.

```yaml
nodes:
  - {id: appgw, parent: agw-subnet, at: [363, 496], label_w: 200, title: Application Gateway,
     icons: ["azure:networking/Application-Gateways", "azure:networking/Web-Application-Firewall-Policies(WAF)"],
     detail: 웹 애플리케이션 방화벽(WAF)}
```

| 키 | 설명 |
| --- | --- |
| `id` | 필수다. |
| `parent` | 속한 그룹 ID다. 노드와 레이블은 그룹 안에 있어야 한다. |
| `at` | 아이콘 중심 `[cx, cy]`다. |
| `col`, `row` | `at` 대신 쓴다. 열 가운데와 행 y에 놓는다. |
| `icon` | 아이콘 키 하나다. |
| `icons` | 아이콘 키 목록이다. 아이콘을 12px 간격으로 나란히 그린다. |
| `frame` | `dashed` 또는 `solid`다. 아이콘 둘레에 테두리를 그린다. 선 색은 `stroke`(기본값 `gray`)다. |
| `title` | 서비스 이름이다. 목록은 ` · `로 잇고, `\n`은 줄을 나눈다. |
| `detail` | 회색 보조 설명이다. 역할이나 SKU처럼 짧게 쓴다. |
| `label_pos` | `below`(기본값), `above`, `right`, `left`다. |
| `label_w` | 레이블 최대 너비다. 기본값은 170px이다. |
| `icon_size` | 아이콘 크기다. 기본값은 64px이다. |
| `title_size`, `detail_size` | 글자 크기다. 기본값은 16px과 13.5px이다. |
| `title_bold` | 제목을 굵게 쓴다. 기본값은 `false`다. |
| `stand_in` | 대체 아이콘이면 `true`로 지정한다. |

- 제목이 3줄을 넘으면 렌더러가 글자를 0.5px씩 줄인다. 최소 크기는 `theme.min_font`(기본값 10px)다.
- 엣지는 아이콘 노드의 연결 상자 테두리에서 시작하고 끝난다. 연결 상자는 아이콘 상자를 레이블 쪽으로 레이블 끝까지 늘린 영역이다. 예를 들어 레이블이 아래에 있으면 가로 범위는 아이콘 너비이고, 세로 범위는 아이콘 위쪽부터 레이블 아래 4px까지다. 따라서 레이블 쪽으로 나가는 선은 레이블 바깥에서 시작한다.

### 다른 노드 종류

`type`을 `card`, `glyph`, `tile` 중 하나로 지정하면 상자형 노드가 된다. 상자형 노드는 위치 키가 다르다.

| 키 | 설명 |
| --- | --- |
| `x` 또는 `col` | 가로 범위다. `col`에는 `w`와 `align`(`left`, `center`, `right`)을 함께 쓸 수 있다. |
| `y` 또는 `row` | 세로 범위다. `row`에는 높이 `h`를 함께 쓸 수 있다. |
| `fill`, `stroke`, `dash` | `card`의 채움 색, 선 색, 점선 여부다. |
| `chips` | `card` 아래쪽 작은 칩 목록이다. |
| `border` | `tile`의 테두리 여부다. |
| `icon` | 아이콘 키 하나다. 생략하면 아이콘 없이 그린다. 상자형 노드는 `icons`를 읽지 않는다. |
| `stand_in` | 대체 아이콘이면 `true`로 지정한다. |

## 엣지

```yaml
edges:
  - {id: e1, from: users, to: appgw, kind: request}
  - {id: e3, from: dns, to: vnet, kind: control, x: 330, label: VNet 연결}
  - {id: e6a, from: nic, to: pe-sql, kind: action, via: [[1120, 384], [945, 384]]}
```

| 키 | 설명 |
| --- | --- |
| `id` | 기본값은 `from-to`다. 배지가 엣지를 참조하려면 지정한다. |
| `from`, `to` | 노드, 그룹, 밴드, 밴드 항목, 패널의 ID다. |
| `kind` | 흐름 종류다. 기본값은 `request`다. |
| `label` | 선 레이블이다. |
| `label_at`, `label_anchor` | 레이블 위치 `[x, y]`와 정렬(`start`, `middle`, `end`)이다. 정렬 기본값은 `middle`이다. |
| `arrow` | `end`(기본값), `start`, `both`, `none`이다. |
| `y`, `x`, `via`, `points` | 경로 지정 방법이다. 하나만 쓴다. |
| `bridge` | 의도한 교차이면 `true`로 지정한다. 교차 경고가 정보로 바뀐다. |
| `color`, `dash` | 이 엣지만 선 색과 파선 패턴을 바꾼다. |

### 흐름 종류

| `kind` | 기본 범례 문구 | `reference` 스타일의 선 | `card` 스타일의 선 |
| --- | --- | --- | --- |
| `request` | 요청 · 질의 | 검은 실선 | 파란 실선 |
| `data` | 데이터 수집 · 적재 | 검은 실선 | 청록 긴 파선 `16 6` |
| `action` | 업무 액션 · 도구 호출 | 검은 파선 `7 4` | 보라 파선 `8 4` |
| `egress` | 인터넷 송신 | 검은 파선 `7 4` | 빨간 2점 쇄선 `10 4 2 4 2 4` |
| `feedback` | 피드백 · 결과 반영 | 검은 1점 쇄선 `10 4 2 4` | 주황 1점 쇄선 `10 4 2 4` |
| `control` | 운영 · 인증 | 회색 점선 `2 3` | 회색 점선 `3 4` |

- 범례는 색과 선 모양이 모두 같은 종류를 한 줄로 합친다. 예를 들어 `reference` 스타일의 `request`와 `data`는 "요청 · 질의 / 데이터 수집 · 적재"가 된다.
- `card` 스타일은 종류마다 선 모양이 달라서 색을 구분하지 못해도 흐름을 구분할 수 있다.
- 범례 문구는 `theme.edge_kinds.<kind>.label`로 바꾼다.
- 두 종류를 구분해서 보여야 하면 `theme.edge_kinds.<kind>.dash`를 바꾼다(필수). `color`만 바꾸면 두 종류가 색으로만 구분되어 `design-color-only` 경고가 난다.

### 경로 지정

| 방법 | 동작 | 조건 |
| --- | --- | --- |
| 자동(경로 키 없음) | 두 아이콘이 겹치는 구간의 가운데로 직선을 긋는다. | 두 아이콘 상자가 한 축에서 2px 넘게 겹치고, 다른 축에서는 겹치지 않아야 한다. 조건을 만족하지 않으면 `boxes are not aligned` 오류가 난다. |
| `y: 값` | 가로 직선을 긋는다. | 값이 두 연결 상자의 세로 범위 안에 있어야 한다. 두 상자가 가로로 겹치면 `use 'via'` 오류가 난다. |
| `x: 값` | 세로 직선을 긋는다. | 값이 두 연결 상자의 가로 범위 안에 있어야 한다. 두 상자가 세로로 겹치면 `use 'via'` 오류가 난다. |
| `via: [[x, y], ...]` | 꺾임점을 지나는 직교 경로를 긋는다. 렌더러가 상자 테두리의 시작점과 끝점을 계산한다. | 첫 점은 출발 상자와 x나 y가 같고 상자 밖에 있어야 한다. 마지막 점은 도착 상자와 같은 조건을 만족해야 한다. |
| `points: [[x, y], ...]` | 전체 경로를 그대로 그린다. | 끝점을 직접 계산해야 한다. 마지막 구간은 14px 이상으로 한다. |

- 한 노드에서 여러 대상으로 갈 때는 같은 꺾임점으로 시작하는 `via`를 써서 공통 줄기를 공유한다. 예시 사양의 `e6`, `e6a`, `e6b`가 이 방식이다.
- 여러 노드에서 한 대상으로 모이는 실선도 끝 구간을 공유할 수 있다. 파선은 무늬가 어긋나므로 끝 구간을 공유하지 않는다.
- 엣지가 교차하면 나중에 정의한 엣지가 앞의 엣지를 건너뛰는 틈을 그린다.

### 선 레이블

`label_at`이 없으면 레이블은 가장 긴 구간의 가운데에 놓인다. 가로 구간이면 선 8px 위, 세로 구간이면 선 8px 오른쪽이다. 레이블은 뒤 배경색으로 테두리를 둘러서 선과 겹쳐도 읽힌다.

레이블 글자는 선 색으로 그린다. 선 색과 레이블 배경의 대비가 [색 대비](style-guide.md#검증하는-규칙)의 글자 기준보다 낮으면 렌더러가 `theme.colors.muted`로 바꾼다. 그래도 낮으면 `theme.colors.ink`로 바꾼다.

## 배지

배지는 흐름 번호다. 패널의 단계 번호와 1:1로 맞춘다.

```yaml
badges:
  - {n: 1, edge: e1}
  - {n: 2, edge: e2, pos: 0.75}
  - {n: 3, edge: e3, side: left}
```

| 키 | 설명 |
| --- | --- |
| `n` | 번호다. 필수다. |
| `edge` | 이 엣지 옆에 놓는다. |
| `at` | 고정 위치 `[x, y]`다. `edge`와 함께 쓸 수 없다. |
| `pos` | `start`(기본값), `mid`, `end` 또는 0~1 비율이다. |
| `side` | `auto`(기본값), `above`, `below`, `left`, `right`다. |
| `offset` | 선에서 배지 중심까지 거리다. 기본값은 반지름 + 5px(17px)이다. |
| `kind` | `card` 스타일에서 배지 색을 정한다. `reference` 스타일의 배지는 모두 검은색이다. |

- `pos`, `side`, `offset`은 `edge`와 함께 쓸 때만 유효하다.
- 렌더러는 `pos`에서 시작해 선을 따라 12px 단위로 앞뒤를 탐색한다. 글자, 아이콘, 다른 배지, 선, 그룹 테두리와 겹치지 않는 첫 자리에 배지를 놓는다. `side: auto`는 가로 구간에서 위와 아래, 세로 구간에서 오른쪽과 왼쪽을 시험한다.
- 빈자리가 없으면 `badge-placement` 경고가 난다. `pos`, `side`, `offset`을 바꾸거나 `at`으로 고정한다.

## 패널

패널은 오른쪽 단계 설명 열이다. 단계는 위에서부터, 범례는 패널 아래쪽에 놓인다.

| 키 | 설명 |
| --- | --- |
| `id` | 기본값은 `panel`이다. |
| `box` | `[x1, y1, x2, y2]`다. 필수다. 1920×1080에서는 `[1460, 0, 1920, 1080]`을 쓴다. |
| `title`, `note` | 패널 제목과 보조 문장이다. 선택 사항이다. |
| `steps` | 단계 목록이다. |
| `legend` | `auto`(기본값), 흐름 종류 목록, `none`이다. `auto`는 사용한 흐름 종류만 보여 준다. |
| `legend_title` | 범례 제목이다. 기본값은 "범례"다. |
| `legend_notes` | 범례 아래 주석 목록이다. 약어를 정의할 때 쓴다. |

단계 항목의 키는 다음과 같다.

| 키 | 설명 |
| --- | --- |
| `text` | 단계 설명이다. `**굵게**`로 서비스 이름을 강조한다. |
| `title` | 문장 앞에 굵게 붙는 짧은 제목이다. `reference` 스타일에서는 선택 사항이고, `card` 스타일에서는 필수다. |
| `kind` | `card` 스타일에서 배지 색을 정한다. |
| `n` | 번호다. 기본값은 단계 순서다. |

- 패널에 남는 공간이 있으면 렌더러가 글자를 최대 1.12배까지 키운다. 그래도 남으면 줄 간격을 글자 크기의 1.6배까지 넓힌다. 단계 사이 간격은 14~48px이다.
- 단계와 범례가 겹치면 `panel-too-short` 오류가 난다. 문장을 줄이거나 패널을 키운다.
- 엣지는 패널을 지나갈 수 없다.

## 밴드

밴드는 ID, 모니터링, 거버넌스처럼 워크로드 전체가 쓰는 공통 서비스를 한 줄로 모은다.

```yaml
bands:
  - id: shared
    box: [40, 915, 1420, 999]
    label: 공통 서비스
    note: ID · 모니터링
    items:
      - {icon: "entra:Microsoft Entra ID", title: Microsoft Entra ID, detail: ID · 액세스 제어}
      - {id: appinsights, icon: "azure:monitor/Application-Insights", title: Application Insights,
         detail: 앱 원격 분석}
```

| 키 | 설명 |
| --- | --- |
| `id`, `box` | 필수다. |
| `label`, `note` | 왼쪽 위 제목과, 제목 오른쪽에 붙는 회색 보조 문구다. 보조 문구는 남은 너비가 60px을 넘을 때만 그린다. |
| `icon_size` | 항목 아이콘 크기다. 기본값은 아이콘 크기의 0.625배(40px)다. |
| `items` | 항목 목록이다. 항목은 `id`, `icon` 또는 `icons`, `title`, `detail`, `stand_in`을 쓴다. |

- 항목은 밴드 너비에 고르게 배치되고 레이블은 아이콘 오른쪽에 놓인다.
- 항목 ID의 기본값은 `<밴드 id>-<순번>`이다. 순번은 1부터 시작한다.
- 엣지는 밴드나 밴드 항목에서 끝날 수 있다. 다른 엣지는 밴드를 지나갈 수 없다.
- `card` 스타일은 `label_width`(기본값 190px)로 레이블 열의 너비를 정한다.

## 자유 텍스트

```yaml
texts:
  - {at: [60, 1040], text: "* 선택 구성 요소", size: 13, color: muted}
```

| 키 | 설명 |
| --- | --- |
| `at` | 글자 기준선의 위치 `[x, y]`다. x는 `anchor`에 따라 문구의 시작점, 가운데, 끝점이 된다. |
| `text` | 한 줄 문구다. |
| `size` | 기본값은 14px이다. |
| `color` | 테마 색 이름(`ink`, `muted`, `accent` 등)이나 색 코드다. 기본값은 `muted`다. |
| `bold` | 굵게 쓴다. |
| `width` | 최대 너비다. 넘치면 `theme.min_font`까지 글자를 줄인다. |
| `anchor` | `start`(기본값), `middle`, `end`다. |

## 페이지

`pages`의 각 항목은 최상위 키 위에 병합된다. 매핑은 키별로 합치고 목록은 통째로 바꾼다. 각 항목에는 `id`가 필요하다.

공통 설정(`style`, `canvas`, `theme`, `footer`)은 최상위에 두고, 페이지마다 다른 목록(`groups`, `nodes`, `edges`, `badges`)과 `panel`은 각 페이지에 둔다. 목록은 병합되지 않으므로 한 페이지의 엣지와 배지는 그 페이지의 노드만 참조해야 한다.

```yaml
name: platform
style: reference
canvas: {width: 1920, height: 1080}
footer: {left: ["근거: Microsoft Learn Azure 아키텍처 센터"]}
pages:
  - id: context
    title: 시스템 컨텍스트
    # groups, nodes, edges, badges, panel
  - id: network
    title: 네트워크 경계
    # groups, nodes, edges, badges, panel
```

여러 페이지 사양은 페이지마다 `{name}-{id}.png`와 `{name}-{id}.svg`를 만든다. `{name}.drawio`에는 모든 페이지가 들어간다.

## 테마

`theme`은 스타일 기본값 위에 깊은 병합된다. 자주 쓰는 키는 다음과 같다.

| 키 | 설명 |
| --- | --- |
| `scale` | 모든 크기를 곱하는 배율이다. 0.5~3 사이 숫자다. 넓은 캔버스에서 올린다. |
| `edge_kinds.<kind>.label` | 범례 문구다. |
| `edge_kinds.<kind>.color`, `dash` | 흐름 종류의 선 색과 파선 패턴이다. 종류마다 `dash`를 다르게 해야 범례가 색에만 기대지 않는다. |
| `group_kinds.<kind>.stroke`, `fill`, `label` | 그룹 종류의 테두리 색, 채움 색, 레이블 색이다. |
| `badge.color` | 배지 색이다. 값이 비어 있으면 흐름 종류의 색을 쓴다. `card` 스타일의 기본값은 비어 있다. |
| `colors.ink`, `colors.muted` | 기본 글자 색과 보조 글자 색이다. 선 색으로 읽기 어려운 선 레이블에도 쓴다. |
| `colors.accent` | 푸터 표제 색이다. |
| `font_family`, `drawio_font` | SVG와 draw.io의 글꼴이다. |
| `min_font` | 자동 축소의 최소 글자 크기다. 기본값은 10px이다. |
| `icon.size`, `icon.label_w` | 아이콘 노드의 기본 크기와 레이블 너비다. |

- `scale`은 `icon`, `group`, `edge`, `badge`, `panel`, `header`, `footer`, `card`, `glyph`, `tile` 구역의 크기와 `min_font`를 곱한다. 줄 수와 비율 값은 곱하지 않는다.
- 노드에 직접 지정한 `icon_size`, `title_size` 같은 값에는 `scale`이 적용되지 않는다.

## 최소 예시

다음 사양은 노드가 한 행뿐이다. 그래서 캔버스 높이를 560px로 줄였다. 같은 내용을 1600×900 캔버스에 그리면 그룹 아래가 비어서 `design-sparse` 경고가 나온다.

```yaml
name: minimal-web
canvas: {width: 1600, height: 560}
title: 웹 애플리케이션 기본 구성
description: 사용자가 **Azure Front Door**를 거쳐 **App Service**에 접속하고, App Service가 **SQL Database**에 데이터를 저장합니다.
grid:
  rows: {main: 330}
groups:
  - {id: sub, label: Azure 구독, icon: "azure:general/Subscriptions", kind: azure, fit: [fd, app, sql]}
nodes:
  - {id: users, at: [110, main], icon: "azure:identity/Users", title: 사용자}
  - {id: fd, parent: sub, at: [400, main], icon: "azure:networking/Front-Door-and-CDN-Profiles",
     title: Azure Front Door}
  - {id: app, parent: sub, at: [680, main], icon: "azure:app services/App-Services", title: Azure App Service}
  - {id: sql, parent: sub, at: [960, main], icon: "azure:databases/SQL-Database", title: Azure SQL Database}
edges:
  - {id: e1, from: users, to: fd}
  - {id: e2, from: fd, to: app}
  - {id: e3, from: app, to: sql, kind: data}
badges:
  - {n: 1, edge: e1}
  - {n: 2, edge: e2}
  - {n: 3, edge: e3}
panel:
  box: [1180, 0, 1600, 560]
  steps:
    - {text: 사용자가 HTTPS로 **Azure Front Door**에 요청을 보냅니다.}
    - {text: Front Door가 원본인 **App Service**로 요청을 전달합니다.}
    - {text: App Service가 **SQL Database**에서 데이터를 읽고 씁니다.}
footer:
  left: ["근거: Microsoft Learn Azure 아키텍처 센터"]
```
