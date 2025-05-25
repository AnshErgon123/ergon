import os
import time
import can
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SERVER_URL = os.getenv("SERVER_URL")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")

print(f"SERVER_URL: {SERVER_URL}")
print(f"SECRET_TOKEN: {SECRET_TOKEN}")

HEADERS = {
    "Authorization": f"Bearer {SECRET_TOKEN}",
    "Content-Type": "application/json"
}

can_interface = 'pcan'
can_channel = 'PCAN_USBBUS1'

RETRY_DELAY = 5  # seconds
HEARTBEAT_INTERVAL = 10  # seconds

def send_heartbeat():
    try:
        res = requests.post(f"{SERVER_URL}/api/heartbeat", headers=HEADERS)
        if res.status_code == 200:
            print("Heartbeat sent")
        else:
            print(f"⚠️ Heartbeat failed: {res.status_code}")
    except Exception as e:
        print("❌ Heartbeat error:", e)

def main():
    last_heartbeat = 0

    try:
        bus = can.interface.Bus(channel=can_channel, bustype=can_interface)
        print(f"🚗 Sending CAN messages to: {SERVER_URL}")

        while True:
            current_time = time.time()
            if current_time - last_heartbeat > HEARTBEAT_INTERVAL:
                send_heartbeat()
                last_heartbeat = current_time

            msg = bus.recv(0.1)  # Timeout of 1 sec

            if msg:
                timestamp_str = datetime.fromtimestamp(msg.timestamp).isoformat()
                can_id_str = f"{msg.arbitration_id:03X}"
                data_str = ' '.join(f"{b:02X}" for b in msg.data)

                payload = {
                    "timestamp": timestamp_str,
                    "id": can_id_str,
                    "data": data_str
                }

                try:
                    res = requests.post(f"{SERVER_URL}/api/send_data", json=payload, headers=HEADERS)
                    if res.status_code == 200:
                        print(f"✅ Sent: {payload}")
                    else:
                        print(f"⚠️ Failed: {res.status_code} {res.text}")
                        time.sleep(RETRY_DELAY)
                except requests.RequestException as e:
                    print(f"❌ Network error: {e}")
                    time.sleep(RETRY_DELAY)

            time.sleep(0.1)

    except can.CanError as e:
        print("❌ CAN interface error:", e)
    except Exception as e:
        print("❌ Unexpected error:", e)

if __name__ == "__main__":
    main()