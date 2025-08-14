const API_URL = "http://127.0.0.1:8765/api";
const HEALTH_CHECK_TEXT = "test connection";

const inputEl = document.getElementById("input");
const sendBtn = document.getElementById("send");
const outputEl = document.getElementById("output");
const modeSel = document.getElementById("mode");
const connPill = document.getElementById("conn-pill");
const modalBg = document.getElementById("modal-bg");
const modalText = document.getElementById("modal-text");
const modalYes = document.getElementById("modal-yes");
const modalNo = document.getElementById("modal-no");

let divePendingText = "";
let lastUserText = "";
let isProcessing = false;

// Connection status check
async function checkConnection() {
    connPill.textContent = "Checking...";
    connPill.className = "pill checking";
    
    try {
        const res = await fetch(API_URL, { 
            method: "POST", 
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: HEALTH_CHECK_TEXT })
        });
        
        if (res.ok) {
            connPill.textContent = "Online";
            connPill.className = "pill online";
        } else {
            throw new Error("Server error");
        }
    } catch (error) {
        connPill.textContent = "Offline";
        connPill.className = "pill offline";
    }
}

// Initial connection check + every 30 seconds
checkConnection();
setInterval(checkConnection, 30000);

// Event listeners
sendBtn.addEventListener("click", () => sendQuery());
inputEl.addEventListener("keypress", e => { 
    if (e.key === "Enter" && !e.shiftKey) { 
        e.preventDefault(); 
        sendQuery(); 
    }
});

modalYes.addEventListener("click", async () => {
    modalBg.style.display = "none";
    await postToAPI(divePendingText, true);
});

modalNo.addEventListener("click", () => {
    modalBg.style.display = "none";
    outputEl.textContent = "Understood. I'll stick with what I have for now.";
    isProcessing = false;
    sendBtn.disabled = false;
});

// Main query function
async function sendQuery() {
    const text = inputEl.value.trim();
    if (!text || isProcessing) return;
    
    lastUserText = text;
    isProcessing = true;
    sendBtn.disabled = true;
    outputEl.textContent = "Thinking...";
    inputEl.value = "";
    
    await postToAPI(text, false);
}

// Send API request
async function postToAPI(text, dive_confirmed) {
    const mode = modeSel.value;
    try {
        const payload = { 
            text, 
            dive_confirmed, 
            domain: null,
            mode: mode
        };
        
        const res = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        
        if (!res.ok) throw new Error(`Server error: ${res.status}`);
        const data = await res.json();
        handleResponse(data, text);
        
    } catch (error) {
        outputEl.textContent = offlineFallback(text);
        connPill.textContent = "Offline";
        connPill.className = "pill offline";
    } finally {
        isProcessing = false;
        sendBtn.disabled = false;
    }
}

// Handle backend response
function handleResponse(data, userText) {
    if (data.status === "ok") {
        outputEl.textContent = data.answer || "(no answer provided)";
    } else if (data.status === "needs_deeper") {
        divePendingText = userText;
        modalText.textContent = data.prompt || "Would you like me to dive deeper?";
        modalBg.style.display = "flex";
    } else if (data.status === "clarify") {
        outputEl.textContent = `${data.question || "Could you clarify your question?"}`;
    } else if (data.status === "error") {
        outputEl.textContent = `Error: ${data.message || "Unknown error"}`;
    } else {
        outputEl.textContent = `(Unexpected response)`;
    }
}

// Offline fallback
function offlineFallback(text) {
    const lowerText = text.toLowerCase();
    const capitals = {
        florida: "Tallahassee",
        texas: "Austin", 
        california: "Sacramento",
        "new york": "Albany",
        connecticut: "Hartford"
    };
    for (const state in capitals) {
        if (lowerText.includes(state) && lowerText.includes("capital")) {
            return `The capital of ${state} is ${capitals[state]}. (offline mode)`;
        }
    }
    if (lowerText.includes("2+2") || lowerText.includes("2 + 2")) return "2 + 2 = 4 (offline)";
    return "I can't reach the AI backend right now.";
}
