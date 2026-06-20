from db.connection import get_connection

from service.tft_api_client import (
    get_latest_version,
    fetch_ddragon_json,
    fetch_cdragon_tft_json,
)

from service.tft_data_utils import (
    extract_set_no,
    normalize_key,
    remove_tft_prefix,
    get_image_url,
)


# 현재 세트 번호 찾기
def get_current_set_no_from_ddragon(champion_data):
    set_numbers = []

    for champion in champion_data.values():
        champion_id = champion.get("id", "")
        set_no = extract_set_no(champion_id)

        if set_no > 0:
            set_numbers.append(set_no)

    if not set_numbers:
        raise Exception("Data Dragon에서 현재 세트 번호를 찾을 수 없습니다.")

    return max(set_numbers)


# Community Dragon에서 현재 세트 찾기
def find_current_cdragon_set(cdragon_data, current_set_no):
    set_data = cdragon_data.get("setData", [])

    if isinstance(set_data, list):
        for set_item in set_data:
            number = set_item.get("number")

            if number == current_set_no:
                return set_item

        valid_sets = [
            item
            for item in set_data
            if isinstance(item, dict) and isinstance(item.get("number"), int)
        ]

        if valid_sets:
            return max(valid_sets, key=lambda item: item.get("number"))

    sets = cdragon_data.get("sets", {})

    if isinstance(sets, dict):
        key = str(current_set_no)

        if key in sets:
            return sets[key]

        valid_sets = []

        for set_item in sets.values():
            if isinstance(set_item, dict):
                valid_sets.append(set_item)

        if valid_sets:
            return valid_sets[-1]

    raise Exception("Community Dragon에서 현재 세트 데이터를 찾을 수 없습니다.")


# 챔피언-특성 관계 map 생성
def build_cdragon_relation_map(current_set_no):
    cdragon_data = fetch_cdragon_tft_json()
    current_set = find_current_cdragon_set(cdragon_data, current_set_no)

    champions = current_set.get("champions", [])

    if not champions:
        raise Exception("Community Dragon 현재 세트에 champions 데이터가 없습니다.")

    relation_map = {}

    for champion in champions:
        api_name = champion.get("apiName", "")
        character_name = champion.get("characterName", "")
        name = champion.get("name", "")
        traits = champion.get("traits", [])

        if not traits:
            continue

        champion_keys = [
            api_name,
            character_name,
            name,
            normalize_key(api_name),
            normalize_key(character_name),
            normalize_key(name),
            remove_tft_prefix(api_name),
            normalize_key(remove_tft_prefix(api_name)),
        ]

        champion_keys = [key for key in champion_keys if key]

        for key in champion_keys:
            relation_map[key] = traits

    return relation_map


# traits 저장 및 lookup 생성
def build_trait_lookup(trait_data, current_set_no, version, con):
    trait_lookup = {}

    for trait in trait_data.values():
        trait_id = trait.get("id", "")
        trait_name = trait.get("name", "")
        set_no = extract_set_no(trait_id)

        if set_no != current_set_no:
            continue

        image = trait.get("image", {})
        image_full = image.get("full", "")
        image_url = get_image_url(version, "tft-trait", image_full)

        con.execute(
            """
            INSERT INTO traits (
                trait_id,
                name,
                image_url,
                set_no
            )
            VALUES (?, ?, ?, ?)
            """,
            [
                trait_id,
                trait_name,
                image_url,
                set_no,
            ],
        )

        lookup_keys = [
            trait_id,
            trait_name,
            normalize_key(trait_id),
            normalize_key(trait_name),
            remove_tft_prefix(trait_id),
            normalize_key(remove_tft_prefix(trait_id)),
        ]

        for key in lookup_keys:
            if key:
                trait_lookup[key] = trait_id

    return trait_lookup


# champions와 champion_traits 저장
def insert_champions_and_relations(
    champion_data,
    current_set_no,
    version,
    cdragon_relation_map,
    trait_lookup,
    con,
):
    inserted_relation_count = 0

    for champion in champion_data.values():
        champion_id = champion.get("id", "")
        champion_name = champion.get("name", "")
        tier = champion.get("tier", 0)
        set_no = extract_set_no(champion_id)

        if set_no != current_set_no:
            continue

        image = champion.get("image", {})
        image_full = image.get("full", "")
        image_url = get_image_url(version, "tft-champion", image_full)

        con.execute(
            """
            INSERT INTO champions (
                champion_id,
                name,
                tier,
                image_url,
                set_no
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                champion_id,
                champion_name,
                tier,
                image_url,
                set_no,
            ],
        )

        trait_values = find_traits_for_champion(
            champion_id,
            champion_name,
            cdragon_relation_map,
        )

        if not trait_values:
            continue

        for trait_value in trait_values:
            matched_trait_id = find_matched_trait_id(trait_value, trait_lookup)

            if matched_trait_id:
                con.execute(
                    """
                    INSERT INTO champion_traits (
                        champion_id,
                        trait_id
                    )
                    VALUES (?, ?)
                    """,
                    [
                        champion_id,
                        matched_trait_id,
                    ],
                )

                inserted_relation_count += 1

    return inserted_relation_count


# 챔피언에 해당하는 특성 찾기
def find_traits_for_champion(champion_id, champion_name, cdragon_relation_map):
    champion_keys = [
        champion_id,
        champion_name,
        normalize_key(champion_id),
        normalize_key(champion_name),
        remove_tft_prefix(champion_id),
        normalize_key(remove_tft_prefix(champion_id)),
    ]

    for key in champion_keys:
        if key in cdragon_relation_map:
            return cdragon_relation_map[key]

    return []


# 특성 이름을 trait_id로 매칭
def find_matched_trait_id(trait_value, trait_lookup):
    candidate_keys = [
        trait_value,
        normalize_key(trait_value),
        remove_tft_prefix(trait_value),
        normalize_key(remove_tft_prefix(trait_value)),
    ]

    for candidate in candidate_keys:
        if candidate in trait_lookup:
            return trait_lookup[candidate]

    return None


# 기존 데이터 삭제
def clear_existing_data(con):
    con.execute("DELETE FROM champion_traits")
    con.execute("DELETE FROM champions")
    con.execute("DELETE FROM traits")


# TFT 데이터 동기화
def sync_tft_data():
    version = get_latest_version()

    champion_data = fetch_ddragon_json(version, "tft-champion.json")
    trait_data = fetch_ddragon_json(version, "tft-trait.json")

    current_set_no = get_current_set_no_from_ddragon(champion_data)
    cdragon_relation_map = build_cdragon_relation_map(current_set_no)

    con = get_connection()

    try:
        clear_existing_data(con)

        trait_lookup = build_trait_lookup(
            trait_data,
            current_set_no,
            version,
            con,
        )

        inserted_relation_count = insert_champions_and_relations(
            champion_data,
            current_set_no,
            version,
            cdragon_relation_map,
            trait_lookup,
            con,
        )

    finally:
        con.close()

    if inserted_relation_count == 0:
        raise Exception(
            "champion_traits 관계 데이터가 0개입니다. "
            "Community Dragon과 Data Dragon의 특성 이름 매칭에 실패했습니다."
        )

    return current_set_no