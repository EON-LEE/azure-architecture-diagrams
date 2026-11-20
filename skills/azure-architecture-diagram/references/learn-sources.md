# Microsoft Learn 근거 문서

이 문서는 스킬의 다이어그램 규칙, 기본 색, 아이콘 팩이 근거로 삼는 문서를 정리한다. 모든 문서는 2026-11-21에 확인했다. 수정일은 그날 각 문서에 표시된 `ms.date` 값이다. 영어 인용문은 원문 그대로 옮겼다. Microsoft Learn은 색 대비 수치를 정하지 않으므로 색 대비 기준은 W3C 문서를 근거로 쓴다.

## 문서 목록

| 번호 | 문서 | 수정일 | 쓰는 곳 |
| --- | --- | --- | --- |
| L1 | [Create architecture design diagrams](https://learn.microsoft.com/azure/well-architected/architect-role/design-diagrams) | 2025-08-13 | [다이어그램 지침](#다이어그램-지침), [관행별 구현](#관행별-구현), [색 대비](#색-대비) |
| L2 | [Azure Well-Architected Framework](https://learn.microsoft.com/azure/well-architected/) | 2026-09-11 | L1이 속한 프레임워크 |
| L3 | [Browse Azure Architectures](https://learn.microsoft.com/azure/architecture/browse/) | 2025-11-05 | [참조 아키텍처](#참조-아키텍처) 검색 |
| L4 | [Baseline Highly Available Zone-Redundant App Services Web Application](https://learn.microsoft.com/azure/architecture/web-apps/app-service/architectures/baseline-zone-redundant) | 2025-12-12 | `examples/baseline-web-app.yaml`, [번호 단계](#번호-단계) |
| L5 | [Baseline Microsoft Foundry Chat Reference Architecture](https://learn.microsoft.com/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-chat) | 2026-06-17 | [참조 아키텍처](#참조-아키텍처), [번호 단계](#번호-단계) |
| L6 | [Hub-Spoke Network Topology in Azure](https://learn.microsoft.com/azure/architecture/networking/architecture/hub-spoke) | 2026-04-10 | [참조 아키텍처](#참조-아키텍처) |
| L7 | [Baseline Architecture for an AKS Cluster](https://learn.microsoft.com/azure/architecture/reference-architectures/containers/aks/baseline-aks) | 2025-12-30 | [참조 아키텍처](#참조-아키텍처), [번호 단계](#번호-단계) |
| L8 | [What is an Azure landing zone?](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/) | 2025-07-24 | [참조 아키텍처](#참조-아키텍처) |
| L9 | [Analytics End-to-End with Microsoft Fabric](https://learn.microsoft.com/azure/architecture/example-scenario/dataplate2e/data-platform-end-to-end) | 2025-10-24 | [참조 아키텍처](#참조-아키텍처) |
| L10 | [Azure Icons](https://learn.microsoft.com/azure/architecture/icons/) | 2026-07-09 | `azure` 팩, [이용 조건](icon-catalog.md#이용-조건) |
| L11 | [Microsoft Fabric product, experience, and item icons](https://learn.microsoft.com/fabric/fundamentals/icons) | 2025-07-03 | `fabric` 팩의 사용 지침 |
| L12 | [Microsoft Power Platform icons](https://learn.microsoft.com/power-platform/guidance/icons) | 2025-12-18 | `powerplatform` 팩 |
| L13 | [Microsoft Entra architecture icons](https://learn.microsoft.com/entra/architecture/architecture-icons) | 2023-08-15 | `entra` 팩 |
| L14 | [Microsoft 365 architecture diagram templates and icons](https://learn.microsoft.com/microsoft-365/solutions/architecture-icons-templates) | 2024-04-30 | `m365` 팩 |
| L15 | [Microsoft Dynamics 365 icons](https://learn.microsoft.com/dynamics365/get-started/icons) | 2026-01-23 | `dynamics365` 팩 |
| L16 | [Azure Data Lake Storage overview](https://learn.microsoft.com/azure/storage/blobs/data-lake-storage-introduction) | 2026-07-02 | [Azure 데이터와 분석](icon-catalog.md#azure-데이터와-분석)의 키 |
| L17 | [Azure Virtual Network FAQ](https://learn.microsoft.com/azure/virtual-network/virtual-networks-faq) | 2026-07-08 | [범위 경계](#범위-경계) |
| L18 | [Plan Azure virtual networks](https://learn.microsoft.com/azure/virtual-network/virtual-network-vnet-plan-design-arm) | 2025-04-17 | [범위 경계](#범위-경계) |

- L14는 보관된 문서다. 링크를 열면 이전 버전 영역(`/previous-versions/`)의 문서로 이동한다. 페이지 메타데이터의 `is_archived`와 `is_retired` 값은 `true`다. 이 스킬은 `m365` 팩을 사람, 문서, 장치 같은 일반 개념 아이콘에만 쓴다.
- `fabric` 팩의 파일은 npm 패키지에서 내려받는다. 패키지 버전과 라이선스는 [아이콘 팩](icon-catalog.md#아이콘-팩)에 있다.

색 대비 기준에는 다음 W3C 문서를 쓴다.

| 번호 | 문서 | 쓰는 곳 |
| --- | --- | --- |
| W1 | [Web Content Accessibility Guidelines (WCAG) 2.1](https://www.w3.org/TR/WCAG21/) | [색 대비](#색-대비) |
| W2 | [CSS Values and Units Module Level 3](https://www.w3.org/TR/css-values-3/#absolute-lengths) | pt를 px로 바꾸는 비율 |

## 다이어그램 지침

L1은 Azure Well-Architected Framework(L2)에 속한 문서다. 이 스킬의 다이어그램 규칙은 대부분 L1에서 가져왔다. L1의 "Diagramming practices" 절은 굵은 글씨로 시작하는 관행 13개를 제시한다. 13개 관행과 이 스킬의 구현은 [관행별 구현](#관행별-구현)에 있다.

### 다이어그램 종류

L1은 다이어그램 종류를 하나씩 설명하고, 목적에 맞는 몇 가지만 그리라고 권한다.

> To visualize your workload, favor a minimal set of purposeful diagrams over creating every possible type. Start broad, progressively narrow, then apply scenario and cross-cutting views.

L1이 설명하는 종류 중 이 스킬이 그리는 종류와 그리지 않는 종류는 다음과 같다.

| L1의 종류 | 이 스킬 |
| --- | --- |
| Context diagram | 그린다. 워크로드 경계, 사용자, 외부 시스템을 그린다. |
| High-level system or container diagram | 그린다. 이 스킬의 기본 용도다. |
| Deployment diagram | 그린다. 지역, 구독, 가상 네트워크, 서브넷을 [그룹](spec-format.md#그룹)으로 그린다. |
| Data-flow diagram (DFD) | 그린다. [흐름 종류](spec-format.md#흐름-종류)와 [배지](spec-format.md#배지)로 데이터의 이동 순서를 그린다. |
| Network connectivity diagram | 그린다. 가상 네트워크, 피어링, 프라이빗 엔드포인트, DNS 연결을 그룹과 엣지로 그린다. |
| Sequence diagram, Entity-relationship diagram (ERD), State diagram, Flowchart and activity diagram | 그리지 않는다. 렌더러에는 생명선, 관계 차수 표기, 상태 전이, 판단 기호가 없다. |

### 점진적 공개

L1은 한 그림에 모든 것을 넣지 말고 단계적으로 보여 주라고 권한다.

> Provide progressive disclosure: a context diagram leads to a container diagram, which leads to a focused component or sequence diagram for a critical use case.

이 스킬은 컨텍스트, 워크로드, 세부 흐름 수준을 [페이지](spec-format.md#페이지)로 나눈다. 시퀀스 다이어그램은 그리지 않는다.

### 외부 시스템

L1의 "Context diagram" 절은 외부 시스템을 다음과 같이 그리라고 한다.

> Rely on generic shapes for external systems rather than product logos, and always include an explicit boundary so readers don't have to infer scope.

- 필수: 외부 시스템에 제품 로고를 쓰지 않는다. `icon`이 없는 `card` 노드나 M365 팩의 일반 기호로 그린다. 자세한 규칙은 [대체 아이콘](icon-catalog.md#대체-아이콘)에 있다.
- 권장: 외부 시스템을 `external` [그룹](spec-format.md#그룹-종류)에 넣어 워크로드와의 경계를 보인다.

### 사양 기반 표기

L1은 Business Process Model and Notation, C4 model, Decision Model and Notation, Unified Modeling Language (UML) 같은 사양 기반 표기를 소개한다. 표기를 채택할지는 워크로드 팀이 정한다.

> Adopting one is a workload team decision; do so only if it adds required shared vocabulary to reduce ambiguity.

L1은 검증된 관례를 골라 빌려 쓰면 다이어그램 묶음의 명확성과 일관성을 높일 수 있다고 설명한다("selectively borrowing proven conventions (layering, cardinality notation, event labeling, legend patterns) can raise clarity and consistency across your diagram set"). 이 스킬은 특정 표기를 강제하지 않는다. 계층 나누기와 범례 패턴만 빌려 쓴다.

## 관행별 구현

다음 표는 L1의 13개 관행과 이 스킬의 구현을 대응시킨다. 자동 검사 열의 코드는 [검증 코드](style-guide.md#검증-코드)에 있다. 자동 검사가 없는 관행은 [PNG 점검 목록](style-guide.md#png-점검-목록)으로 확인한다.

| L1 관행 | 이 스킬의 구현 | 자동 검사 |
| --- | --- | --- |
| Use standard notations | 공식 아이콘, 범위 경계 상자, 번호 배지와 단계 설명, 범례를 쓴다. | 없음 |
| Avoid ambiguous lines | 흐름 종류마다 색과 선 모양을 하나로 정한다(`theme.edge_kinds`). 엣지는 직각으로 꺾는다. 엣지가 교차하면 나중에 정의한 엣지에 틈을 만든다. | `edge-diagonal`, `edge-overlap`, `edge-crossing`, `design-bends` |
| Use directional arrows | `arrow`의 기본값은 `end`다. 양방향 통신은 엣지 두 개로 그린다. | `edge-short-tail` |
| Avoid bidirectional arrows | `arrow: both`를 쓰지 않는다. | 없음. PNG 점검 목록 2번 |
| Label everything clearly | 노드의 `title`과 `detail`, 그룹의 `label`, 엣지의 `label`을 쓴다. 약어는 패널의 `legend_notes`에서 정의한다. | `text-overlap`, `label-overlap`, `text-overflow` |
| Maintain consistency | 흐름 종류(`theme.edge_kinds`), 그룹 종류(`theme.group_kinds`), 크기(`theme.scale`)를 테마에서 한 번 정한다. | `design-scale`, `design-align` |
| Be accurate | 프라이빗 엔드포인트로 접근하는 PaaS 서비스를 서브넷 밖에 그린다. 범위 경계는 [범위 경계](#범위-경계)의 규칙을 따른다. | 없음. PNG 점검 목록 7번 |
| Include metadata | 헤더에 `title`과 `description`을 쓴다. 작성일, 작성자, 버전은 `footer.right`에 쓰고, 근거 문서와 아이콘 출처는 `footer.left`에 쓴다. | 없음. PNG 점검 목록 9번 |
| Use official icons and service names | 6개 공식 팩의 아이콘만 쓴다. 팩에 없는 키는 사양 오류다(종료 코드 2). 아이콘 색을 바꾸는 기능은 없고, 아이콘은 비율을 유지해 그린다. 사용한 아이콘은 `icon-provenance.json`에 기록한다. | 사양 오류 `not found. Similar:` |
| Provide a legend | 패널의 `legend: auto`는 사용한 흐름 종류의 색과 선 모양을 보여 준다. | 없음. PNG 점검 목록 6번 |
| Design for accessibility | 흐름 종류마다 선 모양을 다르게 한다. 기본 색은 [색 대비](#색-대비)의 기준을 만족한다. 선 레이블 색은 렌더러가 고른다. | `design-contrast`, `design-color-only` |
| Layer, don't overload | 컨텍스트, 워크로드, 세부 흐름을 [페이지](spec-format.md#페이지)로 나눈다. | `panel-too-short` |
| Version control | 사양 파일과 `.drawio` 파일을 워크로드의 다른 자산과 같은 저장소에 둔다. | 없음 |

### 관행 원문

L1의 관행 문장은 다음과 같다. "Be accurate", "Use official icons and service names", "Layer, don't overload"는 이 스킬과 관련된 부분만 옮겼다.

- **Use standard notations:** "Use widely recognized symbols, icons, and presentation conventions to ensure good readability and consistent interpretation across different audiences."
- **Avoid ambiguous lines:** "Diagrams often show relationships between entities using lines. Be consistent in how you represent these relationships throughout your diagrams."
- **Use directional arrows:** "Lines without arrows make relationships unclear. Always use arrows, and when bi-directional communication exists, either show two separate flows (preferred) or annotate a single arrow with request/response notes."
- **Avoid bidirectional arrows:** "Double arrows imply bidirectional dependencies, which can create confusion. Use single-ended arrows to represent the flow from the initiating component (client) to the dependency (server)."
- **Label everything clearly:** "Provide clear, accurate, and meaningful labels for each icon, grouping container, and relationship. Label lines when relationships aren't immediately obvious from context."
- **Maintain consistency:** "Use standardized colors, casing, icons, icon sizes, line weights, line types, arrow heads, and border styles for similar elements. Apply the same taxonomy across every diagram in the solution set. Draw from existing organizational standards or taxonomies."
- **Be accurate:** "don't depict a PaaS service inside a subnet if it's actually accessed over a private endpoint"
- **Include metadata:** "Include elements such as title, description, last updated date, author, version, and external references."
- **Use official icons and service names:** "always use the latest official icons and naming conventions. Don't stretch or recolor brand shapes arbitrarily. Don't substitute marketing logos for conceptual elements"
- **Provide a legend:** "If you introduce border or line semantics, for example, solid is a synchronous call while dash is asynchronous, include a compact legend."
- **Design for accessibility:** "Ensure sufficient color contrast. Avoid relying solely on color to distinguish types, instead consistently pair color with pattern."
- **Layer, don't overload:** "Resist the urge to encode every subsystem, data classification, and runtime path in a single diagram."
- **Version control:** "Store diagram source files in the same repository or documentation store as the workload's other versioned assets."

## 색 대비

L1의 "Design for accessibility" 관행은 충분한 색 대비를 요구한다. 그러나 L1은 대비 수치를 정하지 않는다. 그래서 이 스킬은 W1의 두 성공 기준을 쓴다.

| 성공 기준 | 대상 | 최소 대비 |
| --- | --- | --- |
| [1.4.3 Contrast (Minimum)](https://www.w3.org/TR/WCAG21/#contrast-minimum) | 글자, 배지 번호 | 4.5:1. 큰 글자는 3:1 |
| [1.4.11 Non-text Contrast](https://www.w3.org/TR/WCAG21/#non-text-contrast) | 엣지, 범례 선, 그룹 테두리, 노드의 `frame` 테두리 | 3:1 |

1.4.11은 "Parts of graphics required to understand the content"에 3:1 이상의 대비를 요구한다. 이 스킬은 엣지와 테두리를 이런 그래픽 요소로 본다.

W1은 큰 글자를 "at least 18 point or 14 point bold or font size that would yield equivalent size for Chinese, Japanese and Korean (CJK) fonts"로 정의한다. W1은 px 값을 정하지 않는다. W2에 따르면 1pt는 1/72in이고 1px는 1/96in이므로, 1pt는 4/3px다. 렌더러는 이 비율로 큰 글자 기준을 24px로, 굵은 큰 글자 기준을 18.66px로 계산한다. 한국어 글자에도 같은 기준을 쓴다.

두 스타일의 기본 색에서 가장 낮은 대비는 다음과 같다. 배경 후보는 흰색 캔버스, 패널, 모든 그룹 채움 색이다. 배경 후보가 다른 항목은 표 아래 목록에 적었다.

| 항목 | 기준 | `reference` 스타일 | `card` 스타일 |
| --- | --- | --- | --- |
| 본문 글자(`ink`) | 4.5:1 | 15.55:1(#16191F, 패널 위) | 12.67:1(#102D46) |
| 보조 글자(`muted`) | 4.5:1 | 4.79:1(#5F6B7A, 패널 위) | 5.54:1(#4D6475) |
| 강조 글자(`accent`) | 4.5:1 | 4.53:1(#0078D4, 흰색 위) | 5.18:1(#007364) |
| 엣지와 범례 선 | 3:1 | 3.14:1(`control`의 #7D8998, 패널 위) | 4.45:1(`control`의 #62727F) |
| 그룹 테두리 | 3:1 | 3.32:1(#7D8998) | 3.05:1(#6890AB) |
| 노드의 `frame` 테두리 | 3:1 | 3.32:1(기본 선 색 `gray`의 #7D8998) | 4.45:1(기본 선 색 `gray`의 #62727F) |
| 배지의 흰색 번호 | 4.5:1 | 17.6:1(#16191F 위) | 4.96:1(#62727F 위) |

- 범례 선은 패널 위에 그리므로 엣지와 범례 선의 값에는 패널을 배경 후보에 넣었다. 그룹과 노드는 패널 위에 그리지 않으므로 테두리 값에는 패널을 넣지 않았다.
- `reference` 스타일에서 그룹 테두리와 `frame` 테두리의 최저값은 `foundry` 그룹 채움 색(#F8F6FD) 위의 값이다.
- `card` 스타일에서 글자, 엣지, 테두리의 최저값은 모두 `foundry` 그룹 채움 색(#F4F1FB) 위의 값이다.
- `reference` 스타일은 `accent`를 푸터 가운데 표제에만 쓴다. 이 표제는 15px 굵은 글자이므로 4.5:1 기준을 쓴다. 표제는 흰색 위에만 그린다. 패널 위라면 대비가 4.00:1이다.
- `card` 스타일의 배지는 흐름 종류의 색으로 채운다. 번호는 14px 굵은 글자이므로 4.5:1 기준을 쓴다. `control` 외의 흐름 색 중 가장 낮은 값은 5.43:1(#B54708)이다.
- `card` 노드의 칩 글자는 칩 채움 색(#F1F6F9) 위에 그린다. 이 대비는 `reference` 스타일에서 16.17:1, `card` 스타일에서 12.98:1로 표의 본문 글자 값보다 높다.

검사 방법은 [검증하는 규칙](style-guide.md#검증하는-규칙)에 있다. 기본값이 아닌 색은 렌더링할 때 `design-contrast` 경고로 검사한다.

## 참조 아키텍처

작업을 시작할 때 L3에서 가장 가까운 참조 아키텍처를 찾는다. 자주 쓰는 문서는 다음과 같다.

| 문서 | 이런 경우에 쓴다 | 확인한 절 |
| --- | --- | --- |
| L4 | 영역 중복 App Service, Application Gateway와 웹 애플리케이션 방화벽, 프라이빗 엔드포인트 | Network flows, Virtual network segmentation and security |
| L5 | Microsoft Foundry 에이전트 채팅 앱 | Workflow, Components |
| L6 | 허브-스포크 네트워크 | Hub-spoke concepts, Spoke network connectivity |
| L7 | AKS 클러스터의 수신 트래픽과 송신 트래픽 | Network topology, Ingress traffic flow, Egress traffic flow |
| L8 | 플랫폼 랜딩 존과 워크로드 랜딩 존의 경계 | Platform landing zone, Workload landing zone |
| L9 | Microsoft Fabric과 OneLake 기반 분석 플랫폼 | Data flow, Components |

### 번호 단계

L4, L5, L7은 그림의 흐름을 번호 목록으로 설명한다.

- L4의 "Network flows" 절에는 번호 목록 두 개(4단계, 3단계)가 있다. L4는 "The diagram resembles the baseline App Service architecture with two numbered network flows."라고 쓴다.
- L5의 "Workflow" 절은 7단계 번호 목록이다.
- L7의 "Ingress traffic flow" 절은 4단계 번호 목록이다.

이 스킬은 이 형식에 맞춰 흐름에 번호 배지를 붙이고 패널에 같은 번호의 단계를 쓴다. 배지와 단계를 1:1로 맞추는 규칙은 이 스킬의 관례다.

## 범위 경계

L17과 L18은 가상 네트워크의 범위를 다음과 같이 설명한다.

- "A virtual network is limited to a single region." (L17)
- "All Azure resources are created in an Azure region and subscription." (L18)
- "You can create a resource only in a virtual network that exists in the same region and subscription as the resource." (L18)
- "But you can connect virtual networks that exist in different subscriptions and regions." (L18)

이 스킬은 범위 경계를 다음 규칙으로 중첩한다.

1. 필수: 서브넷은 가상 네트워크 안에 그린다.
2. 필수: 가상 네트워크는 한 지역 경계와 한 구독 경계 안에 그린다.
3. 권장: 지역이나 구독이 다른 가상 네트워크는 따로 그리고, 피어링 같은 연결은 엣지로 그린다.
4. 필수: 지역과 구독 중 바깥 경계는 실제 구성에 맞춘다. 한 구독의 리소스가 여러 지역에 있으면 구독을 바깥에 둔다. 한 지역에 여러 구독의 리소스가 있으면 지역을 바깥에 둔다.
5. 허용: 그림의 목적에 필요 없는 경계는 생략한다. 예시 사양은 지역 경계 없이 구독 경계만 그린다.

## 이 스킬의 관례

다음 규칙은 Learn 문서에서 가져오지 않았다. 이 스킬이 정한 관례다.

- 흐름은 왼쪽에서 오른쪽으로, 위에서 아래로 읽히게 배치한다.
- 번호 배지와 패널 단계를 1:1로 맞춘다.
- [디자인 기준](../SKILL.md#디자인-기준)과 [디자인 규칙](style-guide.md#디자인-규칙)의 수치는 이 스킬이 정한 값이다. 정렬 허용 오차, 꺾임 수, 빈 공간, 크기 기준이 여기에 속한다. 수치 중 색 대비 기준만 W1을 따른다.
- `reference` 스타일의 색과 배치는 이 스킬의 기본 디자인이다. Microsoft가 정한 표준 양식이 아니다.

## 다시 확인하는 방법

권장: 규칙을 고치거나 새 아이콘 팩 버전을 쓰기 전에 다음 순서로 근거를 다시 확인한다.

1. [문서 목록](#문서-목록)의 각 문서를 연다. 문서의 수정일(`ms.date`)이 표와 다르면 인용문, 절 제목, 번호 목록을 다시 대조한다.
2. 새 팩 버전을 쓰려면 `scripts/packs.json`에서 그 팩의 `url`, `file`, `title`을 고친다.
3. 아이콘 팩을 다시 내려받는다. 일부 팩만 받으려면 `--packs`에 팩 이름을 쉼표로 구분해 쓴다.

   ```
   python $SKILL/scripts/icon_tool.py fetch --force
   ```

4. [아이콘 카탈로그](icon-catalog.md)의 키를 `icon_tool.py search`로 확인한다. 키나 개수가 바뀌었으면 카탈로그의 확인일과 표를 고친다.
5. 예시 사양을 `--strict`로 렌더링하고 종료 코드가 0인지 확인한다.

   ```
   python $SKILL/scripts/render.py $SKILL/examples/baseline-web-app.yaml --out out --strict
   ```
