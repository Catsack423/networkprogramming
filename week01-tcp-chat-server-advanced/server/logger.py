import datetime

def log_message(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{timestamp}] {message}"
    print(formatted_msg)
    with open("server_log.txt", "a", encoding="utf-8") as f:
        f.write(formatted_msg + "\n")