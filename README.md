## TresGo - Video Interview Platform

**TresGo** is a lightweight online video interview platform that lets candidates record responses to interview questions and automatically upload them to the server in real-time.

![Demo Screenshot](static/screenshot_demo.png)  
*(Make sure to capture a screenshot of the web app and place it in the `static` folder.)*

## Key Features

* **Sequential Recording:** Conduct interviews step-by-step (Question 1 → Question 2 → ...).  
* **Real-time Upload:** Videos are uploaded immediately after each question, preventing any data loss.  
* **Automatic Folder Organization:** Videos are saved in folders automatically named by candidate and timestamp (`DD_MM_YYYY...`).  
* **Speech-to-Text (Optional):** Integrates OpenAI Whisper to generate video transcripts automatically.  
* **Token-Based Authentication:** Secure candidate verification using unique exam tokens.  

## 🛠 Tech Stack

* **Backend:** Python, FastAPI, Uvicorn  
* **Frontend:** Vanilla JS, HTML5, CSS3 (Fetch API, MediaRecorder API)  
* **Utilities & AI:** FFmpeg, OpenAI Whisper  
