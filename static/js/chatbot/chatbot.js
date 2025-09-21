const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".chat-input span");
const chatbox = document.querySelector(".chatbox");
const chatToggler = document.querySelector(".chatbot-toggler");
const chatCloseBtn = document.querySelector(".close-btn");
const initInputHeight = chatInput.scrollHeight;

let chatbot_api;
let userMessage;

// Panggil API Agent
fetch("/chatbot/agent", {
    method: "GET",
})
    .then((response) => {
        if (!response.ok) {
            throw new Error("Network error!");
        }
        return response.json();
    })
    .then((data) => {
        chatbot_api = data.data.agentlinked;
    })
    .catch((error) => {
        console.error(error);
    });

// Convert Markdown
function convertMarkdownLinksToHTML(text) {
    // Link
    text = text.replace(
        /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
        '<a href="$2" target="_blank">$1</a>'
    );

    // Bold (**text**)
    text = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

    // Italic (*text* or _text_)
    text = text.replace(/(?<!\*)\*(?!\*)(.*?)\*(?!\*)/g, "<em>$1</em>");
    text = text.replace(/_(.*?)_/g, "<em>$1</em>");

    // Underline (__text__)
    text = text.replace(/__(.*?)__/g, "<u>$1</u>");

    // Code block ```text```
    text = text.replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>");
    return text;
}

function fillTemplate(type) {
    const textarea = document.querySelector(".chat-input textarea");
    const sendBtn = document.getElementById("send-btn");

    if (type === "keluhan") {
        textarea.value = "Saya ingin membuat keluhan caranya bagaimana ya?";
    } else if (type === "cek_pemesanan") {
        textarea.value = "Saya ingin mengecek status pemesanan";
    }

    // Simulate click on send
    sendBtn.click();
}

const createChatLi = (message, className) => {
    // Create a chat <li> element with passed message and className
    const chatLi = document.createElement("li");
    chatLi.classList.add("chat", className);
    let chatContent =
        className === "outgoing"
            ? `<p>${message}</p>`
            : `<img src='/static/images/logo.png' alt='Logo'><p>${message}</p>`;
    chatLi.innerHTML = chatContent;
    if (className === "incoming") {
        let chatmsg = convertMarkdownLinksToHTML(message);
        chatLi.querySelector("p").innerHTML = chatmsg;
    } else {
        let chatmsg = convertMarkdownLinksToHTML(message);
        chatLi.querySelector("p").innerHTML = chatmsg;
    }
    return chatLi;
};

const generateResponse = (incomingChatLi) => {
    const API_URL = chatbot_api;
    const messageElement = incomingChatLi.querySelector("p");

    const requestOptions = {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            pesan: userMessage,
        }),
    };

    // Send POST request to API, get response
    fetch(API_URL, requestOptions)
        .then((res) => res.json())
        .then((data) => {
            let chatmsg = convertMarkdownLinksToHTML(data.output);
            messageElement.innerHTML = chatmsg;
        })
        .catch((error) => {
            messageElement.textContent =
                "Oops! Something went wrong. Please try again.";
        })
        .finally(() => chatbox.scrollTo(0, chatbox.scrollHeight));
};

const handleChat = () => {
    userMessage = chatInput.value.trim(); // Getting user entered message and removing extra whitespace
    if (!userMessage) return; // If chatInput is empty return from here

    chatInput.value = "";
    chatInput.style.height = `${initInputHeight}px`; // Resetting textarea height to its default height once a message is sent

    // Append the user's message to the chatbox
    chatbox.appendChild(createChatLi(userMessage, "outgoing"));
    chatbox.scrollTo(0, chatbox.scrollHeight); // Auto-scroll to the bottom if chat is overflowing

    setTimeout(() => {
        // Display "Thinking..." message while waiting for the response
        const incomingChatLi = createChatLi("Thinking...", "incoming");
        chatbox.appendChild(incomingChatLi);
        chatbox.scrollTo(0, chatbox.scrollHeight);
        generateResponse(incomingChatLi);
    }, 600);
};

chatInput.addEventListener("input", () => {
    // Adjust the height of the input textarea based on its content
    chatInput.style.height = `${initInputHeight}px`;
    chatInput.style.height = `${chatInput.scrollHeight}px`;
});

chatInput.addEventListener("keyup", (e) => {
    // If Enter key is pressed without Shift key and the window
    // width is greater than 800px, handle the chat
    if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
        e.preventDefault();
        handleChat();
    }
});

sendChatBtn.addEventListener("click", handleChat);
chatCloseBtn.addEventListener("click", () =>
    document.body.classList.remove("show-chatbot")
);
function showchatbot() {
    document.body.classList.toggle("show-chatbot");
}
chatToggler.addEventListener("click", showchatbot);
