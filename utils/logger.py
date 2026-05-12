from datetime import datetime


def log_action(action_text):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("data/audit_log.txt", "a") as file:
        file.write(f"[{timestamp}] {action_text}\n")