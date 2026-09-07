#!/usr/bin/env python3
"""
Gmail SMTP + 앱 비밀번호로 엑셀 파일을 첨부해 메일을 보낸다.

필요 환경변수:
    SMTP_EMAIL         보내는 사람 Gmail 주소
    SMTP_APP_PASSWORD  Google 계정 앱 비밀번호(2단계 인증 필요)
"""

import argparse
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def send_email(to_addr, subject, body, attachment_path):
    sender = os.environ.get("SMTP_EMAIL")
    password = os.environ.get("SMTP_APP_PASSWORD")
    if not sender or not password:
        raise SystemExit("환경변수 SMTP_EMAIL / SMTP_APP_PASSWORD를 설정해야 합니다.")

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content(body)

    path = Path(attachment_path)
    msg.add_attachment(
        path.read_bytes(),
        maintype="application",
        subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=path.name,
    )

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)


def main():
    parser = argparse.ArgumentParser(description="강사료 정산 엑셀을 메일로 발송")
    parser.add_argument("--to", required=True, help="받는 사람 이메일 주소")
    parser.add_argument("--subject", required=True)
    parser.add_argument("--body", default="")
    parser.add_argument("--attachment", required=True, help="첨부할 xlsx 파일 경로")
    args = parser.parse_args()

    send_email(args.to, args.subject, args.body, args.attachment)
    print(f"메일 발송 완료: {args.to}")


if __name__ == "__main__":
    main()
