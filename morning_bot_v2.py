import requests
from datetime import datetime, timezone
import urllib.parse
import sys
import time

# ===================== CONFIG =====================
CITY = "Samoens"
LAT = 46.0833
LON = 6.7278
PHONE = "33766448494"
CALLMEBOT_KEY = "1945917"
WEATHER_KEY = "55dd193119cdf93ff199ed83174aed48"
TIMEZONE_OFFSET = 2
# ==================================================

def validate():
    errors = []
    if CITY == "YOUR_CITY":
        errors.append("CITY")
    if LAT == 0.0 and LON == 0.0:
        errors.append("LAT/LON")
    if PHONE == "YOUR_PHONE":
        errors.append("PHONE")
    if CALLMEBOT_KEY == "YOUR_KEY":
        errors.append("CALLMEBOT_KEY")
    if WEATHER_KEY == "YOUR_KEY":
        errors.append("WEATHER_KEY")
    if errors:
        print("FATAL: Fill in these config values:")
        for e in errors:
            print("  - " + e)
        sys.exit(1)

def get_weather():
    try:
        url = "https://api.openweathermap.org/data/2.5/weather?q=" + CITY + "&appid=" + WEATHER_KEY + "&units=metric"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        d = r.json()
        tc = d["main"]["temp"]
        tf = (tc * 9.0 / 5.0) + 32
        desc = d["weather"][0]["description"].title()
        return str(int(tf)) + "F / " + str(int(tc)) + "C, " + desc
    except Exception as e:
        print("[WARN] Weather failed: " + str(e))
        return "Weather unavailable"

def get_sun():
    try:
        url = "https://api.sunrise-sunset.org/json?lat=" + str(LAT) + "&lng=" + str(LON) + "&formatted=0"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        d = r.json()
        sr = d["results"]["sunrise"][11:16]
        ss = d["results"]["sunset"][11:16]
        return sr, ss
    except Exception as e:
        print("[WARN] Sun times failed: " + str(e))
        return "--:--", "--:--"

def get_btc():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
        r = requests.get(url, timeout=15)
        # If rate limited, wait 30s and retry once
        if r.status_code == 429:
            print("[INFO] CoinGecko rate limited, waiting 30s...")
            time.sleep(30)
            r = requests.get(url, timeout=15)
        r.raise_for_status()
        d = r.json()
        p = d["bitcoin"]["usd"]
        c = d["bitcoin"].get("usd_24h_change", 0)
        a = "UP" if c >= 0 else "DOWN"
        return "$" + "{:,.0f}".format(p) + " (" + a + " " + "{:+.1f}".format(c) + "%)"
    except Exception as e:
        print("[WARN] BTC failed: " + str(e))
        return "BTC unavailable"

def get_fact():
    try:
        url = "https://uselessfacts.jsph.pl/random.json?language=en"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json()["text"]
    except Exception as e:
        print("[WARN] Fact failed: " + str(e))
        return "Fun fact unavailable"

def send(text):
    try:
        enc = urllib.parse.quote(text)
        url = "https://api.callmebot.com/whatsapp.php?phone=" + PHONE + "&text=" + enc + "&apikey=" + CALLMEBOT_KEY
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return True
    except Exception as e:
        print("[WARN] Send failed: " + str(e))
        return False

def main():
    validate()

    day = datetime.now(timezone.utc).strftime("%A, %B %d")
    w = get_weather()
    sr, ss = get_sun()
    b = get_btc()
    f = get_fact()

    lines = []
    lines.append("Morning Briefing")
    lines.append(day)
    lines.append("")
    lines.append(CITY + ": " + w)
    lines.append("Sunrise: " + sr)
    lines.append("Sunset: " + ss)
    lines.append("")
    lines.append("Bitcoin: " + b)
    lines.append("")
    lines.append("Fun Fact: " + f)

    msg = chr(10).join(lines)

    ok = send(msg)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    if ok:
        print("[" + ts + "] Message sent OK")
    else:
        print("[" + ts + "] FAILED to send")
    print("")
    print("--- MESSAGE ---")
    print(msg)
    print("--- END ---")

if __name__ == "__main__":
    main()
