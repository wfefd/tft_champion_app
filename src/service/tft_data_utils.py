import re

from config import DDRAGON_IMAGE_BASE_URL


# TFT 세트 번호 추출
def extract_set_no(value):
    if not value:
        return 0

    match = re.search(r"TFT(\d+)", str(value))

    if match:
        return int(match.group(1))

    return 0


# 비교용 key 정규화
def normalize_key(value):
    if value is None:
        return ""

    value = str(value).lower()
    value = value.replace(" ", "")
    value = value.replace("_", "")
    value = value.replace("-", "")
    value = value.replace("'", "")
    value = value.replace(".", "")

    return value


# TFT17_ 같은 접두어 제거
def remove_tft_prefix(value):
    if not value:
        return ""

    return re.sub(r"^TFT\d+_", "", str(value))


# 이미지 URL 생성
def get_image_url(version, category, image_full):
    if not image_full:
        return ""

    return f"{DDRAGON_IMAGE_BASE_URL.format(version=version)}/{category}/{image_full}"