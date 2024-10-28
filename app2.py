import psutil
import yagmail
import json
import time
import threading
from flask import Flask, jsonify

app = Flask(__name__)

with open('config.json') as config_file:
    config = json.load(config_file)

cpu_threshold = config["thresholds"]["cpu_usage"]
ram_threshold = config["thresholds"]["ram_usage"]

sender = config["email"]["sender"]
receiver = config["email"]["receiver"]
password = config["email"]["password"]

yag = yagmail.SMTP(sender, password)

cpu_high = False
ram_high = False

def send_email_alert(subject, message):
    """Send an email alert."""
    try:
        yag.send(to=receiver, subject=subject, contents=message)
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

def check_thresholds(cpu_usage, ram_usage):
    """Check thresholds for CPU and RAM usage and send alerts if exceeded."""
    global cpu_high, ram_high

    if cpu_usage > cpu_threshold and not cpu_high:
        send_email_alert(
            "CPU Usage Alert",
            f"CPU usage is at {cpu_usage}% which is above the threshold of {cpu_threshold}%."
        )
        cpu_high = True
    elif cpu_usage <= cpu_threshold and cpu_high:
        send_email_alert(
            "CPU Usage Normal",
            f"CPU usage has dropped to {cpu_usage}%, back to normal."
        )
        cpu_high = False


    if ram_usage > ram_threshold and not ram_high:
        send_email_alert(
            "RAM Usage Alert",
            f"RAM usage is at {ram_usage}% which is above the threshold of {ram_threshold}%."
        )
        ram_high = True
    elif ram_usage <= ram_threshold and ram_high:
        send_email_alert(
            "RAM Usage Normal",
            f"RAM usage has dropped to {ram_usage}%, back to normal."
        )
        ram_high = False

def check_system_usage():
    
    while True:
        cpu_usage = psutil.cpu_percent(interval=1)
        ram_usage = psutil.virtual_memory().percent

        print(f"Current CPU Usage: {cpu_usage}%, RAM Usage: {ram_usage}%") 
        check_thresholds(cpu_usage, ram_usage)


        time.sleep(5) 
        
monitoring_thread = threading.Thread(target=check_system_usage)
monitoring_thread.daemon = True
monitoring_thread.start()

@app.route('/cpu', methods=['GET'])
def get_cpu_usage():
    cpu_usage = psutil.cpu_percent(interval=1)
    return jsonify({"cpu_usage": cpu_usage})

@app.route('/ram', methods=['GET'])
def get_ram_usage():
    ram_usage = psutil.virtual_memory().percent
    return jsonify({"ram_usage": ram_usage})

@app.route('/disk', methods=['GET'])
def get_disk_usage():
    disk_usage = psutil.disk_usage('/') 
    return jsonify({
        "total_disk": disk_usage.total // (1024 ** 3),
        "used_disk": disk_usage.used // (1024 ** 3),
        "free_disk": disk_usage.free // (1024 ** 3),
        "disk_usage_percent": disk_usage.percent
    })

@app.route('/system', methods=['GET'])
def get_system_usage():
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    return jsonify({
        "cpu_usage": cpu_usage,
        "ram_usage": ram_usage
    })

if __name__ == '__main__':
    app.run(debug=True)
