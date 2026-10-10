const log = document.getElementById("log");
const input = document.getElementById("in");
const sendButton = document.getElementById("send-button");
function addMessage(text, type) {

    const message = document.createElement("div");
    message.className = `message ${type}`;

    if (type === "bot") {

        message.innerHTML = `
            <div class="avatar">✦</div>
            <div class="message-content">
                <div class="message-name">
                    GlowSkin AI
                </div>
                <div class="message-text"></div>
            </div>
        `;
        message.querySelector(".message-text").textContent = text;
    } else {
        message.innerHTML = `
            <div class="message-content">
                <div class="message-text"></div>
            </div>
        `;
        message.querySelector(".message-text").textContent = text;
    }

    log.appendChild(message);
    log.scrollTop = log.scrollHeight;
}

async function sendMessage() {
    const text = input.value.trim();
    if (!text) {
        return;
    }

    addMessage(text, "user");
    input.value = "";
    sendButton.disabled = true;
    sendButton.textContent = "Thinking...";

    try {

        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: text
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Server error"
            );
        }

        addMessage(
            data.reply,
            "bot"
        );

    } catch (error) {
        console.error("Chat error:", error);
        addMessage(
            "ERROR: " + error.message,
            "bot"
        );
    }

    finally {
        sendButton.disabled = false;
        sendButton.textContent = "Send";
        input.focus();
    }
}

sendButton.addEventListener(
    "click",
    sendMessage
);

input.addEventListener(
    "keydown",
    function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();

        }
    }
);