# 아이콘 카탈로그

이 문서는 렌더러가 쓰는 공식 아이콘 팩, 아이콘 키, 자주 쓰는 키, 대체 아이콘, 이용 조건을 설명한다. 아이콘 키는 [노드](spec-format.md#노드)의 `icon`과 `icons`, [다른 노드 종류](spec-format.md#다른-노드-종류)와 [그룹](spec-format.md#그룹)의 `icon`, [밴드](spec-format.md#밴드) 항목의 `icon`과 `icons`에 쓴다. 팩과 규칙의 근거 문서는 [learn-sources.md](learn-sources.md)에 있다.

이 문서의 키와 개수는 2026-11-20에 [아이콘 팩](#아이콘-팩) 표의 버전으로 확인했다. 팩 버전이 바뀌면 키와 개수가 바뀔 수 있다.

## 용어

| 용어 | 뜻 |
| --- | --- |
| 아이콘 팩 | Microsoft가 배포하는 공식 아이콘 압축 파일 하나다. 렌더러는 6개 팩을 쓴다. |
| 캐시 | 내려받은 아이콘 팩을 저장하는 사용자 폴더다. |
| 아이콘 폴더 | 압축 파일에서 SVG가 들어 있는 기준 폴더다. `scripts/packs.json`의 `root` 값이다. |
| 아이콘 키 | 사양에서 아이콘 하나를 가리키는 문자열이다. `팩:이름` 또는 `팩:폴더/이름` 형식이다. |
| 정리한 이름 | SVG 파일 이름에서 `.svg`와 팩별 접두사, 접미사를 뺀 이름이다. |
| 대체 아이콘 | 공식 아이콘이 없는 Microsoft 제품이나 서비스를 다른 아이콘으로 나타낸 것이다. |
| 항목 아이콘 | Fabric 작업 영역의 항목(레이크하우스, 노트북 등)을 나타내는 아이콘이다. 파일 이름이 `_item`으로 끝난다. |

## 아이콘 팩

Azure 아키텍처 아이콘 문서는 Azure 아이콘과 함께 Microsoft 365, Dynamics 365, Microsoft Entra, Microsoft Fabric, Power Platform 아이콘 세트를 안내한다. 렌더러는 이 6개 세트만 쓴다. 내려받기 URL, 파일 이름, 이용 조건은 `scripts/packs.json`에 있다.

| 팩 | 내용 | 버전 | 출처 문서 | SVG 수 |
| --- | --- | --- | --- | --- |
| `azure` | Azure 서비스 | Azure Public Service Icons V25 | [Azure 아키텍처 아이콘](https://learn.microsoft.com/azure/architecture/icons/) | 721 |
| `fabric` | Microsoft Fabric 워크로드와 항목 | `@fabric-msft/svg-icons` 12.0.0 | [Fabric 아이콘 지침](https://learn.microsoft.com/fabric/fundamentals/icons), [Fabric 아이콘 npm 패키지](https://www.npmjs.com/package/@fabric-msft/svg-icons) | 1,743 |
| `powerplatform` | Power Platform, Copilot Studio, Agent 365 | Power Platform icons (scalable) | [Power Platform 아이콘](https://learn.microsoft.com/power-platform/guidance/icons) | 8 |
| `entra` | Microsoft Entra 제품군 | Microsoft Entra architecture icons (Oct 2023) | [Microsoft Entra 아키텍처 아이콘](https://learn.microsoft.com/entra/architecture/architecture-icons) | 14 |
| `m365` | 사람, 문서, 장치 같은 일반 개념의 콘텐츠 아이콘 | Microsoft 365 content icons (2024) | [Microsoft 365 아키텍처 아이콘과 템플릿](https://learn.microsoft.com/microsoft-365/solutions/architecture-icons-templates) | 963 |
| `dynamics365` | Dynamics 365 앱 | Dynamics 365 icons (scalable) | [Dynamics 365 아이콘](https://learn.microsoft.com/dynamics365/get-started/icons) | 16 |

- `fabric` 팩은 npm 패키지 12.0.0으로 고정한다. 패키지 메타데이터의 라이선스는 MIT다. 이 팩의 출처 기록(`source_page`)은 npm 패키지 페이지다.
- Microsoft 365 아이콘 문서는 보관된 문서다. 링크를 열면 이전 버전 문서로 이동한다.

## 캐시와 내려받기

캐시 폴더는 다음 순서로 정한다.

1. `--icons DIR` 옵션
2. 환경 변수 `AZDIAGRAM_ICON_CACHE`
3. `%LOCALAPPDATA%\azure-architecture-diagram\icons`. `LOCALAPPDATA`가 없으면 `~/.cache/azure-architecture-diagram/icons`다.

- 렌더러는 압축 파일을 풀지 않고 메모리에서 SVG를 읽는다.
- 캐시에 유효한 파일이 있으면 `fetch`는 내려받지 않는다. 다시 내려받으려면 `--force`를 붙인다.
- `fetch`는 받은 파일을 `.part` 파일로 저장하고 압축 형식과 아이콘 폴더의 SVG를 검사한다. 검사를 통과해야 캐시 파일을 바꾼다. 내려받기에 실패하면 기존 캐시 파일은 그대로 남는다.
- `fabric` 팩은 `npm pack`을 먼저 시도한다. npm이 없거나 실패하면 `packs.json`의 `url`에서 받는다.
- 필수: 아이콘 압축 파일과 SVG 파일을 저장소에 커밋하지 않는다.

### 내려받기에 실패하면

`fetch`가 실패하면 표준 오류에 다음 형식의 메시지를 출력하고 종료 코드 1로 끝난다.

```
azure: FAILED (url: <오류 내용>). Download it from https://learn.microsoft.com/azure/architecture/icons/ and run: icon_tool.py import azure <file>
```

이 경우 다음 순서로 진행한다.

1. 브라우저로 메시지에 나온 출처 문서를 연다.
2. 이용 조건을 확인하고 압축 파일을 내려받는다.
3. 내려받은 파일을 캐시로 가져온다.

   ```
   python $SKILL/scripts/icon_tool.py import azure ./Azure_Public_Service_Icons_V25.zip
   ```

4. 캐시 상태를 확인한다.

   ```
   python $SKILL/scripts/icon_tool.py packs
   ```

- `import`는 압축 형식과 아이콘 폴더만 검사한다. 버전은 검사하지 않는다.
- 권장: `packs.json`에 적힌 버전과 같은 파일을 가져온다. 출처 기록은 `packs.json`의 제목과 URL을 쓰고, `archive_sha256`만 실제 파일에서 계산하기 때문이다.
- `fabric` 팩의 형식은 tgz다. `import`는 zip 파일을 거부한다. 직접 받을 때는 `packs.json`의 `fabric` 항목에 있는 `url`의 tgz 파일을 받는다.

## icon_tool.py 명령

캐시 폴더를 바꾸려면 하위 명령 앞에 `--icons DIR`을 쓴다. 예: `python $SKILL/scripts/icon_tool.py --icons ./icons packs`.

| 명령 | 하는 일 | 종료 코드 |
| --- | --- | --- |
| `packs` | 캐시 폴더와 팩별 파일 크기를 출력한다. 없는 팩은 `missing`으로 표시한다. | 0 |
| `fetch [--packs a,b] [--force]` | 팩을 내려받는다. `--packs`에는 팩 이름을 쉼표로 구분해 쓴다. 생략하면 모든 팩을 내려받는다. | 0: 모두 성공했다. 1: 실패한 팩이 있다. 2: 알 수 없는 팩 이름이다. |
| `search QUERY [--pack P] [--limit N]` | 아이콘 키를 한 줄에 하나씩 출력한다. 기본 최대 개수는 40이다. | 0: 결과가 있다. 1: 결과가 없다. |
| `import PACK PATH` | 직접 내려받은 압축 파일을 캐시에 복사한다. | 0: 성공했다. 1: 그 팩의 압축 파일이 아니다. 2: 알 수 없는 팩 이름이다. |

### 검색 규칙

- 검색어는 공백으로 나눈다. 각 단어는 소문자로 바꾸고 영문자, 숫자, 한글만 남긴다.
- 정리한 이름과 폴더 이름도 같은 방법으로 바꿔 비교한다. 모든 단어가 각각 이름이나 폴더 이름에 들어 있어야 결과에 나온다.
- 하이픈은 단어를 나누지 않는다. `AI-Search`는 `aisearch` 한 단어가 되어 결과가 없다. `ai search`는 `azure:ai + machine learning/Cognitive-Search`를 찾는다.
- 부분 문자열로 비교하므로 관계없는 결과가 나올 수 있다. 예를 들어 `entra`는 `azure:iot/IoT-Central-Applications`의 `central`과도 맞는다.
- 결과는 `packs.json`의 팩 순서(`azure`, `fabric`, `powerplatform`, `entra`, `m365`, `dynamics365`)로 나온다. 최대 개수를 넘는 결과는 잘린다. 권장: 찾을 팩을 알면 `--pack`을 붙인다.
- 캐시에 없는 팩은 오류 없이 건너뛴다. 결과가 없으면 `packs`로 캐시를 확인한다.

```
python $SKILL/scripts/icon_tool.py search "managed identit" --pack azure
azure:identity/Entra-Managed-Identities
azure:identity/Managed-Identities
```

## 아이콘 키

### 형식

아이콘 키는 `팩:이름` 또는 `팩:폴더/이름`이다.

```yaml
icon: "azure:networking/Virtual-Networks"
icons: ["azure:networking/Application-Gateways", "azure:networking/Web-Application-Firewall-Policies(WAF)"]
```

- 팩은 첫 번째 콜론 앞의 값이다. [아이콘 팩](#아이콘-팩) 표의 이름 하나를 쓴다.
- 폴더는 마지막 `/` 앞의 전체 값이다. `m365:Microsoft Blue/48x48 Dark Blue Icon/People`처럼 여러 단계 폴더를 쓸 수 있다.
- 이름은 대소문자, 공백, 기호를 무시하고 비교한다. 예를 들어 `azure:networking/virtual networks`도 같은 아이콘이다.
- 폴더는 대소문자만 무시하고 비교한다. 공백과 기호는 정확히 써야 한다. `azure:app-services/App-Services`는 찾지 못한다.
- 정리한 이름 대신 원래 파일 이름(`.svg` 제외)도 쓸 수 있다. 예: `azure:networking/10061-icon-service-Virtual-Networks`.
- 권장: YAML에서는 키를 큰따옴표로 감싼다. 키에 콜론과 공백이 있어 따옴표가 없으면 YAML이 다르게 해석할 수 있기 때문이다.

### 찾는 순서

렌더러는 아이콘 키를 다음 순서로 찾는다.

1. 첫 번째 콜론에서 팩과 이름을 나눈다. 콜론이 없거나 이름이 비어 있으면 오류가 난다.
2. 마지막 `/`에서 폴더와 이름을 나눈다.
3. 정리한 이름이나 원래 파일 이름이 같은 아이콘을 찾는다. 이때 대소문자, 공백, 기호를 무시한다. 폴더가 있으면 그 폴더에서만 찾는다.
4. 결과가 없으면 팩의 접미사를 차례로 붙여 다시 찾는다. 접미사가 있는 팩은 `fabric`뿐이다. `_48_item`을 먼저 붙이고, 결과가 없으면 `_48_color`를 붙인다.
5. 결과가 여러 개이고 키에 폴더가 없으면 팩의 기본 폴더에 있는 결과만 남긴다. 기본 폴더에 결과가 없으면 모두 남긴다. 기본 폴더가 있는 팩은 `entra`와 `m365`다.
6. 결과가 없으면 `not found` 오류가 난다. 결과가 둘 이상 남으면 `is ambiguous` 오류가 난다.

### 팩별 규칙

원래 파일 경로는 아이콘 폴더 기준이다.

| 팩 | 파일 이름에서 빼는 부분 | 기본 폴더 | 원래 파일 | 키 예시 |
| --- | --- | --- | --- | --- |
| `azure` | 앞쪽 번호와 `-icon-service-` | 없음 | `networking/10061-icon-service-Virtual-Networks.svg` | `azure:networking/Virtual-Networks` |
| `fabric` | 없음. 찾을 때 `_48_item`이나 `_48_color`를 붙인다. | 없음 | `lakehouse_48_item.svg` | `fabric:lakehouse` |
| `powerplatform` | 끝의 `_scalable` | 없음 | `Power Platform/PowerApps_scalable.svg` | `powerplatform:PowerApps` |
| `entra` | ` color icon`, ` BW icon` | `Microsoft Entra color icons SVG` | `Microsoft Entra color icons SVG/Microsoft Entra ID color icon.svg` | `entra:Microsoft Entra ID` |
| `m365` | 없음 | `Microsoft Blue/48x48 Dark Blue Icon` | `Microsoft Blue/48x48 Dark Blue Icon/People.svg` | `m365:People` |
| `dynamics365` | 끝의 `_scalable` | 없음 | `Dynamics 365 App Icons/Sales_scalable.svg` | `dynamics365:Sales` |

### 오류 메시지

`render.py`는 다음 메시지 앞에 `spec error: IconError:`를 붙이고 종료 코드 2로 끝난다.

| 메시지 | 원인 | 고치는 방법 |
| --- | --- | --- |
| `icon key '...' must look like 'pack:name'` | 팩 이름이나 콜론이 없다. | `팩:이름` 형식으로 쓴다. |
| `unknown icon pack '...'. Packs: ...` | 팩 이름이 틀렸다. | 메시지의 팩 목록에서 고른다. |
| `icon pack '...' is missing at ...` | 팩을 내려받지 않았다. | `python $SKILL/scripts/icon_tool.py fetch --packs <팩>`을 실행한다. |
| `icon '...' not found. Similar: ...` | 이름이나 폴더가 틀렸거나 팩에 그 아이콘이 없다. | 후보에서 고르거나 `search`로 찾는다. 후보가 `none`이면 [잘못 쓰기 쉬운 키](#잘못-쓰기-쉬운-키)를 확인한다. |
| `icon '...' is ambiguous: ...` | 키에 맞는 아이콘이 둘 이상이다. | 메시지에 나온 키 하나를 그대로 쓴다. 폴더 선택 기준은 [폴더가 필요한 키](#폴더가-필요한-키)에 있다. |

- `Similar` 후보는 키의 이름 부분으로 같은 팩을 검색한 결과다. 최대 6개다.
- `is ambiguous` 다음에는 키가 최대 8개 나온다.

## 폴더가 필요한 키

### Azure 팩의 여러 폴더에 있는 이름

Azure 팩에서 61개 이름이 둘 이상의 폴더에 있다. 이 이름을 폴더 없이 쓰면 `is ambiguous` 오류가 난다.

- `Multi-Factor-Authentication`을 뺀 60개 이름은 모든 폴더의 그림이 같다. 이 경우 폴더는 출처 기록의 `member` 값만 바꾼다.
- `azure:identity/Multi-Factor-Authentication`과 `azure:security/Multifactor-Authentication`은 그림이 다르다. 권장: 한 다이어그램에서는 둘 중 하나만 쓴다.

권장: 같은 서비스를 늘 같은 키로 쓰도록 다음 폴더를 쓴다.

| 키 | 같은 그림이 있는 다른 폴더 |
| --- | --- |
| `azure:app services/App-Services` | `compute`, `containers`, `mobile`, `web` |
| `azure:app services/App-Service-Plans` | `web` |
| `azure:integration/API-Management-Services` | `devops`, `web` |
| `azure:integration/Logic-Apps` | `iot` |
| `azure:monitor/Application-Insights` | `devops`, `management + governance` |
| `azure:monitor/Log-Analytics-Workspaces` | `analytics`, `management + governance` |
| `azure:monitor/Monitor` | `management + governance` |
| `azure:ai + machine learning/Cognitive-Search` | `app services`, `web` |
| `azure:ai + machine learning/Cognitive-Services` | `web` |
| `azure:analytics/Data-Factories` | `databases`, `integration` |
| `azure:analytics/Azure-Synapse-Analytics` | `databases` |
| `azure:analytics/Azure-Data-Explorer-Clusters` | `databases` |
| `azure:analytics/Event-Hubs` | `iot` |
| `azure:analytics/Stream-Analytics-Jobs` | `iot` |
| `azure:management + governance/Recovery-Services-Vaults` | `migrate`, `storage` |
| `azure:management + governance/Cost-Management-and-Billing` | `general`, `migrate` |
| `azure:management + governance/Service-Group-Relationships` | `new icons` |
| `azure:databases/Azure-Cosmos-DB` | `iot` |
| `azure:containers/Container-Instances` | `compute` |
| `azure:containers/Kubernetes-Services` | `compute` |
| `azure:networking/Front-Door-and-CDN-Profiles` | `web` |
| `azure:networking/Network-Watcher` | `monitor` |
| `azure:networking/Private-Link-Services` | `analytics` |
| `azure:networking/CDN-Profiles` | `app services` |
| `azure:compute/Function-Apps` | `iot` |
| `azure:compute/Azure-Spring-Apps` | `web` |
| `azure:compute/Batch-Accounts` | `containers` |

### 같은 폴더에 두 번 있는 이름

다음 이름은 같은 폴더에 서로 다른 그림으로 두 번 있다. 폴더를 넣어도 `is ambiguous` 오류가 난다. 원래 파일 이름으로 쓴다.

| 이름 | 키 |
| --- | --- |
| Workspaces | `azure:compute/00330-icon-service-Workspaces`, `azure:compute/00400-icon-service-Workspaces` |
| Load-Balancer-Hub | `azure:networking/02302-icon-service-Load-Balancer-Hub`, `azure:networking/029029174-icon-service-Load-Balancer-Hub` |

### new icons 폴더

Azure 팩의 최신 아이콘 19개는 서비스 분류 폴더가 아니라 `new icons` 폴더에 있다. 예: `azure:new icons/AI-Gateway`, `azure:new icons/Landing-Zone`.

이 폴더의 이름은 Toolchain-Orchestrator, Landing-Zone, Service-Group-Relationships, Azure-Access-Point, Microsoft-Discovery, Azure-Data-Transfer, Agentic-Web-Apps, Resiliency, DDoS-Custom-Policy, Disconnected-Operations, Azure-Data-Sharing, Azure-Confidential-Clean-Rooms, AI-Gateway, ACA-Sandboxes, Azure-HorizonDB, Azure-Encrypted-Transport, AI-Manager, App-Service-Builder, Azure-Device-Registry다.

### M365 팩

- 키에 폴더가 없고 같은 이름이 기본 폴더 `Microsoft Blue/48x48 Dark Blue Icon`에도 있으면 기본 폴더의 아이콘이 선택된다. 이때 오류나 경고가 없다.
- 기본 폴더에 없는 이름이 여러 폴더에 있으면 `is ambiguous` 오류가 난다. 예를 들어 `m365:Organization_Dark`는 `Planner Green`과 `SharePoint Teal` 폴더에 있다.
- 권장: 기본 폴더가 아닌 아이콘은 키에 폴더를 넣는다. 예: `m365:SharePoint Teal/48x48 SVG Icon/Organization_Dark`.

## 서비스 이름과 다른 키

아이콘 파일 이름은 서비스의 현재 이름과 다를 수 있다. 서비스 이름은 바뀔 수 있다. 그림 레이블에는 근거 문서의 최신 이름을 쓴다.

| 서비스 | 키 | 참고 |
| --- | --- | --- |
| AI Search | `azure:ai + machine learning/Cognitive-Search` | |
| Document Intelligence | `azure:ai + machine learning/Form-Recognizers` | |
| AI services | `azure:ai + machine learning/Cognitive-Services` | |
| Microsoft Foundry | `azure:ai + machine learning/AI-Foundry` | |
| Microsoft Sentinel | `azure:security/Azure-Sentinel` | |
| Front Door | `azure:networking/Front-Door-and-CDN-Profiles` | |
| Web Application Firewall | `azure:networking/Web-Application-Firewall-Policies(WAF)` | |
| Container Apps 환경 | `azure:other/Container-Apps-Environments` | 팩에는 `Container-Apps`라는 이름의 아이콘이 없다. |
| Power BI | `fabric:power_bi` | `azure:analytics/Power-BI-Embedded`는 다른 서비스다. |
| Microsoft Entra ID | `entra:Microsoft Entra ID` | Azure 팩에는 Entra ID 제품 아이콘이 없다. |
| Dynamics 365 Customer Service | `dynamics365:CustomerServices` | |

## 자주 쓰는 키

### Azure 네트워크

| 서비스 | 키 |
| --- | --- |
| Virtual Network | `azure:networking/Virtual-Networks` |
| 서브넷 | `azure:networking/Subnet` |
| Application Gateway | `azure:networking/Application-Gateways` |
| WAF 정책 | `azure:networking/Web-Application-Firewall-Policies(WAF)` |
| Azure Firewall | `azure:networking/Firewalls` |
| Azure Firewall 정책 | `azure:networking/Azure-Firewall-Policy` |
| Azure Bastion | `azure:networking/Bastions` |
| Private Link | `azure:networking/Private-Link` |
| 프라이빗 엔드포인트 | `azure:other/Private-Endpoints` |
| DNS 영역 | `azure:networking/DNS-Zones` |
| DNS Private Resolver | `azure:networking/DNS-Private-Resolver` |
| Load Balancer | `azure:networking/Load-Balancers` |
| 가상 네트워크 게이트웨이(VPN, ExpressRoute) | `azure:networking/Virtual-Network-Gateways` |
| ExpressRoute 회로 | `azure:networking/ExpressRoute-Circuits` |
| 공용 IP 주소 | `azure:networking/Public-IP-Addresses` |
| NAT Gateway | `azure:networking/NAT` |
| 네트워크 보안 그룹 | `azure:networking/Network-Security-Groups` |
| 경로 테이블 | `azure:networking/Route-Tables` |
| DDoS Protection | `azure:networking/DDoS-Protection-Plans` |
| Traffic Manager | `azure:networking/Traffic-Manager-Profiles` |
| Virtual WAN | `azure:networking/Virtual-WANs` |
| 네트워크 인터페이스 | `azure:networking/Network-Interfaces` |
| Front Door | `azure:networking/Front-Door-and-CDN-Profiles` |

- 프라이빗 DNS 영역 전용 아이콘은 없다. 예시 사양은 `azure:networking/DNS-Zones`를 쓴다.
- `networking` 폴더에는 `Private-Link-Service`와 `Private-Link-Services`가 따로 있다.

### Azure 컴퓨팅과 컨테이너

| 서비스 | 키 |
| --- | --- |
| Virtual Machines | `azure:compute/Virtual-Machine` |
| Virtual Machine Scale Sets | `azure:compute/VM-Scale-Sets` |
| Azure Functions | `azure:compute/Function-Apps` |
| Azure Kubernetes Service | `azure:containers/Kubernetes-Services` |
| Container Instances | `azure:containers/Container-Instances` |
| Container Registry | `azure:containers/Container-Registries` |
| Container Apps 환경 | `azure:other/Container-Apps-Environments` |
| Batch | `azure:compute/Batch-Accounts` |

### Azure 웹과 통합

| 서비스 | 키 |
| --- | --- |
| App Service | `azure:app services/App-Services` |
| App Service 계획 | `azure:app services/App-Service-Plans` |
| Static Web Apps | `azure:web/Static-Apps` |
| API Management | `azure:integration/API-Management-Services` |
| Logic Apps | `azure:integration/Logic-Apps` |
| Service Bus | `azure:integration/Azure-Service-Bus` |
| Event Grid | `azure:integration/Event-Grid-Topics` |

### Azure 데이터와 분석

| 서비스 | 키 |
| --- | --- |
| SQL Database | `azure:databases/SQL-Database` |
| SQL Managed Instance | `azure:databases/SQL-Managed-Instance` |
| Azure Cosmos DB | `azure:databases/Azure-Cosmos-DB` |
| Azure Database for PostgreSQL | `azure:databases/Azure-Database-PostgreSQL-Server` |
| Azure Database for MySQL | `azure:databases/Azure-Database-MySQL-Server` |
| Azure Cache for Redis | `azure:databases/Cache-Redis` |
| Azure Managed Redis | `azure:databases/Azure-Managed-Redis` |
| 스토리지 계정 | `azure:storage/Storage-Accounts` |
| Event Hubs | `azure:analytics/Event-Hubs` |
| Data Factory | `azure:analytics/Data-Factories` |
| Azure Databricks | `azure:analytics/Azure-Databricks` |
| Synapse Analytics | `azure:analytics/Azure-Synapse-Analytics` |
| Data Explorer | `azure:analytics/Azure-Data-Explorer-Clusters` |
| Stream Analytics | `azure:analytics/Stream-Analytics-Jobs` |
| Power BI Embedded | `azure:analytics/Power-BI-Embedded` |

Azure 팩의 Data Lake Storage 아이콘(`azure:storage/Data-Lake-Storage-Gen1`, `azure:analytics/Data-Lake-Store-Gen1`)은 Gen1 서비스 아이콘이다. 현재 Data Lake Storage는 별도 서비스나 계정 유형이 아니다. 스토리지 계정의 Blob Storage에서 계층 구조 네임스페이스를 켜서 쓰는 기능이다([Azure Data Lake Storage 개요](https://learn.microsoft.com/azure/storage/blobs/data-lake-storage-introduction)). 권장: `azure:storage/Storage-Accounts`를 쓰고 레이블에 Data Lake Storage를 쓴다. 스토리지 계정이 실제 리소스이므로 이 아이콘은 대체 아이콘이 아니다.

### Azure AI

| 서비스 | 키 |
| --- | --- |
| Microsoft Foundry | `azure:ai + machine learning/AI-Foundry` |
| Azure OpenAI | `azure:ai + machine learning/Azure-OpenAI` |
| AI Search | `azure:ai + machine learning/Cognitive-Search` |
| AI services | `azure:ai + machine learning/Cognitive-Services` |
| Document Intelligence | `azure:ai + machine learning/Form-Recognizers` |
| Machine Learning | `azure:ai + machine learning/Machine-Learning` |
| Bot Service | `azure:ai + machine learning/Bot-Services` |
| Speech | `azure:ai + machine learning/Speech-Services` |
| Language | `azure:ai + machine learning/Language` |
| AI Gateway | `azure:new icons/AI-Gateway` |

### Azure 모니터링

| 서비스 | 키 |
| --- | --- |
| Azure Monitor | `azure:monitor/Monitor` |
| Application Insights | `azure:monitor/Application-Insights` |
| Log Analytics 작업 영역 | `azure:monitor/Log-Analytics-Workspaces` |
| Azure Workbooks | `azure:monitor/Azure-Workbooks` |

### Azure 보안과 ID

| 서비스 | 키 |
| --- | --- |
| Key Vault | `azure:security/Key-Vaults` |
| Microsoft Sentinel | `azure:security/Azure-Sentinel` |
| Microsoft Defender for Cloud | `azure:security/Microsoft-Defender-for-Cloud` |
| 조건부 액세스 | `azure:security/Conditional-Access` |
| 관리 ID | `azure:identity/Managed-Identities` |
| 사용자 | `azure:identity/Users` |

### Azure 관리와 거버넌스

| 서비스 | 키 |
| --- | --- |
| 구독 | `azure:general/Subscriptions` |
| 리소스 그룹 | `azure:general/Resource-Groups` |
| 관리 그룹 | `azure:general/Management-Groups` |
| Azure Policy | `azure:management + governance/Policy` |
| Azure Arc | `azure:management + governance/Azure-Arc` |
| Recovery Services 자격 증명 모음 | `azure:management + governance/Recovery-Services-Vaults` |
| Backup 자격 증명 모음 | `azure:other/Backup-Vault` |
| Cost Management | `azure:management + governance/Cost-Management-and-Billing` |
| 랜딩 존 | `azure:new icons/Landing-Zone` |

### Microsoft Entra

색 아이콘 7개가 기본 폴더 `Microsoft Entra color icons SVG`에 있다.

| 제품 | 키 |
| --- | --- |
| Microsoft Entra ID | `entra:Microsoft Entra ID` |
| Microsoft Entra ID Governance | `entra:Microsoft Entra ID Governance` |
| Microsoft Entra Internet Access | `entra:Microsoft Entra Internet Access` |
| Microsoft Entra Private Access | `entra:Microsoft Entra Private Access` |
| Microsoft Entra Verified ID | `entra:Microsoft Entra Verified ID` |
| Microsoft Entra Workload ID | `entra:Microsoft Entra Workload ID` |
| Microsoft Entra 제품군 | `entra:Microsoft Entra Product Family` |

- 흑백 아이콘은 키에 폴더를 넣는다. 예: `entra:Microsoft Entra BW icons SVG/Microsoft Entra ID`.
- 흑백 폴더에는 Workload ID 아이콘이 없다.
- 흑백 폴더에만 `entra:Microsoft Entra ID filled`가 있다.

### Power Platform

| 제품 | 키 |
| --- | --- |
| Power Apps | `powerplatform:PowerApps` |
| Power Automate | `powerplatform:PowerAutomate` |
| Power Pages | `powerplatform:PowerPages` |
| Dataverse | `powerplatform:Dataverse` |
| AI Builder | `powerplatform:AIBuilder` |
| Power Platform | `powerplatform:PowerPlatform` |
| Copilot Studio | `powerplatform:CopilotStudio` |
| Agent 365 | `powerplatform:Agent365` |

### Microsoft Fabric 워크로드

워크로드와 제품은 컬러 아이콘(`_48_color`)을 쓴다.

| 워크로드 | 키 |
| --- | --- |
| Microsoft Fabric | `fabric:fabric` |
| OneLake | `fabric:one_lake` |
| Power BI | `fabric:power_bi` |
| Microsoft Purview | `fabric:purview` |
| Copilot | `fabric:copilot` |
| Data Engineering | `fabric:data_engineering` |
| Data Factory | `fabric:data_factory_48_color` |
| Data Warehouse | `fabric:data_warehouse_48_color` |
| Data Science | `fabric:data_science` |
| Real-Time Intelligence | `fabric:real_time_intelligence` |
| Databases | `fabric:databases` |
| Industry Solutions | `fabric:industry_solutions` |

### Microsoft Fabric 항목

작업 영역의 항목은 항목 아이콘(`_item`)을 쓴다.

| 항목 | 키 |
| --- | --- |
| Lakehouse | `fabric:lakehouse` |
| Warehouse | `fabric:data_warehouse` |
| Pipeline | `fabric:pipeline` |
| Copy job | `fabric:copy_job` |
| Dataflow Gen2 | `fabric:dataflow_gen2` |
| Notebook | `fabric:notebook` |
| Eventstream | `fabric:eventstream` |
| Eventhouse | `fabric:event_house` |
| KQL database | `fabric:kql_database` |
| Semantic model | `fabric:semantic_model` |
| Report | `fabric:report` |
| Data agent | `fabric:data_agent` |
| Ontology | `fabric:ontology` |
| SQL database | `fabric:sql_database` |
| Mirrored database | `fabric:mirrored_generic_database` |

### Microsoft 365 콘텐츠 아이콘

M365 팩은 제품 로고가 아니라 일반 개념을 나타내는 콘텐츠 아이콘이다. 사용자, 클라이언트, 외부 시스템을 그릴 때 쓴다.

| 개념 | 키 |
| --- | --- |
| 사람 | `m365:People` |
| 건물 | `m365:Building` |
| 데이터베이스 | `m365:Database` |
| 데스크톱 컴퓨터 | `m365:Desktop Tower` |
| 문서 | `m365:Document` |
| 웹 | `m365:Globe` |
| 상담원 | `m365:Headset` |
| 관리자 | `m365:Person Settings` |
| 설정 | `m365:Settings` |

### Dynamics 365

| 앱 | 키 |
| --- | --- |
| Dynamics 365 제품군 | `dynamics365:Dynamics365` |
| Sales | `dynamics365:Sales` |
| Sales Insights | `dynamics365:SalesInsights` |
| Customer Service | `dynamics365:CustomerServices` |
| Contact Center | `dynamics365:ContactCenter` |
| Field Service | `dynamics365:FieldService` |
| Customer Insights | `dynamics365:CustomerInsights` |
| Customer Voice | `dynamics365:CustomerVoice` |
| Business Central | `dynamics365:BusinessCentral` |
| Commerce | `dynamics365:Commerce` |
| Finance | `dynamics365:Finance` |
| Finance and Operations | `dynamics365:FinanceOperations` |
| Human Resources | `dynamics365:HumanResources` |
| Intelligent Order Management | `dynamics365:IntelligentOrderManagement` |
| Project Operations | `dynamics365:ProjectOperations` |
| Supply Chain Management | `dynamics365:SupplyChainManagement` |

## 잘못 쓰기 쉬운 키

| 잘못 쓴 키 | 오류 | 올바른 키 |
| --- | --- | --- |
| `azure:App-Services` | `is ambiguous` | `azure:app services/App-Services` |
| `azure:app-services/App-Services` | `not found` | `azure:app services/App-Services` |
| `azure:integration/Service-Bus` | `not found. Similar: azure:integration/Azure-Service-Bus` | `azure:integration/Azure-Service-Bus` |
| `azure:other/Container-App-Environments` | `not found` | `azure:other/Container-Apps-Environments` |
| `azure:AI-Search` | `not found. Similar: none` | `azure:ai + machine learning/Cognitive-Search` |
| `azure:Entra-ID` | `not found` | `entra:Microsoft Entra ID` |
| `entra:Conditional Access` | `not found. Similar: none` | `azure:security/Conditional-Access` |
| `powerplatform:PowerBI` | `not found. Similar: none` | `fabric:power_bi` |
| `fabric:data_pipeline` | `not found. Similar: none` | `fabric:pipeline` |
| `azure:Dynamics-365` | `not found. Similar: none` | `dynamics365:Dynamics365` |
| `azure:compute/Workspaces` | `is ambiguous` | `azure:compute/00330-icon-service-Workspaces` 또는 `azure:compute/00400-icon-service-Workspaces`. 그림이 다르다. |
| `m365:Organization_Dark` | `is ambiguous` | `m365:Planner Green/48x48 SVG Icons/Organization_Dark` 또는 `m365:SharePoint Teal/48x48 SVG Icon/Organization_Dark` |
| `m365:Teams` | `not found` | Teams 제품 아이콘은 없다. [대체 아이콘](#대체-아이콘)을 쓴다. |

## Fabric 항목 아이콘과 컬러 아이콘

Fabric 팩은 파일 이름의 끝으로 아이콘 종류를 나눈다.

| 파일 이름 끝 | 용도 | 크기 |
| --- | --- | --- |
| `_item` | Fabric 항목 아이콘이다. 대부분 둥근 사각형 타일 위에 기호가 있다. 63종이다. | 20, 24, 32, 40, 48, 64 |
| `_48_color` | Fabric 워크로드와 제품의 컬러 아이콘이다. 15종이다. | 48 |
| `_48_non-item` | 항목이 아닌 대상의 컬러 아이콘이다. `folder`, `group_workspace`, `my_workspace` 등 7종이다. | 48 |
| `_48_regular`, `_48_filled` | 기호 아이콘이다. 각각 15종이다. 30개 중 24개는 색을 `currentColor`로만 지정한 단색 아이콘이다. | 48 |

- 필수: 제품과 워크로드는 `_48_color` 아이콘으로 나타낸다.
- 필수: 항목은 `_item` 아이콘으로 나타낸다.
- 필수: `_48_regular`, `_48_filled`, `_48_non-item` 아이콘으로 제품이나 항목을 나타내지 않는다. `_48_regular`와 `_48_filled` 아이콘은 대부분 제품 색이 없는 단색 아이콘이다.
- 접미사 없이 쓰면 `_48_item`을 먼저 찾고, 없으면 `_48_color`를 찾는다.
- `fabric:data_factory`와 `fabric:data_warehouse`는 항목 아이콘으로 찾는다. 워크로드를 그리려면 `fabric:data_factory_48_color`와 `fabric:data_warehouse_48_color`를 쓴다.
- 다른 크기의 항목 아이콘은 크기를 넣어 쓴다. 예: `fabric:lakehouse_64_item`.
- 렌더러는 노드와 밴드 항목에서 항목 아이콘을 1.12배로 그린다. 타일 위의 기호가 같은 크기의 다른 아이콘보다 작아 보이기 때문이다. 자세한 내용은 [자동 디자인 기능](style-guide.md#자동-디자인-기능)에 있다.

## 팩별 주의 사항

### Azure

- 외부 ID 아이콘은 그림이 서로 다른 3개가 있다: `azure:identity/External-Identities`, `azure:identity/external-id`, `azure:identity/external-id-modified`. 권장: 한 다이어그램에서는 하나만 쓴다.
- 관리 ID 아이콘은 그림이 서로 다른 2개가 있다: `azure:identity/Managed-Identities`, `azure:identity/Entra-Managed-Identities`. 권장: 한 다이어그램에서는 하나만 쓴다.
- Azure 팩에는 Microsoft Entra ID 제품 아이콘이 없다. Entra Connect, 앱 등록 같은 Entra 기능 아이콘은 Azure 팩의 `identity` 폴더에 있다. 예: `azure:identity/Entra-Connect`, `azure:identity/App-Registrations`.
- Entra Verified ID, Private Access, Internet Access 아이콘은 Azure 팩과 `entra` 팩에 모두 있다. 권장: Entra 제품은 `entra` 팩을 쓴다. 한 다이어그램에서 같은 제품을 두 팩의 아이콘으로 섞어 쓰지 않는다.
- Azure 팩에도 `Power-Platform` 아이콘이 있다. 권장: Power Platform 제품은 `powerplatform` 팩을 쓴다.
- `site recovery`, `outlook`, `github`, `office`로 검색하면 6개 팩 모두에서 결과가 없다. `teams`와 `sharepoint`로 검색하면 M365 팩의 일반 기호만 나온다.

### Microsoft Entra

- 흑백 아이콘의 폴더는 `Microsoft Entra BW icons SVG`다.
- 흑백 폴더의 `Microsoft Entra (product family)`와 색 폴더의 `Microsoft Entra Product Family`는 대소문자와 기호를 무시하면 이름이 같다. 따라서 `entra:Microsoft Entra (product family)`처럼 폴더 없이 쓰면 기본 폴더의 색 아이콘이 선택된다.

### Power Platform

- `CopilotStudio`와 `Agent365`는 아이콘 폴더 최상위에 있다. 나머지 6개는 `Power Platform` 폴더에 있다. 모두 폴더 없이 쓸 수 있다.
- Power BI 아이콘은 이 팩에 없다. `fabric:power_bi`를 쓴다.

### Microsoft 365

| 폴더 | 아이콘 수 | 색 구분 |
| --- | --- | --- |
| `Microsoft Blue/48x48 Dark Blue Icon` | 155 | 폴더(기본 폴더) |
| `Microsoft Blue/48x48 Grey & Blue Icon` | 155 | 폴더 |
| `Microsoft Blue/48x48 Light Blue Icon` | 155 | 폴더 |
| `Teams Purple/48x48 Dark Purple Icon` | 145 | 폴더 |
| `Teams Purple/48x48 Grey & Purple Icon` | 145 | 폴더 |
| `Teams Purple/48x48 Light Purple Icon` | 145 | 폴더 |
| `Teams Purple` | 3 | 이름 끝 |
| `Microsoft Purple/48x48 SVG Icons` | 7 | 이름 끝 |
| `Planner Green/48x48 SVG Icons` | 38 | 이름 끝 |
| `Project Green/48x48 SVG Icons` | 12 | 이름 끝 |
| `SharePoint Teal/48x48 SVG Icon` | 3 | 이름 끝 |

- 색 구분이 "폴더"인 6개 폴더는 폴더로 색을 나눈다. 아이콘 이름에는 대부분 색 접미사가 없다.
- 색 구분이 "이름 끝"인 폴더는 이름 끝의 `_Dark`, `_Gray`, `_Light`로 색을 나눈다. 폴더 이름의 철자는 `Grey`이고 접미사의 철자는 `_Gray`다.
- 예외가 있다. `Planner Green/48x48 SVG Icons` 폴더의 `Deploy`와 `Window Edit`에는 색 접미사가 없다. `Microsoft Purple/48x48 SVG Icons` 폴더의 Building 아이콘은 `Building_Gray`만 있다.
- 예: `m365:Teams Purple/48x48 Dark Purple Icon/People Team`, `m365:Teams Purple/Building People_Teams_Dark`.

### Dynamics 365

- 앱 아이콘 15개는 `Dynamics 365 App Icons` 폴더에 있다. 제품군 아이콘은 `Dynamics 365 Product Family Icons` 폴더에 있다. 모두 폴더 없이 쓸 수 있다.
- Dynamics 365 전용 [그룹 종류](spec-format.md#그룹-종류)는 없다. 경계가 필요하면 `kind: plain`을 쓴다.

## 대체 아이콘

대체 아이콘은 공식 아이콘이 없는 Microsoft 제품이나 서비스를 다른 아이콘으로 나타낸 것이다. 다음 규칙을 따른다.

1. 필수: 대체 아이콘을 쓰기 전에 `--pack` 없이 6개 팩을 모두 검색한다.
2. 권장: 같은 제품군의 일반 기호를 쓰고, 레이블에 실제 제품 이름을 쓴다.
3. 필수: 대체 아이콘을 쓴 노드, 그룹, 밴드 항목에 `stand_in: true`를 지정한다. 이 값은 그림에 나타나지 않고 `icon-provenance.json`에 기록된다.
4. 필수: Microsoft 제품이 아닌 시스템이나 사내 시스템에 Microsoft 제품 아이콘을 쓰지 않는다.
5. 필수: 결과물을 전달할 때 대체 아이콘 목록을 밝힌다. [PNG 점검 목록](style-guide.md#png-점검-목록)의 8번 항목으로 확인한다.

Teams 제품 아이콘은 없으므로 Teams 색의 일반 기호를 쓴다.

```yaml
- {id: teams, at: [300, 400], icon: "m365:Teams Purple/48x48 Dark Purple Icon/People Team",
   title: Microsoft Teams, detail: 협업, stand_in: true}
```

외부 시스템은 대체 아이콘이 아니다. 외부 시스템은 `icon`이 없는 `card` 노드나 M365 팩의 일반 기호로 그리고, `stand_in`을 지정하지 않는다. Microsoft Learn 다이어그램 지침도 외부 시스템에는 제품 로고 대신 일반 도형을 쓰라고 권한다("Rely on generic shapes for external systems rather than product logos").

## icon-provenance.json

렌더러는 사용한 아이콘마다 출처 기록 하나를 `icon-provenance.json`에 쓴다.

| 필드 | 내용 |
| --- | --- |
| `key` | 사양에 쓴 아이콘 키 |
| `pack`, `pack_title` | 팩 이름과 `packs.json`의 팩 제목 |
| `source_page` | 출처 문서 URL |
| `download` | 내려받기 URL |
| `terms` | 이용 조건 URL이나 설명 |
| `archive_sha256` | 캐시에 있는 실제 압축 파일의 SHA-256 |
| `member` | 압축 파일 안의 SVG 경로 |
| `svg_sha256` | BOM을 제거한 SVG의 SHA-256 |
| `stand_in` | 한 곳이라도 `stand_in: true`로 쓰면 `true`다. |
| `used_by` | 이 아이콘을 쓴 노드, 그룹, 밴드 항목의 ID 목록 |

- 기록은 키 문자열마다 하나다. 같은 아이콘을 다른 키로 쓰면 기록이 두 개 생긴다. 권장: 한 사양에서는 같은 아이콘을 같은 키로 쓴다.
- 기록은 `key` 순서로 정렬한다.

## 이용 조건

Azure 아이콘의 이용 조건은 다음과 같다.

> Microsoft permits the use of these icons in architectural diagrams, training materials, or documentation. You can copy, distribute, and display the icons only for the permitted use unless granted explicit permission by Microsoft. Microsoft reserves all other rights.

Azure 아이콘 지침과 렌더러 동작은 다음과 같이 대응한다.

| 지침 | 렌더러 동작 |
| --- | --- |
| "Use the icon to illustrate how products can work together." | 아이콘을 흐름과 범위 경계 안에 배치한다. |
| "In diagrams, we recommend including the product name somewhere close to the icon." | 아이콘 노드와 밴드 항목은 아이콘 가까이에 `title`을 그린다. |
| "Use the icons as they would appear within Azure." | 아이콘 그림을 바꾸지 않는다. 색을 바꾸거나 필터를 적용하는 기능이 없다. |
| "Don't crop, flip, or rotate icons." | 자르기, 뒤집기, 회전 기능이 없다. |
| "Don't distort or change icon shape in any way." | 정사각형 영역에 비율을 유지해 넣는다. draw.io 파일에서도 비율을 고정한다. |
| "Don't use Microsoft product icons to represent your product or service." | [대체 아이콘](#대체-아이콘)의 4번 규칙으로 금지한다. |

- Fabric 지침은 아이콘 가까이에 제품, 경험, 항목 이름을 넣으라고 권한다("including a label that contains the product, experience, or item name somewhere close to the icon").
- Microsoft Entra 지침에는 "Don't use Microsoft product icons in Marketing communications."가 있다. 권장: 마케팅 자료에 쓰기 전에 팩마다 이용 조건을 확인한다.
- Fabric npm 패키지의 설명은 "A publicly available collection of SVG icons for use in Microsoft Fabric platform extension development."다. 다이어그램의 아이콘 사용 지침은 [Fabric 아이콘 지침](https://learn.microsoft.com/fabric/fundamentals/icons)을 따른다.

압축 파일에는 다음 이용 조건 파일이 있다.

| 팩 | 파일 |
| --- | --- |
| `azure` | `Azure_Icons_FAQ.pdf`, `Microsoft_Terms_of_Use.pdf` |
| `fabric` | `package/package.json`의 `"license": "MIT"` |
| `powerplatform` | `Power_Platform_Icons_FAQ.pdf`, `CELA_Licenses_Public_Use_Icons.pdf` |
| `entra` | `Microsoft Terms of Use.docx` |
| `m365` | 없다. 출처 문서를 확인한다. |
| `dynamics365` | `Dynamics 365_Icons_FAQ.pdf`, `CELA_Licenses_Public_Use_Icons.pdf` |
