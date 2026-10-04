"""
Gabungkan data OpenStreetMap + daftar kurasi (artikel kuliner) -> ai-cafe-data.json
Pemakaian: python build_data.py            (default: data/osm.json data/osm2.json)
           python build_data.py a.json b.json
Hasil juga langsung disisipkan ke ai-cafe.html sebagai data bawaan.
"""
import json, re, sys, time, urllib.parse, urllib.request

WEEK = 10080
DAYS = {"su": 0, "mo": 1, "tu": 2, "we": 3, "th": 4, "fr": 5, "sa": 6}
UA = "AICafe-data-builder/1.0 (personal project)"

# ---------- Kurasi: sumber artikel (rating dari Google Maps sesuai artikel) + tempat legendaris ----------
# rs: "artikel" = rating dikutip artikel, "perkiraan" = perkiraan AI, None = tidak ada
CURATED = [
 # Jl. Tunjungan — JawaPos (rating Google per artikel)
 dict(name="Tomoro Coffee Tunjungan", category="cafe", address="Jl. Tunjungan No.31, Genteng", rating=4.9, reviews=625, rs="artikel", hours="Mo-Fr 07:00-22:00; Sa,Su 07:00-23:00", tags=["takeaway"], src="jawapos.com"),
 dict(name="Firstfloor Coffee", category="cafe", address="Jl. Tunjungan No.57D, Genteng", rating=4.5, reviews=485, rs="artikel", hours="Mo-Fr 08:00-23:00; Sa,Su 08:00-24:00", tags=["kerja"], src="jawapos.com"),
 dict(name="Thirty Three Brew", category="cafe", address="Jl. Tunjungan No.34C, Genteng", rating=4.6, reviews=574, rs="artikel", tags=["specialty coffee"], src="jawapos.com"),
 dict(name="Loske Coffee Service Tunjungan", category="cafe", address="Jl. Tunjungan No.14, Genteng", hours="Mo-Su 06:00-02:00", tags=["kuliner malam"], src="idntimes.com"),
 # detik.com
 dict(name="Scrt Coffee & Eatery", category="cafe", address="Jl. Ngagel Jaya Barat No.63, Pucang Sewu, Gubeng", rating=4.7, reviews=563, rs="artikel", tags=["outdoor","instagramable"], src="detik.com"),
 dict(name="Yoi Kona", category="cafe", address="Jl. Dr. Ir. H. Soekarno No.20M, Rungkut Kidul, Rungkut", rating=4.6, reviews=1600, rs="artikel", tags=["outdoor","rombongan","instagramable"], src="detik.com"),
 dict(name="Locus Cafe by Kuea", category="cafe", address="Jl. Sidosermo Indah No.6, Sidosermo, Wonocolo", rating=4.6, reviews=224, rs="artikel", hours="Mo-Su 10:00-22:00", tags=["outdoor","instagramable"], src="detik.com"),
 dict(name="Jokopi Ketabang Kali", category="cafe", address="Jl. Ketabang Kali No.51A, Genteng", rating=4.6, reviews=2906, rs="artikel", tags=["outdoor","rombongan"], src="detik.com"),
 dict(name="Jokopi Dinoyo", category="cafe", address="Jl. Dinoyo No.83B, Keputran, Tegalsari", rating=4.6, reviews=1303, rs="artikel", tags=["rombongan"], src="detik.com"),
 dict(name="Jokopi MERR", ll=(-7.3200, 112.7835), geo="Jalan Dokter Ir. H. Soekarno, Rungkut, Surabaya", category="cafe", address="Jl. Dr. Ir. H. Soekarno No.431, Rungkut", rating=4.5, reviews=965, rs="artikel", tags=["rombongan","parkir luas"], src="detik.com"),
 dict(name="Saisho Coffee G-Walk", category="cafe", address="Food Garden FG 5B, G-Walk CitraLand, Sambikerep", rating=4.4, reviews=176, rs="artikel", src="detik.com", geo="G-Walk Citraland Surabaya"),
 dict(name="TENTWO Coffee & Kindness", category="cafe", address="Jl. Jawa No.41, Gubeng", rating=4.6, reviews=322, rs="artikel", tags=["outdoor"], src="detik.com"),
 # JawaPos / IDN Times / Hipwee (tanpa rating)
 dict(name="Calibre Coffee Roasters", category="cafe", address="Jl. Walikota Mustajab No.67-69, Genteng", hours="Mo-Fr 10:00-22:00; Sa,Su 10:00-23:00", tags=["specialty coffee","kerja"], src="jawapos.com"),
 dict(name="Redback Specialty Coffee", category="cafe", address="Graha Golf 2 Blok K, Graha Famili, Dukuh Pakis", hours="Mo-Su 06:00-22:00", tags=["specialty coffee","sarapan"], src="jawapos.com", geo="Graha Famili Surabaya"),
 dict(name="Matly Bakehouse", geo="Darmo Permai, Surabaya", category="cafe", address="Jl. Raya Darmo Permai I No.24, Pradahkalikendal, Dukuhpakis", hours="Mo-Su 08:00-22:00", src="idntimes.com"),
 dict(name="Postman Dining", category="resto", address="Jl. Dharmahusada Permai I No.301, Mulyorejo", hours="Mo-Su 07:00-22:00", tags=["sarapan"], src="idntimes.com"),
 dict(name="14g Coffee", category="cafe", address="Ruko Beverly RL5 No.15, Pakuwon City", hours="Mo-Su 07:00-19:00", src="idntimes.com", geo="Pakuwon City Surabaya"),
 dict(name="Brunsj Bake House Nias", category="cafe", address="Jl. Nias No.96, Gubeng", hours="Mo-Su 11:00-22:00", src="idntimes.com"),
 dict(name="Stacked Burger Joint", category="resto", address="Jl. Teuku Umar No.30, DR. Soetomo, Tegalsari", hours="Mo-Su 11:00-22:00", src="idntimes.com"),
 dict(name="Le Blé Boulangerie Margorejo", geo="Margorejo Indah, Surabaya", category="cafe", address="Jl. Margorejo Indah Blok A-512, Wonocolo", hours="Mo-Su 07:00-22:00", tags=["sarapan"], src="idntimes.com"),
 dict(name="Midnightbaker Imam Bonjol", category="cafe", address="Jl. Imam Bonjol No.40, Tegalsari", hours="Mo-Su 07:00-22:00", src="idntimes.com"),
 dict(name="Breaky Eatery & Desserts", category="cafe", address="Jl. Rajawali No.49 J-K, Krembangan Selatan", hours="Mo-Su 07:00-21:00", tags=["sarapan"], src="idntimes.com"),
 dict(name="Karbs Social Bakery & Cafe", category="cafe", address="Jl. Opak No.52, Darmo, Wonokromo", hours="Mo-Su 07:00-22:00", src="idntimes.com"),
 dict(name="Fine Co Workingspace", geo="Medokan Asri, Surabaya", category="cafe", address="Jl. Medokan Asri Barat No.26, Rungkut", hours="Mo-Su 08:00-24:00", tags=["kerja","wifi","colokan"], src="idntimes.com"),
 dict(name="Tomoro Coffee Sidosermo", category="cafe", address="Jl. Sidosermo Airdas No.19, Wonocolo", hours="Mo-Su 07:00-23:00", tags=["takeaway"], src="idntimes.com"),
 dict(name="Völks Coffee", category="cafe", address="Jl. Jambi No.21, Darmo, Wonokromo", hours="Mo-Su 07:00-21:00", src="jawapos.com"),
 dict(name="Threelogy Coffee", category="cafe", address="Jl. Mojopahit No.46, Darmo, Wonokromo", hours="Mo-Su 07:00-21:00", src="jawapos.com"),
 dict(name="Kedai Bubu Hainan", category="kedai", address="Bukit Telaga Golf TC3 No.28, CitraLand, Sambikerep", tags=["sarapan"], src="jawapos.com", geo="Bukit Telaga Golf Citraland Surabaya"),
 # Warkop
 dict(name="Warkop Sarkam", category="warkop", address="Jl. Nyamplungan No.97, Ampel, Semampir", hours="24/7", tags=["legendaris","murah"], src="mojok.co"),
 dict(name="Warkop Mantul", category="warkop", address="Jl. Kusuma Bangsa No.31, Ketabang, Genteng", hours="24/7", tags=["murah"], src="jawapos.com"),
 dict(name="Warkop Kopi Makmur Rungkut", approx=True, category="warkop", address="Rungkut, Surabaya Timur", note="Buka mulai 15.00", tags=["murah","legendaris"], src="jawapos.com", geo="Rungkut Surabaya"),
 dict(name="Warkop Lestari Menur", approx=True, category="warkop", address="Menur Pumpungan, Sukolilo", tags=["murah","legendaris"], src="jawapos.com", geo="Menur Pumpungan Surabaya"),
 dict(name="Depot Sederhana (Gubeng Pojok)", category="resto", address="Jl. Stasiun Gubeng No.1A, Pacar Keling, Genteng", hours="24/7", tags=["legendaris"], src="jawapos.com", geo="Stasiun Gubeng Surabaya"),
 # Legendaris (rating & jam = perkiraan AI)
 dict(name="Carpentier Kitchen", category="cafe", address="Jl. Untung Suropati No.83, DR. Soetomo, Tegalsari", rating=4.6, reviews=9000, rs="perkiraan", hours="Mo-Su 08:00-22:00", tags=["instagramable","outdoor","ac"]),
 dict(name="De Soematra 1910", category="resto", address="Jl. Sumatera No.75, Gubeng", rating=4.6, reviews=4000, rs="perkiraan", hours="Mo-Su 10:00-22:00", tags=["heritage","ac","date"]),
 dict(name="Zangrandi Ice Cream", category="kedai", address="Jl. Yos Sudarso No.15, Embong Kaliasin, Genteng", rating=4.5, reviews=10000, rs="perkiraan", hours="Mo-Su 10:00-22:00", tags=["legendaris","heritage"]),
 dict(name="House of Sampoerna Café", category="cafe", address="Jl. Taman Sampoerna No.6, Krembangan Utara", rating=4.6, reviews=3000, rs="perkiraan", hours="Mo-Su 09:00-22:00", tags=["heritage","ac"], geo="House of Sampoerna Surabaya"),
 dict(name="Warkop Mbah Cokro", ll=(-7.3165, 112.7530), geo="Jalan Raya Prapen, Surabaya", category="warkop", address="Jl. Raya Prapen No.22, Panjang Jiwo, Tenggilis Mejoyo", rating=4.5, reviews=8000, rs="perkiraan", hours="Mo-Su 07:00-24:00", tags=["wifi","colokan","outdoor","parkir luas","rombongan"]),
 dict(name="Rawon Setan Mbak Endang", category="resto", address="Jl. Embong Malang No.78, Kedungdoro, Tegalsari", rating=4.4, reviews=12000, rs="perkiraan", hours="Mo-Su 18:00-04:00", tags=["legendaris","kuliner malam"]),
 dict(name="Lontong Balap Pak Gendut", category="kedai", address="Jl. Kranggan No.60, Sawahan", rating=4.4, reviews=3500, rs="perkiraan", hours="Mo-Su 08:00-21:00", tags=["legendaris","murah"]),
 dict(name="Sate Klopo Ondomohen Bu Asih", category="resto", address="Jl. Walikota Mustajab No.36, Ketabang, Genteng", rating=4.5, reviews=9000, rs="perkiraan", hours="Mo-Su 06:00-22:00", tags=["legendaris","sarapan"]),
 dict(name="Rujak Cingur Ahmad Jais", category="kedai", address="Jl. Ahmad Jais No.40, Peneleh, Genteng", rating=4.4, reviews=2500, rs="perkiraan", hours="Mo-Su 08:00-16:00", tags=["legendaris"]),
 dict(name="Depot Bu Rudy Dharmahusada", category="resto", address="Jl. Dharmahusada No.140, Mojo, Gubeng", rating=4.6, reviews=15000, rs="perkiraan", hours="Mo-Su 06:00-21:00", tags=["legendaris","parkir luas","rombongan"]),
 dict(name="Soto Ayam Lamongan Cak Har", category="resto", address="Jl. Dr. Ir. H. Soekarno (MERR), Sukolilo", rating=4.5, reviews=11000, rs="perkiraan", hours="Mo-Su 07:00-24:00", tags=["legendaris","parkir luas"], geo="Soto Cak Har Surabaya"),
 dict(name="Kya-Kya Kembang Jepun", category="resto", address="Jl. Kembang Jepun, Pabean Cantian", rating=4.3, reviews=3000, rs="perkiraan", hours="Mo-Su 17:00-23:00", tags=["kuliner malam","outdoor","murah"], geo="Jalan Kembang Jepun Surabaya"),
 dict(name="G-Walk Citraland", category="resto", address="G-Walk, CitraLand, Sambikerep", rating=4.5, reviews=6000, rs="perkiraan", hours="Mo-Su 10:00-24:00", tags=["kuliner malam","outdoor","parkir luas","rombongan"], geo="G-Walk Citraland Surabaya"),
]

# ---------- Jam buka format OSM -> periode menit/minggu ----------
def parse_hours(s):
    if not s:
        return []
    s = s.strip()
    if s in ("24/7", "Mo-Su 00:00-24:00", "00:00-24:00"):
        return [[0, WEEK]]
    out = []
    for rule in s.split(";"):
        rule = rule.strip()
        if not rule or "PH" in rule:
            continue
        m = re.match(r"^((?:[A-Za-z]{2}(?:-[A-Za-z]{2})?)(?:,[A-Za-z]{2}(?:-[A-Za-z]{2})?)*)?\s*(.*)$", rule)
        dpart, tpart = m.group(1), m.group(2).strip()
        days = set()
        if dpart:
            for seg in dpart.split(","):
                a, _, b = seg.partition("-")
                a, b = a.lower(), (b or a).lower()
                if a not in DAYS or b not in DAYS:
                    return []
                i = DAYS[a]
                while True:
                    days.add(i)
                    if i == DAYS[b]:
                        break
                    i = (i + 1) % 7
        else:
            days = set(range(7))
        if tpart in ("off", "closed"):
            out = [p for p in out if p[0] // 1440 not in days]
            continue
        times = re.findall(r"(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})", tpart)
        if not times:
            if tpart == "24/7" or tpart == "":
                for d in days:
                    out.append([d * 1440, d * 1440 + 1440])
                continue
            return []
        out = [p for p in out if p[0] // 1440 not in days]
        for d in sorted(days):
            for h1, m1, h2, m2 in times:
                o = int(h1) * 60 + int(m1)
                c = int(h2) * 60 + int(m2)
                if c <= o:
                    c += 1440
                out.append([d * 1440 + o, d * 1440 + c])
    if len(out) == 7 and all(e - s >= 1440 for s, e in out):
        return [[0, WEEK]]
    return sorted(out)

def area_of(lat, lng):
    if lat > -7.245: return "Utara"
    if lng < 112.705: return "Barat"
    if lng > 112.765: return "Timur"
    if lat < -7.300: return "Selatan"
    return "Pusat"

def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())

def category_of(name, t):
    n = name.lower()
    if "sedulur tunggal" in n or re.search(r"\bstk\b", n):
        return "stk"
    if re.search(r"warkop|warung kopi|\bwk\b", n):
        return "warkop"
    if "kedai" in n or t.get("amenity") == "ice_cream":
        return "kedai"
    if t.get("amenity") == "cafe" or t.get("shop") == "coffee" or re.search(r"cafe|kafe|coffee|kopi|bakery|bake", n):
        return "cafe"
    return "resto"

SKIP = re.compile(r"fotokopi|foto kopi|bukopin|toko kopi|jasa desain|\bbank\b|herbal|jamu", re.I)
OUTSIDE = re.compile(r"sidoarjo|gresik|waru|taman|gedangan|menganti|driyorejo", re.I)

def from_osm(e):
    t = e["tags"]
    name = (t.get("name") or "").strip()
    if not name or SKIP.search(name):
        return None
    if OUTSIDE.search(t.get("addr:city", "") + " " + t.get("addr:district", "")):
        return None
    lat = e.get("lat") or e.get("center", {}).get("lat")
    lng = e.get("lon") or e.get("center", {}).get("lon")
    if lat is None or not (-7.35 <= lat <= -7.19 and 112.595 <= lng <= 112.825):
        return None
    street = " ".join(x for x in [t.get("addr:street"), ("No." + t["addr:housenumber"]) if t.get("addr:housenumber") else None] if x)
    loc = ", ".join(x for x in [street, t.get("addr:suburb") or t.get("addr:village"), t.get("addr:district") or t.get("addr:subdistrict")] if x)
    tags = []
    if t.get("internet_access") in ("wlan", "yes", "wifi"): tags.append("wifi")
    if t.get("outdoor_seating") == "yes": tags.append("outdoor")
    if t.get("air_conditioning") == "yes": tags.append("ac")
    if t.get("smoking") in ("yes", "outside", "separated", "isolated"): tags.append("smoking area")
    if t.get("takeaway") in ("yes", "only"): tags.append("takeaway")
    if t.get("delivery") == "yes": tags.append("delivery")
    cuisine = t.get("cuisine", "").replace(";", ", ").replace("_", " ")
    return dict(
        id="osm-" + e["type"][0] + str(e["id"]), name=name, category=category_of(name, t),
        address=loc, lat=round(lat, 6), lng=round(lng, 6), rating=None, reviews=0, rs=None,
        price=0, periods=parse_hours(t.get("opening_hours")), hoursRaw=t.get("opening_hours"),
        phone=t.get("phone") or t.get("contact:phone"), website=t.get("website") or t.get("contact:website"),
        cuisine=cuisine or None, tags=tags, src="openstreetmap.org",
    )

def geocode(q):
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": q, "format": "json", "limit": 1, "countrycodes": "id", "viewbox": "112.59,-7.18,112.83,-7.36", "bounded": 1})
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "id"})
    time.sleep(1.1)
    try:
        r = json.load(urllib.request.urlopen(req, timeout=30))
        return (float(r[0]["lat"]), float(r[0]["lon"])) if r else None
    except Exception as ex:
        print("  geocode gagal:", q, ex)
        return None

def main(paths):
    els = []
    for p in paths:
        els += json.load(open(p, encoding="utf-8"))["elements"]
    seen, places = set(), []
    for e in els:
        key = e["type"] + str(e["id"])
        if key in seen: continue
        seen.add(key)
        p = from_osm(e)
        if p: places.append(p)
    print("OSM:", len(places))

    by_norm = {}
    for p in places:
        by_norm.setdefault(norm(p["name"]), []).append(p)

    added = merged = 0
    for i, c in enumerate(CURATED):
        cand = by_norm.get(norm(c["name"]))
        if not cand:
            # cocokkan nama OSM yang memuat nama kurasi (atau sebaliknya), minimal 8 huruf
            nc = norm(c["name"])
            cand = [p for p in places if len(norm(p["name"])) >= 8 and (norm(p["name"]) in nc or nc in norm(p["name"]))]
        if cand and len(cand) == 1:
            p = cand[0]
            for k in ("rating", "reviews", "rs", "note"):
                if c.get(k) is not None: p[k] = c[k]
            if c.get("hours"): p["periods"] = parse_hours(c["hours"]); p["hoursRaw"] = c["hours"]
            p["name"] = c["name"]; p["category"] = c["category"]
            if c.get("address"): p["address"] = c["address"]
            p["tags"] = sorted(set(p["tags"]) | set(c.get("tags", [])))
            p["src"] = c.get("src", "pengetahuan AI") + " + openstreetmap.org"
            merged += 1
            print("  gabung:", c["name"], "<-", cand[0]["id"])
            continue
        approx = bool(c.get("approx"))
        g = c.get("ll")
        if g:
            approx = True
        else:
            g = geocode(c["name"] + ", " + c["address"] + ", Surabaya") or geocode(c["address"] + ", Surabaya")
        if not g:
            street = re.split(r"\s*No\.|,", c["address"])[0].strip()
            g = (geocode(c["geo"]) if c.get("geo") else None) or geocode(street + ", Surabaya")
            approx = True
        if not g:
            print("  lewati (tanpa koordinat):", c["name"])
            continue
        places.append(dict(
            id="cur-%d" % i, name=c["name"], category=c["category"], address=c["address"],
            lat=round(g[0], 6), lng=round(g[1], 6), rating=c.get("rating"), reviews=c.get("reviews", 0),
            rs=c.get("rs"), price=0, periods=parse_hours(c.get("hours")), hoursRaw=c.get("hours"),
            note=c.get("note"), tags=c.get("tags", []), src=c.get("src", "pengetahuan AI"),
            approx=approx or None,
        ))
        added += 1
    print("Kurasi digabung ke OSM:", merged, "| kurasi baru:", added)

    for p in places:
        p["area"] = area_of(p["lat"], p["lng"])
        if not p["periods"]: p.pop("periods")
        for k in [k for k, v in p.items() if v in (None, "", [])]:
            p.pop(k)
    places.sort(key=lambda p: p["name"].lower())
    with open("ai-cafe-data.json", "w", encoding="utf-8") as f:
        json.dump(places, f, ensure_ascii=False, separators=(",", ":"))
    from collections import Counter
    print("Total:", len(places), Counter(p["category"] for p in places))
    print("dengan jam:", sum("periods" in p for p in places), "| dengan rating:", sum("rating" in p for p in places))
    embed(places)

def embed(places, html="ai-cafe.html"):
    """Sisipkan data ke ai-cafe.html di antara penanda /*DATA*/ ... /*END*/."""
    s = open(html, encoding="utf-8").read()
    a, b = s.index("/*DATA*/"), s.index("/*END*/") + len("/*END*/")
    js = json.dumps(places, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    open(html, "w", encoding="utf-8").write(s[:a] + "/*DATA*/" + js + "/*END*/" + s[b:])
    print("Data disisipkan ke", html)

if __name__ == "__main__":
    main(sys.argv[1:] or ["data/osm.json", "data/osm2.json"])
