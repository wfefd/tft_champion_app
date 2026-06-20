# TFT Champion App

롤토체스 현재 시즌 챔피언 정보를 조회하고, 챔피언을 조합판에 추가하여 활성 특성을 확인할 수 있는 Flet + DuckDB 기반 GUI 애플리케이션입니다.

## 1. 프로젝트 개요

본 프로젝트는 Riot Data Dragon과 Community Dragon에서 롤토체스 챔피언, 특성, 챔피언-특성 관계 데이터를 가져와 DuckDB에 저장합니다.

사용자는 Flet GUI를 통해 다음 기능을 사용할 수 있습니다.

- 현재 시즌 챔피언 목록 조회
- 챔피언 이름 검색
- 코스트별 챔피언 목록 조회
- 특성별 챔피언 목록 조회
- 챔피언 조합판 추가 및 제거
- 선택된 챔피언들의 활성 특성 확인
- 챔피언 카드 hover 시 상세정보 확인
- 외부 데이터 동기화

## 2. 사용 기술

- Python
- Flet
- DuckDB
- Riot Data Dragon
- Community Dragon

## 3. 프로젝트 구조

```text
tft_champion_app/
├─ src/
│  ├─ main.py
│  ├─ config.py
│  ├─ db/
│  │  ├─ connection.py
│  │  └─ schema.py
│  ├─ repository/
│  │  ├─ champion_repository.py
│  │  ├─ champion_trait_repository.py
│  │  └─ trait_repository.py
│  ├─ service/
│  │  ├─ champion_service.py
│  │  ├─ data_dragon_service.py
│  │  ├─ tft_api_client.py
│  │  └─ tft_data_utils.py
│  └─ ui/
│     ├─ constants.py
│     ├─ champion_card.py
│     ├─ sections.py
│     └─ tft_app.py
├─ storage/
│  └─ data/
│     └─ tft.duckdb
├─ requirements.txt
└─ README.md
```

## 4. 실행 방법

### 4.1 저장소 내려받기

```bash
git clone https://github.com/wfefd/tft_champion_app.git
cd tft_champion_app
```

### 4.2 가상환경 생성

Windows PowerShell 기준입니다.

```powershell
python -m venv .venv
.venv\Scripts\activate
```

macOS 또는 Linux에서는 다음 명령어를 사용합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4.3 의존성 설치

```bash
pip install -r requirements.txt
```

### 4.4 프로그램 실행

```bash
flet run src/main.py
```

## 5. 최초 실행 후 해야 할 일

프로그램을 처음 실행하면 DuckDB 데이터베이스 파일이 자동으로 생성됩니다.

앱 실행 후 상단의 **데이터 동기화** 버튼을 클릭하면 외부 API에서 현재 시즌 챔피언, 특성, 챔피언-특성 관계 데이터를 가져와 DuckDB에 저장합니다.

데이터 동기화 후 챔피언 목록, 검색, 조합판 기능을 사용할 수 있습니다.

## 6. 주요 기능 설명

### 챔피언 목록 조회

DuckDB에 저장된 챔피언 데이터를 불러와 화면에 출력합니다.

### 챔피언 이름 검색

검색창에 챔피언 이름을 입력하면 해당 이름을 포함하는 챔피언만 조회합니다.

### 코스트별 보기

챔피언의 `tier` 값을 기준으로 1코스트, 2코스트, 3코스트, 4코스트, 5코스트로 나누어 출력합니다.

### 특성별 보기

`champions`, `champion_traits`, `traits` 테이블을 Join한 결과를 기준으로 각 특성에 해당하는 챔피언을 출력합니다.

### 조합판

챔피언 카드를 클릭하면 조합판에 챔피언이 추가됩니다.  
조합판에 추가된 챔피언 카드를 클릭하면 해당 챔피언이 제거됩니다.

### 활성 특성 패널

조합판에 추가된 챔피언들의 특성을 계산하여 현재 보유 중인 특성 이름과 개수를 출력합니다.

### 챔피언 상세정보

챔피언 카드에 마우스를 올리면 챔피언 이름, 코스트, 세트 번호, 보유 특성 수, 특성 이름을 확인할 수 있습니다.

## 7. 데이터베이스 테이블

본 프로젝트는 다음 세 개의 테이블을 사용합니다.

### champions

챔피언 기본 정보를 저장합니다.

- champion_id
- name
- tier
- image_url
- set_no

### traits

특성 정보를 저장합니다.

- trait_id
- name
- image_url
- set_no

### champion_traits

챔피언과 특성의 다대다 관계를 저장합니다.

- champion_id
- trait_id

## 8. 과제 제한요소 충족 여부

| 제한요소 | 충족 내용 |
|---|---|
| Table 3개 이상 생성 | champions, traits, champion_traits |
| Entity 2개, Relationship 1개 | Entity: champions, traits / Relationship: champion_traits |
| 데이터 삽입 | Data Dragon, Community Dragon 데이터를 DuckDB에 삽입 |
| Join 필수 | champions, champion_traits, traits 세 테이블 LEFT JOIN |
| Flet GUI 구현 | 챔피언 목록, 검색, 조합판, 활성 특성 패널 구현 |
| DuckDB 접근 | Repository 계층에서 DuckDB SQL 실행 |
| Image 저장 및 출력 | DB에 image_url 저장 후 Flet Image로 출력 |
| 수업 내용 활용 | PK, FK, 다대다 관계, 정규화, BCNF, Join 활용 |
| GitHub Public Repository | GitHub 저장소 링크 첨부 |

## 9. 실행 시 주의사항

- 인터넷 연결이 필요합니다.
- 최초 실행 후 반드시 **데이터 동기화** 버튼을 클릭해야 합니다.
- `storage/data/tft.duckdb` 파일은 실행 중 자동 생성됩니다.
- Python 가상환경을 활성화한 뒤 실행하는 것을 권장합니다.

## 10. GitHub Repository

https://github.com/wfefd/tft_champion_app
