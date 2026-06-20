"""
TFT Champion App의 화면 흐름과 이벤트 처리를 담당하는 클래스.

main.py가 너무 길어지는 것을 막기 위해 다음 역할을 이 파일로 분리하였다.
- Flet 화면 구성
- 챔피언 목록 조회
- 코스트별/특성별 보기 전환
- 조합판 추가/삭제
- 활성 특성 패널 갱신
- hover 상세정보 출력
- 데이터 동기화 버튼 처리
"""

import flet as ft

from service.data_dragon_service import sync_tft_data
from service.champion_service import get_champion_list, get_champion_detail

from ui.constants import (
    COLOR_BACKGROUND,
    COLOR_PANEL,
    COLOR_PANEL_DARK,
    COLOR_BORDER,
    COLOR_TEXT,
    COLOR_SUB_TEXT,
    COLOR_MUTED,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_ERROR,
    get_cost_color,
)
from ui.champion_card import (
    make_empty_board_slot,
    make_board_champion_card,
    make_champion_icon_card,
    make_detail_champion_card,
)
from ui.sections import (
    make_cost_section,
    make_trait_section,
)


class TFTChampionApp:
    """
    Flet 기반 TFT 챔피언 조회 앱.
    화면 상태와 이벤트 함수를 하나의 클래스로 묶어 관리한다.
    """

    def __init__(self, page: ft.Page):
        self.page = page

        # 조합판에 선택된 챔피언 목록
        self.selected_champions = []

        # 챔피언 상세 Join 결과 캐시
        # 같은 챔피언에 대해 매번 DB를 조회하지 않기 위해 사용한다.
        self.champion_detail_cache = {}

        # 챔피언 목록 보기 모드: "cost" 또는 "trait"
        self.view_mode = "cost"

        self._init_page()
        self._init_controls()

    def _init_page(self):
        """
        Flet 페이지 기본 설정.
        """
        self.page.title = "TFT Champion App"
        self.page.bgcolor = COLOR_BACKGROUND
        self.page.padding = 20
        self.page.scroll = ft.ScrollMode.AUTO

    def _init_controls(self):
        """
        여러 메서드에서 공통으로 접근해야 하는 Flet 컨트롤들을 생성한다.
        """
        self.search_field = ft.TextField(
            label="챔피언 이름 검색",
            hint_text="예: 아리, 가렌",
            width=300,
            border_color="#374151",
            color=COLOR_TEXT,
            label_style=ft.TextStyle(color=COLOR_SUB_TEXT),
            hint_style=ft.TextStyle(color=COLOR_MUTED),
        )

        self.status_text = ft.Text(
            "",
            size=13,
            color=COLOR_SUB_TEXT,
        )

        self.trait_panel = ft.Column(
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            height=260,
        )

        self.board_grid = ft.GridView(
            expand=False,
            runs_count=5,
            max_extent=115,
            child_aspect_ratio=1,
            spacing=8,
            run_spacing=8,
            height=230,
        )

        self.champion_sections = ft.Column(
            spacing=16,
        )

        self.hover_detail_title = ft.Text(
            "챔피언 상세정보",
            size=18,
            weight=ft.FontWeight.BOLD,
            color=COLOR_TEXT,
        )

        self.hover_detail_card_area = ft.Container(
            width=105,
            height=105,
            content=ft.Text(
                "카드",
                size=11,
                color=COLOR_MUTED,
            ),
        )

        self.hover_detail_text = ft.Text(
            "챔피언 카드에 마우스를 올리면 챔피언 상세정보가 표시됩니다.",
            size=12,
            color=COLOR_SUB_TEXT,
            selectable=True,
        )

    def build(self):
        """
        전체 화면을 조립하고 초기 데이터를 불러온다.
        """
        self.page.add(
            self._make_top_bar(),
            ft.Container(height=16),
            self._make_composition_area(),
            ft.Container(height=16),
            self._make_hover_detail_area(),
            ft.Container(height=16),
            ft.Text(
                "챔피언 목록",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=COLOR_TEXT,
            ),
            ft.Text(
                "코스트별 보기와 특성별 보기를 전환할 수 있으며, 챔피언 아이콘을 클릭하면 조합판에 추가됩니다.",
                size=12,
                color=COLOR_SUB_TEXT,
            ),
            ft.Container(height=8),
            self.champion_sections,
        )

        self.render_team_board()
        self.render_trait_panel()
        self.load_champions()

    # ------------------------------------------------------------------
    # 데이터 조회 관련 함수
    # ------------------------------------------------------------------

    def get_champion_traits(self, champion_id):
        """
        챔피언 ID를 기준으로 상세 Join 결과를 조회한다.
        내부적으로 ChampionRepository의 LEFT JOIN 결과를 사용한다.
        """
        if champion_id in self.champion_detail_cache:
            return self.champion_detail_cache[champion_id]

        rows = get_champion_detail(champion_id)
        self.champion_detail_cache[champion_id] = rows
        return rows

    def _get_trait_names(self, champion_id):
        """
        챔피언이 가진 특성 이름 목록을 중복 없이 반환한다.
        """
        rows = self.get_champion_traits(champion_id)
        trait_names = []

        for row in rows:
            trait_id = row[4]
            trait_name = row[5]

            if trait_id is None or trait_name is None:
                continue

            if trait_name not in trait_names:
                trait_names.append(trait_name)

        return trait_names

    # ------------------------------------------------------------------
    # 상단 영역 / 상세정보 영역 / 조합판 영역 생성
    # ------------------------------------------------------------------

    def _make_top_bar(self):
        """
        앱 제목, 검색창, 기능 버튼 영역을 생성한다.
        """
        return ft.Container(
            padding=16,
            bgcolor=COLOR_PANEL,
            border_radius=12,
            border=ft.Border.all(1, COLOR_BORDER),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Text(
                        "TFT Champion Archive",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_TEXT,
                    ),
                    ft.Text(
                        "롤토체스 현재 시즌 챔피언을 조회하고 조합판에 추가하여 활성 특성을 확인합니다.",
                        size=13,
                        color=COLOR_SUB_TEXT,
                    ),
                    ft.Row(
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            self.search_field,
                            ft.Button(
                                content=ft.Text("검색"),
                                on_click=self.load_champions,
                            ),
                            ft.Button(
                                content=ft.Text("코스트별 보기"),
                                on_click=self.set_cost_mode,
                            ),
                            ft.Button(
                                content=ft.Text("특성별 보기"),
                                on_click=self.set_trait_mode,
                            ),
                            ft.Button(
                                content=ft.Text("데이터 동기화"),
                                on_click=self.sync_data,
                            ),
                            ft.Button(
                                content=ft.Text("조합판 초기화"),
                                on_click=self.reset_team,
                            ),
                        ],
                    ),
                    self.status_text,
                ],
            ),
        )

    def _make_composition_area(self):
        """
        왼쪽 활성 특성 패널과 오른쪽 조합판 영역을 생성한다.
        """
        return ft.Container(
            padding=12,
            bgcolor=COLOR_PANEL,
            border_radius=12,
            border=ft.Border.all(1, COLOR_BORDER),
            content=ft.Row(
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(
                        width=210,
                        height=330,
                        padding=10,
                        bgcolor=COLOR_PANEL_DARK,
                        border_radius=10,
                        border=ft.Border.all(1, COLOR_BORDER),
                        content=ft.Column(
                            spacing=10,
                            controls=[
                                ft.Text(
                                    "활성 특성",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=COLOR_TEXT,
                                ),
                                self.trait_panel,
                            ],
                        ),
                    ),
                    ft.Container(
                        expand=True,
                        height=330,
                        padding=10,
                        bgcolor=COLOR_PANEL_DARK,
                        border_radius=10,
                        border=ft.Border.all(1, COLOR_BORDER),
                        content=ft.Column(
                            spacing=10,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(
                                            "조합판",
                                            size=18,
                                            weight=ft.FontWeight.BOLD,
                                            color=COLOR_TEXT,
                                        ),
                                        ft.Text(
                                            "챔피언 클릭: 추가 / 조합판 클릭: 제거",
                                            size=12,
                                            color=COLOR_SUB_TEXT,
                                        ),
                                    ],
                                ),
                                self.board_grid,
                            ],
                        ),
                    ),
                ],
            ),
        )

    def _make_hover_detail_area(self):
        """
        챔피언 카드에 마우스를 올렸을 때 표시되는 상세정보 영역을 생성한다.
        """
        return ft.Container(
            padding=12,
            bgcolor=COLOR_PANEL,
            border_radius=10,
            border=ft.Border.all(1, COLOR_BORDER),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Column(
                        spacing=8,
                        expand=True,
                        controls=[
                            self.hover_detail_title,
                            self.hover_detail_text,
                        ],
                    ),
                    ft.Container(
                        width=100,
                        height=100,
                        bgcolor=None,
                        border_radius=8,
                        content=ft.Column(
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                self.hover_detail_card_area,
                            ],
                        ),
                    ),
                ],
            ),
        )

    # ------------------------------------------------------------------
    # 상세정보 / 조합판 / 활성 특성 패널 갱신
    # ------------------------------------------------------------------

    def show_hover_detail(self, e, champion):
        """
        챔피언 카드 hover 시 상세정보 영역을 갱신한다.
        """
        if str(e.data).lower() != "true":
            return

        champion_id, name, tier, image_url, set_no = champion
        trait_names = self._get_trait_names(champion_id)

        self.hover_detail_title.value = name
        self.hover_detail_card_area.content = make_detail_champion_card(champion)

        self.hover_detail_text.value = (
            f"챔피언: {name}\n"
            f"코스트: {tier}코스트\n"
            f"세트 번호: {set_no}\n"
            f"보유 특성 수: {len(trait_names)}개\n"
            f"특성: {', '.join(trait_names) if trait_names else '없음'}"
        )

        self.page.update()

    def render_trait_panel(self):
        """
        조합판에 선택된 챔피언들을 기준으로 특성 개수를 계산하고,
        왼쪽 활성 특성 패널을 갱신한다.
        """
        self.trait_panel.controls.clear()

        trait_count = {}
        trait_images = {}

        for champion in self.selected_champions:
            champion_id = champion[0]
            rows = self.get_champion_traits(champion_id)

            for row in rows:
                trait_id = row[4]
                trait_name = row[5]
                trait_image_url = row[6]

                if trait_id is None:
                    continue

                if trait_id not in trait_count:
                    trait_count[trait_id] = {
                        "name": trait_name,
                        "count": 0,
                    }
                    trait_images[trait_id] = trait_image_url

                trait_count[trait_id]["count"] += 1

        if not trait_count:
            self.trait_panel.controls.append(
                ft.Text(
                    "챔피언을 선택하면 활성 특성이 표시됩니다.",
                    size=12,
                    color=COLOR_MUTED,
                )
            )
        else:
            sorted_traits = sorted(
                trait_count.items(),
                key=lambda item: (-item[1]["count"], item[1]["name"]),
            )

            for trait_id, info in sorted_traits:
                self.trait_panel.controls.append(
                    ft.Container(
                        padding=8,
                        bgcolor=COLOR_PANEL,
                        border_radius=8,
                        border=ft.Border.all(1, COLOR_BORDER),
                        content=ft.Row(
                            spacing=8,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Image(
                                    src=trait_images.get(trait_id),
                                    width=28,
                                    height=28,
                                    fit=ft.BoxFit.CONTAIN,
                                )
                                if trait_images.get(trait_id)
                                else ft.Container(width=28, height=28),
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text(
                                            info["name"],
                                            size=13,
                                            color=COLOR_TEXT,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            f"{info['count']}명 보유",
                                            size=11,
                                            color=COLOR_SUB_TEXT,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    )
                )

        self.page.update()

    def render_team_board(self):
        """
        조합판에 선택된 챔피언들을 다시 그린다.
        """
        self.board_grid.controls.clear()

        if not self.selected_champions:
            self.board_grid.controls.append(make_empty_board_slot())
        else:
            for champion in self.selected_champions:
                self.board_grid.controls.append(
                    make_board_champion_card(
                        champion=champion,
                        on_click=self.remove_champion_from_team,
                        on_hover=self.show_hover_detail,
                    )
                )

        self.page.update()

    # ------------------------------------------------------------------
    # 사용자 이벤트 처리
    # ------------------------------------------------------------------

    def add_champion_to_team(self, champion):
        """
        챔피언 목록에서 클릭한 챔피언을 조합판에 추가한다.
        """
        champion_id = champion[0]

        for selected in self.selected_champions:
            if selected[0] == champion_id:
                self.status_text.value = "이미 조합판에 추가된 챔피언입니다."
                self.status_text.color = COLOR_WARNING
                self.page.update()
                return

        if len(self.selected_champions) >= 10:
            self.status_text.value = "조합판에는 최대 10명까지 추가할 수 있습니다."
            self.status_text.color = COLOR_WARNING
            self.page.update()
            return

        self.selected_champions.append(champion)

        self.status_text.value = f"{champion[1]} 챔피언을 조합판에 추가했습니다."
        self.status_text.color = COLOR_SUCCESS

        self.render_team_board()
        self.render_trait_panel()

    def remove_champion_from_team(self, champion_id):
        """
        조합판에서 선택된 챔피언을 제거한다.
        """
        self.selected_champions[:] = [
            champion
            for champion in self.selected_champions
            if champion[0] != champion_id
        ]

        self.status_text.value = "챔피언을 조합판에서 제거했습니다."
        self.status_text.color = COLOR_SUB_TEXT

        self.render_team_board()
        self.render_trait_panel()

    def reset_team(self, e=None):
        """
        조합판을 초기화한다.
        """
        self.selected_champions.clear()

        self.status_text.value = "조합판을 초기화했습니다."
        self.status_text.color = COLOR_SUB_TEXT

        self.render_team_board()
        self.render_trait_panel()

    def set_cost_mode(self, e=None):
        """
        챔피언 목록을 코스트별 보기로 변경한다.
        """
        self.view_mode = "cost"
        self.status_text.value = "코스트별 보기로 변경했습니다."
        self.status_text.color = COLOR_SUB_TEXT
        self.load_champions()

    def set_trait_mode(self, e=None):
        """
        챔피언 목록을 특성별 보기로 변경한다.
        """
        self.view_mode = "trait"
        self.status_text.value = "특성별 보기로 변경했습니다."
        self.status_text.color = COLOR_SUB_TEXT
        self.load_champions()

    # ------------------------------------------------------------------
    # 챔피언 목록 조회 / 화면 출력
    # ------------------------------------------------------------------

    def _make_champion_card(self, champion):
        """
        목록용 챔피언 카드를 생성한다.
        """
        return make_champion_icon_card(
            champion=champion,
            on_click=self.add_champion_to_team,
            on_hover=self.show_hover_detail,
        )

    def load_champions(self, e=None):
        """
        검색어와 보기 모드에 따라 챔피언 목록을 다시 불러온다.
        """
        self.champion_sections.controls.clear()

        keyword = self.search_field.value or ""
        champions = get_champion_list(keyword)

        if not champions:
            self.champion_sections.controls.append(
                ft.Text(
                    "챔피언 데이터가 없습니다. 데이터 동기화를 먼저 실행하세요.",
                    color=COLOR_ERROR,
                    size=14,
                )
            )
            self.page.update()
            return

        if self.view_mode == "cost":
            self._render_champions_by_cost(champions)
            self.status_text.value = f"챔피언 {len(champions)}명을 코스트별로 불러왔습니다."
        else:
            self._render_champions_by_trait(champions)
            self.status_text.value = f"챔피언 {len(champions)}명을 특성별로 불러왔습니다."

        self.status_text.color = COLOR_SUB_TEXT
        self.page.update()

    def _render_champions_by_cost(self, champions):
        """
        champions 테이블의 tier 값을 기준으로 챔피언을 분류한다.
        """
        champions_by_cost = {}

        for champion in champions:
            tier = champion[2]

            if tier not in champions_by_cost:
                champions_by_cost[tier] = []

            champions_by_cost[tier].append(champion)

        for tier in sorted(champions_by_cost.keys()):
            self.champion_sections.controls.append(
                make_cost_section(
                    tier=tier,
                    champions=champions_by_cost[tier],
                    card_factory=self._make_champion_card,
                )
            )

    def _render_champions_by_trait(self, champions):
        """
        champions, champion_traits, traits Join 결과를 이용하여
        챔피언을 특성별로 분류한다.
        """
        champions_by_trait = {}

        for champion in champions:
            champion_id = champion[0]
            rows = self.get_champion_traits(champion_id)

            for row in rows:
                trait_id = row[4]
                trait_name = row[5]

                if trait_id is None or trait_name is None:
                    continue

                if trait_name not in champions_by_trait:
                    champions_by_trait[trait_name] = []

                # 같은 챔피언이 같은 특성 섹션에 중복으로 들어가지 않도록 방지한다.
                already_added = False

                for saved_champion in champions_by_trait[trait_name]:
                    if saved_champion[0] == champion_id:
                        already_added = True
                        break

                if not already_added:
                    champions_by_trait[trait_name].append(champion)

        if not champions_by_trait:
            self.champion_sections.controls.append(
                ft.Text(
                    "특성별 챔피언 데이터를 불러오지 못했습니다.",
                    color=COLOR_ERROR,
                    size=14,
                )
            )
            return

        for trait_name in sorted(champions_by_trait.keys()):
            self.champion_sections.controls.append(
                make_trait_section(
                    trait_name=trait_name,
                    champions=champions_by_trait[trait_name],
                    card_factory=self._make_champion_card,
                )
            )

    # ------------------------------------------------------------------
    # 외부 데이터 동기화
    # ------------------------------------------------------------------

    def sync_data(self, e=None):
        """
        Data Dragon과 Community Dragon에서 데이터를 가져와 DuckDB에 저장한다.
        """
        self.status_text.value = "데이터 동기화 중입니다..."
        self.status_text.color = COLOR_SUB_TEXT
        self.page.update()

        try:
            set_no = sync_tft_data()

            # 동기화 후 기존 캐시와 조합판을 초기화한다.
            self.champion_detail_cache.clear()
            self.selected_champions.clear()

            self.status_text.value = f"데이터 동기화 완료: TFT Set {set_no}"
            self.status_text.color = COLOR_SUCCESS

            self.render_team_board()
            self.render_trait_panel()
            self.load_champions()

        except Exception as ex:
            self.status_text.value = f"데이터 동기화 실패: {ex}"
            self.status_text.color = COLOR_ERROR
            self.page.update()
