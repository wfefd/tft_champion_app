from repository.champion_repository import (
    find_all_champions,
    search_champions_by_name,
    find_champion_detail,
)


# 챔피언 목록 조회
def get_champion_list(keyword=""):
    keyword = keyword.strip()

    if keyword:
        return search_champions_by_name(keyword)

    return find_all_champions()


# 챔피언 상세정보 조회
def get_champion_detail(champion_id):
    return find_champion_detail(champion_id)