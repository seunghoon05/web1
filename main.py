
import requests
import re
import urllib3
import traceback
import smtplib
from email.mime.text import MIMEText
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://golfpang.com/web/round/join_tblList.do"

exclude_keywords = ["스프링베일", "블랙스톤벨포레", 
"힐데스하임","솔라고","동서울","대영","떼제베","올데이"]

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0"
}

# Gmail 정보
GMAIL_USER = "seunghoon272@gmail.com"
GMAIL_APP_PASSWORD = "kkjlrqqeacbtkhov"
TO_EMAIL = "seunghoon272@gmail.com"  # 본인 메일 가능

def send_email(subject, body):
    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = TO_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(msg)

def get_golf_data():
    all_data = []
    try:
        for page in range(1, 6):
            payload = {
                "pageNum": str(page),
                "bkOrder": "rd_fee_desc",
                "rd_date": "",
                "sector": "",
                "cdOrder": "2",
                "clubname": ""
            }
            response = requests.post(url, data=payload, headers=headers, verify=False)
            html = response.text

            pattern = re.compile(
                r'<tr[^>]*>.*?'
                r'<td[^>]*>(.*?)</td>.*?'
                r'<td[^>]*>(.*?)</td>.*?'
                r'<td[^>]*>(.*?)</td>.*?'
                r'(?:<td[^>]*>.*?</td>.*?)?'
                r'<td[^>]*align="left"[^>]*>(.*?)</td>.*?'
                r'(?:<td[^>]*>.*?</td>.*?)?'
                r'(?:<td[^>]*>.*?</td>.*?)?'
                r'<td[^>]*>.*?<span class="price">([\d,]+)</span>원.*?</td>.*?'
                r'(?:<td[^>]*>.*?</td>.*?)?'
                r'<td[^>]*class="state"[^>]*>(.*?)</td>',
                re.DOTALL
            )

            matches = pattern.findall(html)

            for region, date, time_, name, price, caddy in matches:
                try:
                    price_num = int(price.replace(',', ''))
                    caddy_clean = re.sub(r'<[^>]+>', '', caddy).strip()
                    if any(keyword in name for keyword in exclude_keywords):
                        continue
                    all_data.append((region.strip(), date.strip(), time_.strip(), name.strip(), price_num, caddy_clean))
                except:
                    continue
        all_data.sort(key=lambda x: x[4])
        return all_data[:300]
    except Exception:
        with open("부킹정보_log.txt", "w", encoding="utf-8") as f:
            f.write("에러 발생!\n")
            f.write(traceback.format_exc())
        return []

if __name__ == "__main__":
    while True:
        data = get_golf_data()
        if data:
            body = "\n".join([f"{r} | {d} | {t} | {n} | {p}원 | {c}" for r, d, t, n, p, c in data])
            body += f"\n\n총 {len(data)}개 항목이 출력되었습니다."
            send_email("골프 예약 데이터", body)
            print("이메일 전송 완료")
        else:
            send_email("골프 예약 데이터 - 오류", "데이터를 가져오지 못했습니다.")
            print("오류 이메일 전송")

        time.sleep(3600)  # 1시간 대기