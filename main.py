import json
import os
import smtplib
from email.mime.text import MIMEText
from pathlib import Path
from dotenv import load_dotenv
from kaggle.api.kaggle_api_extended import KaggleApi

# .envファイルを読み込む
load_dotenv()


def load_config():
    with open("config.json", "r") as f:
        return json.load(f)


def load_sent_history():
    """送信済みコンペの履歴を読み込む"""
    history_file = Path("sent_competitions.json")
    if not history_file.exists():
        return set()

    with open(history_file, "r") as f:
        data = json.load(f)
        return set(data.get("sent_titles", []))


def save_sent_history(titles):
    """送信済みコンペの履歴を保存"""
    history_file = Path("sent_competitions.json")
    with open(history_file, "w") as f:
        json.dump({"sent_titles": list(titles)}, f, indent=2)


def get_competitions():
    """Kaggle APIを使ってコンペ一覧を取得"""
    api = KaggleApi()
    api.authenticate()

    # 全コンペを取得（複数ページ）
    all_comps = []
    for page in range(1, 4):  # 最初の3ページ（約60件）
        comps = api.competitions_list(page=page)
        if not comps:
            break
        all_comps.extend(comps)

    results = []
    for comp in all_comps:
        results.append(
            {
                "title": comp.title,
                "deadline": str(comp.deadline),
                "category": comp.category,
                "reward": comp.reward,
                "teams": comp.team_count,
                "userHasEntered": comp.user_has_entered,
                "tags": [tag.name for tag in comp.tags] if comp.tags else [],
            }
        )

    return results


def filter_comps(comps, filters, sent_history):
    results = []
    for c in comps:
        if filters.get("category") and c["category"] not in filters["category"]:
            continue

        # 送信済みコンペをスキップ
        if c["title"] in sent_history:
            continue

        # テーブルコンペのみフィルタ
        if filters.get("table_only"):
            tags = c.get("tags", [])
            if "tabular" not in tags:
                continue

        results.append(c)
    return results


def send_email(subject, body):
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    to = os.getenv("EMAIL", "")

    # 環境変数チェック
    if not smtp_user or not smtp_pass:
        raise ValueError(
            "SMTP_USER and SMTP_PASS must be set in .env file.\n"
            "For Gmail, you need to:\n"
            "1. Enable 2-factor authentication\n"
            "2. Generate an App Password at https://myaccount.google.com/apppasswords\n"
            "3. Set SMTP_USER=your-email@gmail.com and SMTP_PASS=your-app-password in .env"
        )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
    except smtplib.SMTPAuthenticationError as e:
        raise ValueError(
            f"SMTP Authentication failed: {e}\n\n"
            "If using Gmail:\n"
            "1. Make sure 2-factor authentication is enabled\n"
            "2. Generate an App Password (not your regular password)\n"
            "3. Visit: https://myaccount.google.com/apppasswords\n"
            "4. Set SMTP_PASS to the 16-digit app password (no spaces)"
        ) from e
    except Exception as e:
        raise RuntimeError(f"Failed to send email: {e}") from e


def main():
    config = load_config()
    sent_history = load_sent_history()

    comps = get_competitions()
    filtered = filter_comps(comps, config["filters"], sent_history)

    if not filtered:
        print("No new competitions found.")
        return

    body = "\n\n".join(
        [f"{c['title']} ({c['category']})\nReward: {c['reward']}\nDeadline: {c['deadline']}" for c in filtered]
    )

    send_email(
        "New Kaggle Competitions Found!",
        body,
    )

    # 送信後に履歴を更新
    new_titles = {c["title"] for c in filtered}
    updated_history = sent_history | new_titles
    save_sent_history(updated_history)
    print(f"Sent notification for {len(filtered)} competition(s).")


if __name__ == "__main__":
    main()
