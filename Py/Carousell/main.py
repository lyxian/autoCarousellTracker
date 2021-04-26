import requests
import json

def requestPayload(query: str, num: int) -> dict:
    return {
        "count": num,
        "countryCode": "SG",
        "countryId": "1880251",
        "filters": [],
        "isFreeItems": False,
        "locale": "en",
        "prefill": {"prefill_sort_by": ""},
        "query": query
    }

def searchCarousell(base_url_filter, payload):
    return requests.post(base_url_filter, json=payload).json()