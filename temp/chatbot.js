const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".chat-input span");
const chatbox = document.querySelector(".chatbox");
const chatbotToggler = document.querySelector(".chatbot-toggler");
const chatbotCloseBtn = document.querySelector(".close-btn");

const FILE_URL = "http://127.0.0.1:5000/botinfo"; // URL file info.txt

let companyInfo = {}; // Untuk menyimpan informasi perusahaan

// Fungsi untuk mengambil data dari info.txt
const fetchCompanyInfo = async () => {
  try {
    const response = await fetch(FILE_URL);
    const text = await response.text();
    companyInfo = processCompanyInfo(text);
  } catch (error) {
    console.error("Error fetching company info:", error);
    companyInfo = {}; // Set default jika fetch gagal
  }
};

// Fungsi untuk memproses teks info.txt menjadi objek
const processCompanyInfo = (text) => {
  const lines = text.split("\n");
  const info = {};

  lines.forEach((line) => {
    // console.log("Processing line:", line); // Log setiap baris untuk memeriksa formatnya
    if (line.startsWith("CV. BAHTERA CAHAYA EXPRESS")) {
      info.overview = line.replace("CV. BAHTERA CAHAYA EXPRESS", "").trim();
    } else if (line.startsWith("Halo :")) {
      info.halo = line.replace("Halo :", "").trim();
    } else if (line.startsWith("Hi :")) {
      info.hi = line.replace("Hi :", "").trim();
    } else if (line.startsWith("Pagi :")) {
      info.pagi = line.replace("Pagi :", "").trim();
    } else if (line.startsWith("Siang :")) {
      info.siang = line.replace("Siang :", "").trim();
    } else if (line.startsWith("Sore :")) {
      info.sore = line.replace("Sore :", "").trim();
    } else if (line.startsWith("Malam :")) {
      info.malam = line.replace("Malam :", "").trim();
    } else if (line.startsWith("Alamat :")) {
      info.alamat = line.replace("Alamat :", "").trim();
    } else if (line.startsWith("Head Office :")) {
      info.headOffice = line.replace("Head Office :", "").trim();
    } else if (line.startsWith("Field Office :")) {
      info.fieldOffice = line.replace("Field Office :", "").trim();
    } else if (line.startsWith("Contact Telp/WhatsApp :")) {
      info.contact = line.replace("Contact Telp/WhatsApp :", "").trim();
    } else if (line.startsWith("E-Mail :")) {
      info.email = line.replace("E-Mail :", "").trim();
    } else if (line.startsWith("Tentang Kami/About Us :")) {
      info.aboutUs = line.replace("Tentang Kami/About Us :", "").trim();
    } else if (line.startsWith("VISI :")) {
      info.vision = line.replace("VISI :", "").trim();
    } else if (line.startsWith("MISI :")) {
      info.mission = line.replace("MISI :", "").trim();
    } else if (line.startsWith("LEGALITAS :")) {
      info.legalitas = line.replace("LEGALITAS :", "").trim();
    } else if (line.startsWith("LAYANAN :")) {
      info.services = line.replace("LAYANAN :", "").trim();
    }
  });
  // console.log("Processed info:", info); // Log info yang sudah diproses
  return info;
};

// Panggil fungsi fetchCompanyInfo() ketika halaman dimuat
fetchCompanyInfo();

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

  console.log("User Message:", userMessage);
  console.log("Company Info:", companyInfo);

  // Sesuaikan respons berdasarkan input pengguna
  if (userMessage.toLowerCase().includes("overview")) {
    messageElement.textContent =
      companyInfo.overview || "Maaf, aku tidak punya informasi tentang itu.";
  } else if (userMessage.toLowerCase().includes("halo")) {
    messageElement.textContent =
      companyInfo.halo || "Maaf, aku tidak punya informasi tentang itu.";
  } else if (userMessage.toLowerCase().includes("hi")) {
    messageElement.textContent =
      companyInfo.hi || "Maaf, aku tidak punya informasi tentang itu.";
  } else if (
    userMessage.toLowerCase().includes("pagi") ||
    userMessage.toLowerCase().includes("selamat pagi")
  ) {
    messageElement.textContent =
      companyInfo.pagi || "Maaf, aku tidak punya informasi tentang itu.";
  } else if (
    userMessage.toLowerCase().includes("siang") ||
    userMessage.toLowerCase().includes("selamat siang")
  ) {
    messageElement.textContent =
      companyInfo.siang || "Maaf, aku tidak punya informasi tentang itu.";
  } else if (
    userMessage.toLowerCase().includes("sore") ||
    userMessage.toLowerCase().includes("selamat sore")
  ) {
    messageElement.textContent =
      companyInfo.sore || "Maaf, aku tidak punya informasi tentang itu.";
  } else if (
    userMessage.toLowerCase().includes("malam") ||
    userMessage.toLowerCase().includes("selamat malam")
  ) {
    messageElement.textContent =
      companyInfo.malam || "Maaf, aku tidak punya informasi tentang itu.";
  } else if (userMessage.toLowerCase().includes("alamat")) {
    messageElement.textContent =
      companyInfo.alamat || "Maaf, aku tidak punya informasi tentang itu.";
  } else if (
    userMessage.toLowerCase().includes("head office") ||
    userMessage.toLowerCase().includes("kantor pusat")
  ) {
    messageElement.textContent =
      companyInfo.headOffice || "Maaf, aku tidak punya informasi tentang itu.";
  } else if (
    userMessage.toLowerCase().includes("field office") ||
    userMessage.toLowerCase().includes("kantor lapangan")
  ) {
    messageElement.textContent =
      companyInfo.fieldOffice || "Maaf, aku tidak punya informasi tentang itu.";
  } else if (
    userMessage.toLowerCase().includes("contact") ||
    userMessage.toLowerCase().includes("kontak")
  ) {
    messageElement.textContent =
      companyInfo.contact || "Maaf, aku tidak punya informasi tentang itu.";
  } else if (userMessage.toLowerCase().includes("email")) {
    messageElement.textContent =
      companyInfo.email || "Maaf, aku tidak punya informasi tentang itu.";
  } else if (userMessage.toLowerCase().includes("about us")) {
    messageElement.textContent =
      companyInfo.aboutUs || "Maaf, aku tidak punya informasi tentang itu.";
  } else if (userMessage.toLowerCase().includes("visi")) {
    messageElement.textContent =
      companyInfo.vision || "Maaf, aku tidak punya informasi tentang itu.";
  } else if (userMessage.toLowerCase().includes("misi")) {
    messageElement.textContent =
      companyInfo.mission || "Maaf, aku tidak punya informasi tentang itu.";
  } else if (userMessage.toLowerCase().includes("legalitas")) {
    messageElement.textContent =
      companyInfo.legalitas || "Maaf, aku tidak punya informasi tentang itu.";
  } else if (userMessage.toLowerCase().includes("layanan")) {
    messageElement.textContent =
      companyInfo.services || "Maaf, aku tidak punya informasi tentang itu.";
  } else {
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
