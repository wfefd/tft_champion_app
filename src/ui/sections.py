"""
챔피언 목록 섹션 UI 모음.

- 코스트별 섹션
- 특성별 섹션

섹션은 챔피언 카드를 직접 만들지 않고 card_factory를 받아서 사용한다.
"""

import flet as ft

from ui.constants import (
    COLOR_SECTION,
    COLOR_SECTION_HEADER,
    COLOR_TEXT,
    COLOR_SUB_TEXT,
    get_cost_color,
    get_cost_label,
)


def _make_champion_grid(champions, card_factory):
    """
    챔피언 카드들을 GridView로 배치한다.
    공통 슬롯 크기인 105 x 105에 맞춰 그리드 크기를 설정한다.
    """

    row_count = (len(champions) + 5) // 6
    grid_height = max(115, row_count * 115)

    grid = ft.GridView(
        expand=False,
        runs_count=6,
        max_extent=115,
        child_aspect_ratio=1,
        spacing=8,
        run_spacing=8,
        height=grid_height,
    )

    for champion in champions:
        grid.controls.append(card_factory(champion))

    return grid


def make_cost_section(tier, champions, card_factory):
    """
    코스트별 챔피언 목록 섹션을 생성한다.
    """

    return ft.Container(
        padding=10,
        bgcolor=COLOR_SECTION,
        border_radius=4,
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Container(
                    height=36,
                    padding=ft.Padding(left=8, top=4, right=8, bottom=4),
                    bgcolor=COLOR_SECTION_HEADER,
                    content=ft.Row(
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=12,
                                height=12,
                                border_radius=20,
                                bgcolor=get_cost_color(tier),
                            ),
                            ft.Text(
                                get_cost_label(tier),
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_TEXT,
                            ),
                            ft.Text(
                                f"{len(champions)}명",
                                size=12,
                                color=COLOR_SUB_TEXT,
                            ),
                        ],
                    ),
                ),
                _make_champion_grid(champions, card_factory),
            ],
        ),
    )


def make_trait_section(trait_name, champions, card_factory):
    """
    특성별 챔피언 목록 섹션을 생성한다.
    """

    return ft.Container(
        padding=10,
        bgcolor=COLOR_SECTION,
        border_radius=4,
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Container(
                    height=36,
                    padding=ft.Padding(left=8, top=4, right=8, bottom=4),
                    bgcolor=COLOR_SECTION_HEADER,
                    content=ft.Row(
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                trait_name,
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_TEXT,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                f"{len(champions)}명",
                                size=12,
                                color=COLOR_SUB_TEXT,
                                max_lines=1,
                            ),
                        ],
                    ),
                ),
                _make_champion_grid(champions, card_factory),
            ],
        ),
    )