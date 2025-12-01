## TresGo - Video Interview Platform

**TresGo** là một nền tảng phỏng vấn video trực tuyến đơn giản, cho phép ứng viên quay video trả lời câu hỏi và tự động upload lên server theo thời gian thực.

![Demo Screenshot](static/screenshot_demo.png) *(Bạn nhớ chụp ảnh màn hình web và để vào folder static nhé)*

## Tính năng nổi bật (Features)
* **Sequential Recording:** Quy trình phỏng vấn tuần tự (Câu 1 -> Câu 2 -> ...).
* **Real-time Upload:** Video được upload ngay sau khi kết thúc mỗi câu hỏi (tránh mất dữ liệu).
* **Auto-Naming:** Hệ thống tự động tổ chức thư mục lưu trữ theo tên ứng viên và thời gian (`DD_MM_YYYY...`).
* **Speech-to-Text (Bonus):** Tích hợp OpenAI Whisper để tự động tạo transcript từ video.
* **Token Authentication:** Cơ chế xác thực ứng viên bằng mã dự thi.

## 🛠 Công nghệ sử dụng (Tech Stack)
* **Backend:** Python, FastAPI, Uvicorn.
* **Frontend:** Vanilla JS, HTML5, CSS3 (Fetch API, MediaRecorder API).
* **Utilities:** FFmpeg, OpenAI Whisper (AI).

## Installation

1.  **Clone dự án:**
    ```bash
    git clone [https://github.com/username-cua-ban/TresGo.git](https://github.com/username-cua-ban/TresGo.git)
    cd TresGo/backend
    ```

2.  **Cài đặt thư viện:**
    ```bash
    pip install fastapi uvicorn python-multipart pytz openai-whisper
    ```
    *(Lưu ý: Cần tải `ffmpeg.exe` và đặt vào thư mục gốc của project)*

3.  **Chạy Server:**
    ```bash
    python main.py
    ```

4.  **Truy cập:**
    Mở trình duyệt tại: `http://127.0.0.1:8002`

## Nhóm phát triển
Dự án được thực hiện bởi nhóm 3 thành viên (Team TresGo):
* Nguyen Thi Thuy Linh
* Vu Kim Minh
* Pham Mai Phuong