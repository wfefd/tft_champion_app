import requests

from config import (
    DDRAGON_VERSION_URL,
    DDRAGON_BASE_URL,
    DDRAGON_LOCALE,
    CDRAGON_LOCALE,
)


CDRAGON_TFT_URL = (
    f"https://raw.communitydragon.org/latest/cdragon/tft/{CDRAGON_LOCALE}.json"
)


# 최신 Data Dragon 버전 조회
def get_latest_version():
    response = requests.get(DDRAGON_VERSION_URL, timeout=20)
    response.raise_for_status()

    versions = response.json()
    return versions[0]


# Data Dragon JSON 조회
def fetch_ddragon_json(version, file_name):
    url = (
        f"{DDRAGON_BASE_URL.format(version=version, locale=DDRAGON_LOCALE)}"
        f"/{file_name}"
    )

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    return response.json()["data"]


# Community Dragon TFT JSON 조회
def fetch_cdragon_tft_json():
    response = requests.get(CDRAGON_TFT_URL, timeout=60)
    response.raise_for_status()

    return response.json()