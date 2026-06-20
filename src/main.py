import flet as ft

from db.schema import create_tables
from ui.tft_app import TFTChampionApp


def main(page: ft.Page):
    """
    Flet 앱의 시작점이다.
    - DB 테이블을 생성한다.
    - 화면 전체를 담당하는 TFTChampionApp 객체를 실행한다.
    """
    create_tables()

    app = TFTChampionApp(page)
    app.build()


ft.run(main)
