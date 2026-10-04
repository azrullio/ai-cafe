"""
AI Cafe — pengumpul data tempat nongkrong Surabaya dari Google Places API (New).

Hasil: ai-cafe-data.json  ->  buka AI Cafe, klik "Impor data", pilih file ini.

Persiapan:
  1. Buat project di Google Cloud Console, aktifkan "Places API (New)", buat API key.
  2. pip install requests
  3. Windows PowerShell:  $env:GOOGLE_MAPS_API_KEY="KEY_KAMU"; python fetch_places.py
     Bash:                GOOGLE_MAPS_API_KEY=KEY_KAMU python fetch_places.py

Catatan:
  - Text Search mengembalikan maks. 60 hasil per query per area, jadi kota dibagi
    menjadi grid kecil supaya cakupannya luas. Ubah GRID_ROWS/GRID_COLS sesuai budget.
  - Field atmosfer (outdoorSeating, liveMusic, dll.) masuk SKU yang lebih mahal.
    Hapus dari FIELD_MASK kalau ingin hemat. Cek harga terbaru di Google Cloud.
  - Ketentuan Google: data Places (selain place_id) tidak boleh disimpan permanen;
    jalankan ulang script ini berkala (misal tiap bulan) untuk menyegarkan data.
"""
import json
import os
import sys
import time

import requests

API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
URL = "https://places.googleapis.com/v1/places:searchText"

# Batas kota Surabaya (kira-kira)
SOUTH, NORTH = -7.35, -7.19
WEST, EAST = 112.60, 112.82
GRID_ROWS, GRID_COLS = 5, 6  # 30 sel

QUERIES = [
    ("cafe", "cafe"),
    ("coffee shop", "cafe"),
    ("warkop", "warkop"),
    ("warung kopi", "warkop"),
    ("kedai", "kedai"),
    ("Sedulur Tunggal Kopi", "stk"),
    ("warkop STK", "stk"),
    ("restoran", "resto"),
    ("rumah makan", "resto"),
]

FIELD_MASK = ",".join([
    "places.id", "places.displayName", "places.formattedAddress", "places.location",
    "places.rating", "places.userRatingCount", "places.priceLevel",
    "places.regularOpeningHours", "places.googleMapsUri", "places.primaryType",
    "places.types", "places.nationalPhoneNumber", "places.websiteUri",
    "places.businessStatus",
    # atmosfer (lebih mahal)
    "places.outdoorSeating", "places.liveMusic", "places.goodForGroups",
    "places.parkingOptions", "places.servesCoffee", "places.paymentOptions",
    "nextPageToken",
])

PRICE = {
    "PRICE_LEVEL_FREE": 1, "PRICE_LEVEL_INEXPENSIVE": 1, "PRICE_LEVEL_MODERATE": 2,
    "PRICE_LEVEL_EXPENSIVE": 3, "PRICE_LEVEL_VERY_EXPENSIVE": 4,
}
WEEK = 10080


def area_of(lat, lng):
    if lat > -7.245:
        return "Utara"
    if lng < 112.705:
        return "Barat"
    if lng > 112.765:
        return "Timur"
    if lat < -7.300:
        return "Selatan"
    return "Pusat"


def category_of(name, types, fallback):
    n = name.lower()
    # STK = Sedulur Tunggal Kopi (cek duluan karena namanya sering juga memuat "warkop")
    if "sedulur tunggal" in n or "stk" in n.replace("(", " ").replace(")", " ").split():
        return "stk"
    if "warkop" in n or "warung kopi" in n:
        return "warkop"
    if "kedai" in n:
        return "kedai"
    if "cafe" in types or "coffee_shop" in types or "cafe" in n or "kopi" in n or "coffee" in n:
        return "cafe"
    if any(t.endswith("restaurant") for t in types) or "restaurant" in types:
        return "resto"
    return fallback


def periods_of(hours):
    """Ubah regularOpeningHours Google ke [[menit_mulai, menit_selesai]] dalam seminggu (Minggu=0)."""
    out = []
    for p in (hours or {}).get("periods", []):
        o = p.get("open")
        if not o:
            continue
        s = o["day"] * 1440 + o.get("hour", 0) * 60 + o.get("minute", 0)
        c = p.get("close")
        if not c:  # buka 24 jam
            return [[0, WEEK]]
        e = c["day"] * 1440 + c.get("hour", 0) * 60 + c.get("minute", 0)
        if e <= s:
            e += WEEK
        out.append([s, e])
    return out


def tags_of(pl, cat):
    t = []
    if pl.get("outdoorSeating"):
        t.append("outdoor")
    if pl.get("liveMusic"):
        t.append("live music")
    if pl.get("goodForGroups"):
        t.append("rombongan")
    park = pl.get("parkingOptions") or {}
    if park.get("freeParkingLot") or park.get("paidParkingLot"):
        t.append("parkir luas")
    if (pl.get("paymentOptions") or {}).get("acceptsCashOnly") is False:
        t.append("non-tunai")
    if PRICE.get(pl.get("priceLevel"), 0) == 1:
        t.append("murah")
    return t


def search(query, low, high):
    body = {
        "textQuery": f"{query} Surabaya",
        "pageSize": 20,
        "languageCode": "id",
        "regionCode": "ID",
        "locationRestriction": {"rectangle": {
            "low": {"latitude": low[0], "longitude": low[1]},
            "high": {"latitude": high[0], "longitude": high[1]},
        }},
    }
    headers = {"X-Goog-Api-Key": API_KEY, "X-Goog-FieldMask": FIELD_MASK}
    for _ in range(3):  # maks. 3 halaman = 60 hasil
        r = requests.post(URL, json=body, headers=headers, timeout=30)
        if r.status_code != 200:
            print("  ! error", r.status_code, r.text[:200], file=sys.stderr)
            return
        data = r.json()
        yield from data.get("places", [])
        token = data.get("nextPageToken")
        if not token:
            return
        body["pageToken"] = token
        time.sleep(1.5)


def main():
    if not API_KEY:
        sys.exit("Set dulu environment variable GOOGLE_MAPS_API_KEY.")
    seen = {}
    dlat = (NORTH - SOUTH) / GRID_ROWS
    dlng = (EAST - WEST) / GRID_COLS
    for i in range(GRID_ROWS):
        for j in range(GRID_COLS):
            low = (SOUTH + i * dlat, WEST + j * dlng)
            high = (low[0] + dlat, low[1] + dlng)
            for q, fallback in QUERIES:
                n0 = len(seen)
                for pl in search(q, low, high):
                    if pl["id"] in seen or pl.get("businessStatus") == "CLOSED_PERMANENTLY":
                        continue
                    name = pl.get("displayName", {}).get("text", "")
                    loc = pl.get("location", {})
                    types = pl.get("types", [])
                    cat = category_of(name, types, fallback)
                    seen[pl["id"]] = {
                        "id": pl["id"],
                        "placeId": pl["id"],
                        "name": name,
                        "category": cat,
                        "area": area_of(loc.get("latitude", 0), loc.get("longitude", 0)),
                        "address": pl.get("formattedAddress", ""),
                        "lat": loc.get("latitude"),
                        "lng": loc.get("longitude"),
                        "rating": pl.get("rating", 0),
                        "reviews": pl.get("userRatingCount", 0),
                        "price": PRICE.get(pl.get("priceLevel"), 0),
                        "periods": periods_of(pl.get("regularOpeningHours")),
                        "hoursText": (pl.get("regularOpeningHours") or {}).get("weekdayDescriptions", []),
                        "phone": pl.get("nationalPhoneNumber"),
                        "website": pl.get("websiteUri"),
                        "mapsUrl": pl.get("googleMapsUri"),
                        "tags": tags_of(pl, cat),
                    }
                print(f"sel {i},{j} '{q}': +{len(seen) - n0}  (total {len(seen)})")

    places = [p for p in seen.values() if p["lat"] is not None]
    with open("ai-cafe-data.json", "w", encoding="utf-8") as f:
        json.dump(places, f, ensure_ascii=False, indent=1)
    print(f"\nSelesai: {len(places)} tempat -> ai-cafe-data.json")


if __name__ == "__main__":
    main()
