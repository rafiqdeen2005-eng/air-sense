import requests
from datetime import datetime

TIMEOUT = 3

def _clean(ip: str) -> str:
    return ip.strip().replace("http://", "").replace("https://", "").strip("/")

def fetch_real(ip: str):
    if not ip or not ip.strip():
        return {"error": "No IP entered."}
    ip = _clean(ip)
    try:
        r = requests.get(f"http://{ip}/data", timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        data["timestamp"] = datetime.now().strftime("%H:%M:%S")
        data["ip"] = ip
        data["source"] = "REAL"
        return data
    except requests.exceptions.Timeout:
        return {"error": f"Timeout — ESP32 at {ip} not responding"}
    except requests.exceptions.ConnectionError:
        return {"error": f"Cannot reach ESP32 at {ip}"}
    except ValueError:
        return {"error": f"ESP32 at {ip} returned invalid JSON"}
    except Exception as e:
        return {"error": str(e)}

def test_connection(ip: str):
    if not ip or not ip.strip():
        return False, "Please enter an IP."
    ip = _clean(ip)
    try:
        r = requests.get(f"http://{ip}/data", timeout=3)
        if r.status_code == 200:
            r.json()
            return True, f"Connected to {ip}"
        return False, f"Status {r.status_code}"
    except requests.exceptions.Timeout:
        return False, f"Timeout — no response from {ip}"
    except requests.exceptions.ConnectionError:
        return False, f"Cannot connect to {ip}. Is ESP32 on?"
    except Exception as e:
        return False, str(e)

def simulate(air, temp, hum, air_max, temp_max, hum_max):
    air_alert  = air > air_max
    temp_alert = temp > temp_max
    hum_alert  = hum > hum_max
    any_danger = air_alert or temp_alert or hum_alert
    return {
        "air": air, "temp": temp, "hum": hum,
        "status": "POOR" if any_danger else "OK",
        "air_alert":  air_alert,
        "temp_alert": temp_alert,
        "hum_alert":  hum_alert,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "ip": "SIMULATION", "source": "SIM",
    }