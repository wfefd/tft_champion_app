"""
챔피언 카드 UI 컴포넌트 모음.

조합판, 챔피언 목록, 상세정보 영역에서 같은 카드 디자인을 재사용한다.
카드 크기와 이미지 위치는 make_champion_card() 한 곳에서만 관리한다.
"""

import flet as ft

from ui.constants import (
    COLOR_PANEL,
    COLOR_BORDER,
    COLOR_TEXT,
    COLOR_MUTED,
    get_cost_color,
)


CARD_SIZE = 95
INNER_SIZE = 89

def make_card_slot(card):
    """
    챔피언 카드를 감싸는 공통 슬롯이다.

    GridView, 상세정보 영역, 조합판 등에서 카드가 같은 크기와 위치로 보이도록 한다.
    """

    return ft.Container(
        width=105,
        height=105,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                card,
            ],
        ),
    )

def make_empty_board_slot():
    """
    조합판에 챔피언이 없을 때 표시하는 빈 슬롯을 생성한다.
    """

    return ft.Container(
        width=CARD_SIZE,
        height=CARD_SIZE,
        bgcolor=COLOR_PANEL,
        border_radius=10,
        border=ft.Border.all(1, COLOR_BORDER),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("+", size=28, color=COLOR_MUTED),
                ft.Text("선택", size=11, color=COLOR_MUTED),
            ],
        ),
    )


def make_champion_card(champion, on_click=None, on_hover=None):
    """
    공통 챔피언 카드이다.

    이 함수가 조합판, 챔피언 목록, 상세정보 영역에서 모두 사용된다.
    따라서 카드 디자인을 수정할 때는 이 함수만 수정하면 된다.
    """

    champion_id, name, tier, image_url, set_no = champion

    return ft.Container(
        width=CARD_SIZE,
        height=CARD_SIZE,
        bgcolor=COLOR_PANEL,
        border_radius=16,
        border=ft.Border.all(2, get_cost_color(tier)),
        padding=0.2,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        on_click=(lambda e, champ=champion: on_click(champ)) if on_click else None,
        on_hover=(lambda e, champ=champion: on_hover(e, champ)) if on_hover else None,
        content=ft.Container(
            width=INNER_SIZE,
            height=INNER_SIZE,
            border_radius=13,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Stack(
                width=INNER_SIZE,
                height=INNER_SIZE,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                controls=[
                    ft.Image(
                        src=image_url,
                        width=118,
                        height=90,
                        fit=ft.BoxFit.COVER,
                        left=-27,
                        top=1,
                    ),
                    ft.Container(
                        width=INNER_SIZE,
                        height=20,
                        left=2,
                        top=65,
                        bgcolor=None,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text(
                                    name,
                                    size=10,
                                    color=COLOR_TEXT,
                                    weight=ft.FontWeight.BOLD,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    text_align=ft.TextAlign.CENTER,
                                )
                            ],
                        ),
                    ),
                ],
            ),
        ),
    )


def make_board_champion_card(champion, on_click, on_hover):
    """
    조합판에 표시되는 챔피언 카드이다.
    클릭하면 조합판에서 제거된다.
    """

    champion_id = champion[0]

    card = make_champion_card(
        champion=champion,
        on_click=lambda champ: on_click(champion_id),
        on_hover=on_hover,
    )

    return make_card_slot(card)

def make_champion_icon_card(champion, on_click, on_hover):
    """
    챔피언 목록에 표시되는 카드이다.
    조합판과 같은 공통 카드 디자인을 사용한다.
    """

    card = make_champion_card(
        champion=champion,
        on_click=on_click,
        on_hover=on_hover,
    )

    return make_card_slot(card)

def make_detail_champion_card(champion):
    """
    상세정보 영역에 표시되는 카드이다.
    클릭/hover 이벤트 없이 공통 카드 디자인만 사용한다.
    """

    card = make_champion_card(
        champion=champion,
    )

    return make_card_slot(card)