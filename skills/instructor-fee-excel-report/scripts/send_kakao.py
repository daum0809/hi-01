#!/usr/bin/env python3
"""
카카오톡 "나에게 보내기" 텍스트 메시지 발송.

카카오톡 메시지 API는 바이너리 파일을 직접 첨부할 수 없으므로, 엑셀 파일을 먼저
다운로드 가능한 링크(예: Google Drive 공유 링크)로 만든 뒤 그 링크를 담아 보낸다.

필요 환경변수:
    KAKAO_ACCESS_TOKEN  카카오 로그인으로 발급받은 액세스 토큰 (talk_message 동의 필요)

사전 준비:
    1. https://developers.kakao.com 에서 애플리케이션 생성, REST API 키 확인
    2. "카카오 로그인" 활성화, 동의항목에서 talk_message 활성화
    3. 카카오 로그인으로 인가 코드 -> 액세스 토큰 발급 (본인 계정으로 1회 로그인)
"""

import argparse
import json
import os
import urllib.parse
import urllib.request

KAKAO_MEMO_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"


def send_kakao_text(text, link_url=None):
    token = os.environ.get("KAKAO_ACCESS_TOKEN")
    if not token:
        raise SystemExit("환경변수 KAKAO_ACCESS_TOKEN을 설정해야 합니다.")

    template_object = {
        "object_type": "text",
        "text": text,
        "link": {
            "web_url": link_url or "https://developers.kakao.com",
            "mobile_web_url": link_url or "https://developers.kakao.com",
        },
    }
    if link_url:
        template_object["button_title"] = "확인하기"

    data = urllib.parse.urlencode(
        {"template_object": json.dumps(template_object, ensure_ascii=False)}
    ).encode("utf-8")

    req = urllib.request.Request(
        KAKAO_MEMO_URL,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return resp.status, resp.read().decode("utf-8")


def main():
    parser = argparse.ArgumentParser(description="카카오톡 '나에게 보내기' 발송")
    parser.add_argument("--text", required=True, help="메시지 본문")
    parser.add_argument("--link", default=None, help="엑셀 파일 다운로드 링크 (Google Drive 등)")
    args = parser.parse_args()

    status, body = send_kakao_text(args.text, args.link)
    print(f"카카오톡 발송 결과: {status} {body}")


if __name__ == "__main__":
    main()
