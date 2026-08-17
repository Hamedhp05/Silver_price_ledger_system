# import requests
# import secrets
# import string
# import random

# def find_all(obj, keyword, path=""):
#     if isinstance(obj, dict):
#         for key, value in obj.items():
#             new_path = f"{path}.{key}" if path else key

#             if keyword.lower() in str(key).lower():
#                 print("\n🔎", new_path)
#                 print(value)

#             find_all(value, keyword, new_path)

#     elif isinstance(obj, list):
#         for i, value in enumerate(obj):
#             find_all(value, keyword, f"{path}[{i}]")

# subdomains = ["call2", "call3", "call4"]

# possible = string.ascii_letters + string.digits

# rev = ''.join(
#     secrets.choice(possible)
#     for _ in range(60)
# )

# subdomain = random.choice(subdomains)

# url = f"https://{subdomain}.tgju.org/ajax.json"

# data = requests.get(
#     url,
#     params={"rev": rev}
# ).json()

# silver = data["current"]["silver_999"]
# for key, value in silver.items():
#     print(f"{key}: {value}")

import random
import secrets
import string

import requests


TGJU_SUBDOMAINS = ("call2", "call3", "call4")
TGJU_URL = "https://{subdomain}.tgju.org/ajax.json"


class TGJUScraperError(Exception):
    """Raised when fetching data from TGJU fails."""


def _generate_rev(length: int = 60) -> str:
    characters = string.ascii_letters + string.digits

    return "".join(
        secrets.choice(characters)
        for _ in range(length)
    )


def get_silver_price() -> dict:
    """
    Fetch raw Silver 999 data from TGJU.

    Returns:
        {
            "source": "tgju",
            "price": "4,074,300",
            "fetched_at": "2026-08-15 12:49:29",
            "currency": "IRR"
        }
    """

    try:
        subdomain = random.choice(TGJU_SUBDOMAINS)

        response = requests.get(
            TGJU_URL.format(subdomain=subdomain),
            params={"rev": _generate_rev()},
            timeout=15,
        )

        response.raise_for_status()

        data = response.json()
        silver = data["current"]["silver_999"]

        return {
            "source": "tgju",
            "price": silver["p"],
            "fetched_at": silver["ts"],
            "currency": "IRR",
        }

    except requests.RequestException as exc:
        raise TGJUScraperError(
            f"TGJU request failed: {exc}"
        ) from exc

    except (KeyError, TypeError, ValueError) as exc:
        raise TGJUScraperError(
            f"Invalid TGJU response: {exc}"
        ) from exc

