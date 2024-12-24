from flask import Flask, request, session
import csv
from datetime import datetime

with open("attendance.csv", mode="a", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["test_student", datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M:%S"), "출근"])

app = Flask(__name__)
app.secret_key = "secret_key_for_session_management"  # 세션 관리 키

# 출석 기록 확인 함수
def has_already_checked_in(student_id, check_type):
    try:
        with open("attendance.csv", mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            today_date = datetime.now().strftime("%Y-%m-%d")
            for row in reader:
                if row[0] == student_id and row[1] == today_date and row[3] == check_type:
                    return True
    except FileNotFoundError:
        print("File not found.")
    return False

@app.route("/")
def home():
    now = datetime.now()
    formatted_date = now.strftime("%Y년 %m월 %d일 %A").replace("Monday", "월요일").replace("Tuesday", "화요일").replace("Wednesday", "수요일").replace("Thursday", "목요일").replace("Friday", "금요일").replace("Saturday", "토요일").replace("Sunday", "일요일")
    current_time = now.strftime("%p %I:%M")  # 현재 시간 (AM/PM 형식)
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>IPUD 2025-1 출석부</title>
        <style>
            body {{
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                font-family: Arial, sans-serif;
                background-color: #f9f9f9;
            }}
            .container {{
                text-align: center;
                background: white;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                border: 2px solid #007BFF; /* 전체를 둘러싼 파란색 테두리 */
            }}
            button {{
                font-size: 1.5em;
                padding: 10px 20px;
                border: none;
                border-radius: 30px;
                margin: 2px;
            }}
            .check-in {{
                background-color: #00E676;
                color: white;
            }}
            .check-out {{
                background-color: #5592FC;
                color: white;
            }}
            .highlight {{
                color: #5592FC; /* 파란색 */
                font-weight: bold;
            }}
            .label {{
                font-weight: bold; /* 전체 굵게 */
            }}
            .date {{
                color: gray;
                font-size: 0.8em;
                margin-bottom: 2px; /* 간격 줄임 */
            }}
            .time {{
                color: black;
                font-size: 1.5em;
                font-weight: bold;
                margin-top: 0; /* 추가 간격 제거 */
            }}
            .result-container {{
                text-align: center;
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                border: 2px solid #007BFF;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 50vh;
                margin: 0;
            }}
            .result-container h1 {{
                font-size: 1em; /* 글씨 크기 줄임 */
                text-align: center; /* 중앙 정렬 */
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>IPUD 2025-1 출석부</h1>
            <form style="display: inline;" action="/check_in" method="post">
                <label class="label" for="student_id"><span class="highlight">학번</span>을 입력해주세요:</label><br>
                <input type="text" id="student_id" name="student_id" required><br><br>
                <p class="date">{formatted_date}</p>
                <p class="time">{current_time}</p>
                <button type="submit" class="check-in">출근</button>
            </form>
            <form style="display: inline;" action="/check_out" method="post">
                <input type="hidden" id="student_id" name="student_id" value="">
                <button type="submit" class="check-out" disabled id="check_out_button">퇴근</button>
            </form>
        </div>
        <script>
            document.getElementById("student_id").addEventListener("input", function() {{
                document.getElementById("check_out_button").disabled = false;
            }});
        </script>
    </body>
    </html>
    """

@app.route("/check_in", methods=["POST"])
def check_in():
    student_id = request.form["student_id"]
    now = datetime.now()
    current_time = now.strftime("%p %I:%M")
    current_hour = now.hour

    if current_hour < 8:
        return f"""
        <div class='result-container'>
            <h1>출근 시간이 아닙니다. (출근 가능 시간: 08:00 ~ 22:00)</h1>
        </div>
        """

    if current_hour >= 22:
        return f"""
        <div class='result-container'>
            <h1>출근 기록은 22시까지 가능합니다.</h1>
        </div>
        """

    if has_already_checked_in(student_id, "출근"):
        return f"""
        <div class='result-container'>
            <h1>이미 출근 기록이 있습니다.</h1>
        </div>
        """

    with open("attendance.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([student_id, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), "출근"])
    session["checked_in"] = True
    return f"""
    <div class='result-container'>
        <h1>✅ 출근 완료!</h1>
        <p>학번 <b>{student_id}</b>님의 출근이 기록되었습니다.</p>
        <p>출근 시간: <b>{current_time}</b></p>
    </div>
    """

@app.route("/check_out", methods=["POST"])
def check_out():
    student_id = request.form["student_id"]
    now = datetime.now()
    current_time = now.strftime("%p %I:%M")
    current_hour = now.hour

    if not session.get("checked_in"):
        return f"""
        <div class='result-container'>
            <h1>출근 기록이 없습니다. 먼저 출근을 기록해주세요.</h1>
        </div>
        """

    if current_hour < 8 or current_hour >= 22:
        return f"""
        <div class='result-container'>
            <h1>퇴근 시간이 아닙니다. (퇴근 가능 시간: 08:00 ~ 22:00)</h1>
        </div>
        """

    if has_already_checked_in(student_id, "퇴근"):
        return f"""
        <div class='result-container'>
            <h1>이미 퇴근 기록이 있습니다.</h1>
        </div>
        """

    with open("attendance.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([student_id, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), "퇴근"])
    return f"""
    <div class='result-container'>
        <h1>✅ 퇴근 완료!</h1>
        <p>학번 <b>{student_id}</b>님의 퇴근이 기록되었습니다.</p>
        <p>퇴근 시간: <b>{current_time}</b></p>
    </div>
    """

if __name__ == "__main__":
    app.run(debug=True)
