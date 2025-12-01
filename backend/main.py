print("---- CODE ĐANG CHẠY, VUI LÒNG ĐỢI... ----")

import os
import json
import shutil
import re
from datetime import datetime
import pytz
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel
import whisper

# ==============================
# CẤU HÌNH FASTAPI
# ==============================
app = FastAPI(title="TRESGO", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent

# Thư mục uploads
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Timezone VN
try:
    VN_TZ = pytz.timezone('Asia/Bangkok')
except:
    VN_TZ = datetime.now().astimezone().tzinfo

# ==============================
# CẤU HÌNH STATIC FILES (Đoạn này đã đúng rồi)
# ==============================
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

# Serve static folder: HTML, CSS, IMG
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ==============================
# LOAD MODEL WHISPER
# ==============================
print("--- ĐANG TẢI MODEL AI (WHISPER)... VUI LÒNG ĐỢI 1-2 PHÚT ---")
try:
    stt_model = whisper.load_model("base")
    print("--- ĐÃ TẢI XONG MODEL! ---")
except Exception as e:
    print(f"Lỗi tải model Whisper: {e}")
    stt_model = None

# ==============================
# TOKEN
# ==============================
VALID_TOKENS = {
    "DEV_TEAM_KEY_2025": "Administrator",
    "TEACHER_KEY": "Tran Hung",
    "11247188": "Nguyen Thi Thuy Linh",
    "11247205": "Vu Kim Minh",
    "11247218": "Pham Mai Phuong",
    "user_guest": "User Khách 1"
}

# ==============================
# MODELS
# ==============================
class TokenCheck(BaseModel):
    token: str

class SessionStart(BaseModel):
    token: str
    userName: str

class SessionFinish(BaseModel):
    token: str
    folder: str
    questionsCount: int


# ==============================
# HÀM PHỤ
# ==============================
def generate_folder_name(user_name: str) -> str:
    now = datetime.now(VN_TZ)
    time_str = now.strftime("%d_%m_%Y_%H_%M")
    safe_name = re.sub(r'[^a-zA-Z0-9]', '_', user_name)
    return f"{time_str}_{safe_name}"

def update_metadata(folder_path: Path, data: dict):
    meta_path = folder_path / "meta.json"
    current_meta = {}
    if meta_path.exists():
        try:
            with meta_path.open("r", encoding="utf-8") as f:
                current_meta = json.load(f)
        except:
            pass
    current_meta.update(data)
    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(current_meta, f, ensure_ascii=False, indent=2)


# NHIỆM VỤ STT CHẠY NGẦM (AUTO DETECT ANH/VIỆT)
# ==============================
# ==============================
# BACKGROUND STT TASK (ROBUST VERSION)

def run_stt_task(video_path: str, folder_path: Path, question_index: int):
    if stt_model is None:
        return

    try:
        # 1. Kiểm tra file rỗng (Giữ nguyên để tránh lỗi)
        if os.path.getsize(video_path) < 1000: 
            print(f"--> [Skip] Câu {question_index}: Video lỗi/rỗng.")
            return

        print(f"--> Đang xử lý STT câu {question_index} (Tối ưu Prompt)...")

        # 2. Cấu hình "Thần thánh" để tăng độ nhạy
        result = stt_model.transcribe(
            str(video_path), 
            fp16=False, # Bắt buộc False nếu chạy CPU
            
            # --- BÍ KÍP 1: Prompt chứa từ khóa ---
            # Liệt kê trước các từ có thể xuất hiện để AI "bắt sóng" nhanh hơn
            initial_prompt=(
                "Đây là buổi phỏng vấn trực tiếp, interview context. The candidate answers in Vietnamese or English. "
                "Keywords: xin chào, giới thiệu, kinh nghiệm, IT, programming, "
                "teamwork, kỹ năng, development, project, mục tiêu, cảm ơn."
            ),
            
            # --- BÍ KÍP 2: Tham số chặt chẽ ---
            condition_on_previous_text=False, # Không cho AI nhìn lại câu trước (tránh lặp)
            temperature=0.0,      # =0 nghĩa là: "Hãy chọn đáp án chắc chắn nhất, đừng đoán mò"
            beam_size=2,          # =2: Tìm kiếm kỹ hơn 1 chút (Mặc định là 1). Tăng lên 5 sẽ rất chậm.
            patience=1.0,         # Kiên nhẫn chờ đợi kết quả tốt
            
            # --- BÍ KÍP 3: Hỗ trợ tiếng Việt tốt hơn ---
            # Nếu bạn nói tiếng Việt là chính, có thể bỏ comment dòng dưới để ép Tiếng Việt (sẽ chuẩn hơn nhiều)
            # language='vi' 
        )
        
        text_content = result["text"].strip()
        
        # In ra để Debug
        print(f"   + RAW: '{text_content}'")

        # Lọc rác (Hallucination)
        bad_phrases = ["Subtitles by", "Amara.org", "Thank you", "Watching"]
        if not text_content or any(phrase in text_content for phrase in bad_phrases):
             # Nếu AI đoán sai ra mấy câu vô nghĩa, ta ghi log nhẹ nhàng
             if len(text_content) < 5: 
                 text_content = "[Âm thanh không rõ lời]"

        # Ghi file
        transcript_path = folder_path / "transcript.txt"
        timestamp = datetime.now(VN_TZ).strftime("%H:%M:%S")
        log_line = f"[{timestamp}] Question {question_index}:\n{text_content}\n{'-'*30}\n"

        with open(transcript_path, "a", encoding="utf-8") as f:
            f.write(log_line)

        print(f"--> Xong câu {question_index}")

    except Exception as e:
        print(f"Lỗi STT câu {question_index}: {e}")
# ==============================
# ROUTES
# ==============================

@app.get("/", response_class=HTMLResponse)
def home():
    """Trả về trang HTML chính từ static/index.html"""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>LỖI: Chưa có file index.html trong thư mục static/</h1>")

@app.post("/api/verify-token")
async def verify_token(data: TokenCheck):
    if data.token in VALID_TOKENS:
        return {"ok": True}
    raise HTTPException(status_code=401, detail="Token không hợp lệ")

@app.post("/api/session/start")
async def start_session(data: SessionStart):
    if data.token not in VALID_TOKENS:
        raise HTTPException(status_code=401)

    folder_name = generate_folder_name(data.userName)
    session_path = UPLOAD_DIR / folder_name
    session_path.mkdir(parents=True, exist_ok=True)

    init_meta = {
        "userName": data.userName,
        "startTime": datetime.now(VN_TZ).isoformat(),
        "status": "started",
        "files": []
    }
    update_metadata(session_path, init_meta)
    return {"ok": True, "folder": folder_name}

@app.post("/api/upload-one")
async def upload_one(
    background_tasks: BackgroundTasks,
    token: str = Form(...),
    folder: str = Form(...),
    questionIndex: int = Form(...),
    video: UploadFile = File(...)
):
    if token not in VALID_TOKENS:
        raise HTTPException(status_code=401)

    session_path = UPLOAD_DIR / folder
    if not session_path.exists():
        raise HTTPException(status_code=404)

    file_name = f"Q{questionIndex}.webm"
    dest = session_path / file_name

    try:
        with dest.open("wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    meta_path = session_path / "meta.json"
    if meta_path.exists():
        with meta_path.open("r", encoding="utf-8") as f:
            meta = json.load(f)
        if "files" not in meta:
            meta["files"] = []
        meta["files"].append({
            "questionIndex": questionIndex,
            "fileName": file_name,
            "uploadedAt": datetime.now(VN_TZ).isoformat()
        })
        with meta_path.open("w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    # chạy ngầm STT
    background_tasks.add_task(run_stt_task, str(dest), session_path, questionIndex)

    return JSONResponse({"ok": True, "savedAs": file_name})

@app.post("/api/session/finish")
async def finish_session(data: SessionFinish):
    session_path = UPLOAD_DIR / data.folder
    update_metadata(session_path, {
        "status": "finished",
        "totalQuestions": data.questionsCount,
        "endTime": datetime.now(VN_TZ).isoformat()
    })
    return {"ok": True}


# ==============================
# CHẠY SERVER
# ==============================
if __name__ == "__main__":
    import uvicorn
    print("=====================================================")
    print("   SERVER STT ĐANG KHỞI ĐỘNG TẠI CỔNG 8002... ")
    print("   HÃY TRUY CẬP: http://127.0.0.1:8002")
    print("=====================================================")
    uvicorn.run(app, host="127.0.0.1", port=8002, reload=False)