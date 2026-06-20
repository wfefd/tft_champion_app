"""
UI에서 공통으로 사용하는 색상, 크기, 라벨 관련 함수 모음.
여러 파일에서 같은 값을 반복하지 않기 위해 분리하였다.
"""

# 화면 공통 색상
COLOR_BACKGROUND = "#0B111A"
COLOR_PANEL = "#111827"
COLOR_PANEL_DARK = "#0B111A"
COLOR_SECTION = "#1F232B"
COLOR_SECTION_HEADER = "#171B22"
COLOR_BORDER = "#263241"
COLOR_TEXT = "#E5E7EB"
COLOR_SUB_TEXT = "#9CA3AF"
COLOR_MUTED = "#6B7280"
COLOR_SUCCESS = "#22C55E"
COLOR_WARNING = "#F59E0B"
COLOR_ERROR = "#F87171"


def get_cost_color(tier):
    """
    챔피언 코스트에 따라 카드 테두리 색상을 반환한다.
    """
    colors = {
        1: "#9CA3AF",
        2: "#22C55E",
        3: "#3B82F6",
        4: "#A855F7",
        5: "#F59E0B",
    }
    return colors.get(tier, "#9CA3AF")


def get_cost_label(tier):
    """
    코스트 숫자를 화면 표시용 문자열로 변환한다.
    """
    return f"{tier} 코스트"
