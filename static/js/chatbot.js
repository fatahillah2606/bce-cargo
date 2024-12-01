const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".chat-input span");
const chatbox = document.querySelector(".chatbox");
const chatbotToggler = document.querySelector(".chatbot-toggler");
const chatbotCloseBtn = document.querySelector(".close-btn");

const API_URL = "https://fatahillah2606.github.io/bce-cargo/app/bce-cargo.chatbot.json"; // api data perusahaan

let companyInfo; // Untuk menyimpan informasi perusahaan

fetch(API_URL)
  .then((res) => {
    if (!res.ok) {
      throw new Error(`HTTP error! Status: ${res.status}`);
    }
    return res.json();
  })
  .then((data) => (companyInfo = data))
  .catch((error) => console.error("Unable to fetch data:", error));

// Pesan pengguna
let userMessage;

const inputInitHeight = chatInput.scrollHeight;

const createChatLi = (message, className) => {
  // Membuat elemen <li> dengan pesan yang diteruskan dan className
  const chatLi = document.createElement("li");
  chatLi.classList.add("chat", className);
  let chatContent =
    className === "outgoing"
      ? `<p></p>`
      : `<span class="material-symbols-rounded">smart_toy</span><p></p>`;
  chatLi.innerHTML = chatContent;
  chatLi.querySelector("p").textContent = message;
  return chatLi;
};

const generateResponse = async (incomingChatLi) => {
  const messageElement = incomingChatLi.querySelector("p");

  // Cek apakah companyInfo sudah terisi
  if (!companyInfo || Object.keys(companyInfo).length === 0) {
    console.log("Company Info is empty");
    messageElement.textContent = "Maaf, informasi perusahaan tidak tersedia.";
    return;
  }

  //Jawab pertanyaan client
  companyInfo.forEach((jawaban, index, array) => {
    let pertanyaan = jawaban["command"];
    // Tangani jika pertanyaan dalam bentuk Array pada database
    if (Array.isArray(jawaban["command"])) {
      pertanyaan.forEach((kataKunci) => {
        if (userMessage.toLowerCase().includes(kataKunci.toLowerCase())) {
          prosesJawaban(array.indexOf(jawaban));
        }
      });
    } else if (userMessage.toLowerCase().includes(pertanyaan.toLowerCase())) {
      prosesJawaban(array.indexOf(jawaban));
    }
  });

  function prosesJawaban(index) {
    let responJawaban = companyInfo[index]["response"];
    // Jika jawaban berupa array
    if (Array.isArray(responJawaban)) {
      messageElement.textContent = responJawaban
        .map((item, index) => `${index + 1}. ${item}`)
        .join("\n");

      // Jika jawaban berupa Object
    } else if (typeof responJawaban === "object" && responJawaban !== null) {
      messageElement.innerHTML = Object.entries(responJawaban)
        .map(([key, value]) => `<b>${key}</b>: ${value}`)
        .join("\n");

      // Jika jawaban berupa String atau sejenisnya
    } else {
      messageElement.textContent =
        responJawaban || "Maaf, aku tidak punya informasi tentang itu.";
    }
  }
  // Scroll chatbox ke bawah setelah menampilkan pesan
  chatbox.scrollTo(0, chatbox.scrollHeight);
};

const handleChat = async () => {
  userMessage = chatInput.value.trim(); // Supaya gak ada spasi lebih
  if (!userMessage) return;
  chatInput.value = "";
  chatInput.style.height = `${inputInitHeight}px`;

  // Menambahkan pesan pengguna ke chatbox
  chatbox.appendChild(createChatLi(userMessage, "outgoing"));
  chatbox.scrollTo(0, chatbox.scrollHeight);

  setTimeout(async () => {
    // Menampilkan delay bot untuk merespon pengguna
    const incomingChatLi = createChatLi(
      "Maaf saya tidak mengerti :)",
      "incoming"
    );
    chatbox.scrollTo(0, chatbox.scrollHeight);
    chatbox.appendChild(incomingChatLi); // Menambahkan elemen <li> ke chatbox
    await generateResponse(incomingChatLi);
  }, 10);
};

chatInput.addEventListener("input", () => {
  chatInput.style.height = `${inputInitHeight}px`;
  chatInput.style.height = `${chatInput.scrollHeight}px`;
});

chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
    e.preventDefault();
    handleChat();
  }
});

sendChatBtn.addEventListener("click", handleChat);
chatbotCloseBtn.addEventListener("click", () =>
  document.body.classList.remove("show-chatbot")
);
chatbotToggler.addEventListener("click", () =>
  document.body.classList.toggle("show-chatbot")
);
