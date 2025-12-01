/**
 * TRESGO - REAL BACKEND INTEGRATION (ENGLISH)
 */

// Retrieve info from Login page
const interviewToken = localStorage.getItem('userToken');
const folderName = localStorage.getItem('sessionFolder');
const userName = localStorage.getItem('userName');

// Redirect if not logged in
if (!interviewToken || !folderName) {
    alert("Please log in first!");
    window.location.href = '/static/login.html';
}

const MAX_QUESTIONS = 5;
let currentQuestionIndex = 0;
let mediaRecorder;
let recordedChunks = [];
let stream;

// DOM Elements
const videoPreview = document.getElementById("camera-preview");
const permissionPrompt = document.getElementById("permission-prompt");
const questionTitle = document.getElementById("question-title");
const questionText = document.getElementById("question-text");
const loadingIndicator = document.getElementById("loading-indicator");
const uploadError = document.getElementById("upload-error");
const nextButton = document.getElementById("next-button");
const finishButton = document.getElementById("finish-button");
const retryButton = document.getElementById("retry-button");

// Question List (Translated to English)
const questions = [
    "Please introduce yourself and explain why you are interested in this position?",
    "What is your experience with handling network errors and file uploads in web projects?",
    "In your opinion, why is HTTPS important for a web application requiring camera/microphone access?",
    "Describe the process you would use to ensure video upload even with temporary network failures.",
    "Do you have any questions for us?",
];

// --- UI FUNCTIONS ---
function updateQuestionUI() {
    questionTitle.textContent = `Question ${currentQuestionIndex + 1}/${MAX_QUESTIONS}`;
    questionText.textContent = questions[currentQuestionIndex];

    if (currentQuestionIndex === MAX_QUESTIONS - 1) {
        nextButton.textContent = "Complete Interview";
        nextButton.classList.remove("hidden");
        finishButton.classList.add("hidden");
    } else {
        nextButton.textContent = "Next Question";
        finishButton.classList.add("hidden");
    }
}

function showLoading(message) {
    loadingIndicator.querySelector('span').textContent = message;
    loadingIndicator.classList.remove("hidden");
    uploadError.classList.add("hidden");
    nextButton.disabled = true;
    retryButton.disabled = true;
}

function hideStatus() {
    loadingIndicator.classList.add("hidden");
    uploadError.classList.add("hidden");
    nextButton.disabled = false;
}

function showError(message) {
    loadingIndicator.classList.add("hidden");
    uploadError.querySelector('span').textContent = message;
    uploadError.classList.remove("hidden");
    nextButton.disabled = true;
    retryButton.disabled = false;
}

// --- RECORDING LOGIC ---
async function startRecording() {
    recordedChunks = [];
    const options = { mimeType: 'video/webm;codecs=vp8,opus' };
    
    try {
        mediaRecorder = new MediaRecorder(stream, options);
    } catch (e) {
        mediaRecorder = new MediaRecorder(stream); // Fallback
    }

    mediaRecorder.ondataavailable = event => {
        if (event.data.size > 0) recordedChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
        console.log("Recording stopped, preparing upload...");
        await handleUpload();
    };

    mediaRecorder.start();
    console.log("Recording started...");
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }
}

// --- UPLOAD LOGIC ---
async function handleUpload() {
    const videoBlob = new Blob(recordedChunks, { type: 'video/webm' });
    
    const formData = new FormData();
    formData.append('token', interviewToken);
    formData.append('folder', folderName);
    formData.append('questionIndex', currentQuestionIndex + 1);
    formData.append('video', videoBlob, `Q${currentQuestionIndex + 1}.webm`);

    showLoading(`Uploading Question ${currentQuestionIndex + 1}...`);

    try {
        const response = await fetch('/api/upload-one', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error("Server returned error " + response.status);

        console.log("Upload successful!");
        proceedToNextQuestion();

    } catch (error) {
        console.error("Upload error:", error);
        showError("Upload failed: " + error.message);
        
        retryButton.onclick = () => {
            uploadError.classList.add("hidden");
            handleUpload(); // Retry upload
        };
    }
}

function proceedToNextQuestion() {
    hideStatus();
    currentQuestionIndex++;
    
    if (currentQuestionIndex < MAX_QUESTIONS) {
        updateQuestionUI();
        startRecording(); // Auto start next question
    } else {
        // All questions finished
        nextButton.classList.add("hidden");
        finishButton.classList.remove("hidden");
        finishButton.disabled = false;
        
        questionTitle.textContent = "Completed!";
        questionText.textContent = "You have answered all questions. Please click Finish to complete the session.";
        stopRecording();
        if(stream) stream.getTracks().forEach(track => track.stop());
    }
}

async function sessionFinish() {
    showLoading("Finalizing interview...");
    try {
        await fetch('/api/session/finish', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                token: interviewToken, 
                folder: folderName, 
                questionsCount: currentQuestionIndex 
            })
        });
        alert("Thank you! Your interview has been saved successfully.");
        window.location.href = "/static/index.html"; // Back to home
    } catch (e) {
        alert("Finish error: " + e.message);
    }
}

// --- INIT ---
async function init() {
    permissionPrompt.classList.remove("hidden");
    
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        videoPreview.srcObject = stream;
        permissionPrompt.classList.add("hidden");
        
        nextButton.addEventListener("click", () => {
            stopRecording(); // Stop -> Upload -> Next
        });

        finishButton.addEventListener("click", sessionFinish);

        updateQuestionUI();
        startRecording();

    } catch (error) {
        permissionPrompt.querySelector('p').textContent = "Error: Cannot access Camera/Microphone.";
        console.error(error);
    }
}

document.addEventListener("DOMContentLoaded", init);