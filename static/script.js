let isVoiceMode = false;

function toggleVoiceMode() {
    isVoiceMode = document.getElementById('voiceToggle').checked;
}

function sendMessage() {
    const userInput = document.getElementById("userInput").value.trim();
    if (userInput === "") return;

    appendMessage("You", userInput, "user-msg");

    fetch("/get", {
        method: "POST",
        body: JSON.stringify({ message: userInput }),
        headers: { "Content-Type": "application/json" }
    })
    .then(res => res.json())
    .then(data => {
        appendMessage("Bot", data.response, "bot-msg");
        if (isVoiceMode) speakResponse(data.response);
    });

    document.getElementById("userInput").value = "";
}

function appendMessage(sender, message, className) {
    const chatBox = document.getElementById("chat-box");
    const msgDiv = document.createElement("div");
    msgDiv.className = className;
    msgDiv.innerText = `${sender === "You" ? "" : ""}${message}`;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function speakResponse(text) {
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    synth.speak(utterance);
}
