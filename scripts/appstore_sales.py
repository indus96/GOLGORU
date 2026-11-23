#!/usr/bin/env python3
"""앱스토어 앱별 다운로드(지난 30일 · 그 전 30일 대비) — 주간 지표 대시보드의 「앱스토어 다운로드」 표.

    /usr/bin/python3 scripts/appstore_sales.py <출력 폴더>      # → <출력 폴더>/appstore.json

App Store Connect API 의 판매 보고서(일별 SUMMARY)를 60일치 받아 더한다 — 크롬 로그인이 필요 없다.
키: ~/.config/golgoru/asc-sales-key 에 「판매」 권한 키 ID 가 있으면 그 키(~/.appstoreconnect/private_keys/AuthKey_<ID>.p8), 없으면 배포 키(asc-submit.py — 판매 권한 없음). 판매자 번호(vendor number, 8자리)는
~/.config/golgoru/asc-vendor 한 줄에 둔다(App Store Connect › 결제 및 재무 보고서 왼쪽 위).
보고서는 하루 늦게 나오므로 어제까지 센다. 업데이트(제품 유형 7…)와 인앱 구입은 빼고 처음 받기만 센다.
"""
import csv, datetime, gzip, importlib.util, io, json, pathlib, sys, time, urllib.error, urllib.parse, urllib.request

HOME = pathlib.Path.home()
VENDOR_FILE = HOME / ".config/golgoru/asc-vendor"
APPS = {"6797157864": "골고루", "6828151139": "뭐타지", "6803049427": "복지비 청구", "6823171086": "메트로놈 - 템포 트레이너"}
DOWNLOAD_TYPES = ("1", "1F", "1T", "F1", "1E", "1EP", "1EU")  # 처음 받기(유료 · 무료 · 유니버설 · 맥)


SALES_KEY_FILE = HOME / ".config/golgoru/asc-sales-key"  # 판매 권한 키 ID 한 줄(배포 키에는 판매 보고서 권한이 없다 — 403)


def token():
    spec = importlib.util.spec_from_file_location("asc", HOME / "Claude/medical-claim/scripts/asc-submit.py")
    asc = importlib.util.module_from_spec(spec); spec.loader.exec_module(asc)
    key_id, key = asc.KEY_ID, asc.KEY  # 발급자(issuer)는 같은 팀이라 그대로 쓴다
    if SALES_KEY_FILE.exists():
        key_id = SALES_KEY_FILE.read_text().strip()
        key = HOME / ".appstoreconnect/private_keys" / f"AuthKey_{key_id}.p8"
    import jwt
    now = int(time.time())
    return jwt.encode({"iss": asc.ISSUER, "iat": now, "exp": now + 1200, "aud": "appstoreconnect-v1"},
                      key.read_text(), algorithm="ES256", headers={"kid": key_id, "typ": "JWT"})


def day_units(tok, vendor, day):
    q = urllib.parse.urlencode({"filter[frequency]": "DAILY", "filter[reportSubType]": "SUMMARY", "filter[reportType]": "SALES",
                                "filter[vendorNumber]": vendor, "filter[reportDate]": day.isoformat()})
    req = urllib.request.Request("https://api.appstoreconnect.apple.com/v1/salesReports?" + q)
    req.add_header("Authorization", "Bearer " + tok); req.add_header("Accept", "application/a-gzip")
    try:
        raw = gzip.decompress(urllib.request.urlopen(req).read()).decode()
    except urllib.error.HTTPError as e:
        if e.code == 404:  # 그날 판매 없음 · 아직 안 나옴
            return {}
        sys.exit(f"{day}: HTTP {e.code} {e.read().decode()[:300]}")
    units = {}
    for row in csv.DictReader(io.StringIO(raw), delimiter="\t"):
        if row.get("Product Type Identifier") in DOWNLOAD_TYPES:
            app = row.get("Apple Identifier") or row.get("Parent Identifier")
            units[app] = units.get(app, 0) + int(row.get("Units") or 0)
    return units


def summarize(cur, prev):
    total = sum(cur.values()) or 1
    out = []
    for app_id, name in APPS.items():
        c, p = cur.get(app_id, 0), prev.get(app_id, 0)
        change = "" if not p else f"{'+' if c >= p else '−'}{abs(round((c - p) / p * 100))}%"
        out.append({"app": name, "units_30d": c, "share_pct": round(c / total * 100), "change": change})
    return sorted(out, key=lambda r: -r["units_30d"])


if __name__ == "__main__":
    if len(sys.argv) == 1:  # 자체 확인
        r = summarize({"6797157864": 8, "6823171086": 12}, {"6797157864": 6, "6823171086": 20})
        assert r[0] == {"app": "메트로놈 - 템포 트레이너", "units_30d": 12, "share_pct": 60, "change": "−40%"}, r
        assert r[1]["change"] == "+33%" and r[-1]["change"] == "", r
        print("ok"); sys.exit()
    if not VENDOR_FILE.exists():
        sys.exit(f"판매자 번호가 없습니다: {VENDOR_FILE} 에 8자리 숫자 한 줄을 넣어 주세요.")
    vendor = VENDOR_FILE.read_text().strip()
    tok = token()
    yesterday = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).date() - datetime.timedelta(days=1)
    cur, prev = {}, {}
    for i in range(60):
        for k, v in day_units(tok, vendor, yesterday - datetime.timedelta(days=i)).items():
            bucket = cur if i < 30 else prev
            bucket[k] = bucket.get(k, 0) + v
    rows = summarize(cur, prev)
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    (out / "appstore.json").write_text(json.dumps(rows, ensure_ascii=False))
    print(json.dumps(rows, ensure_ascii=False, indent=1))
