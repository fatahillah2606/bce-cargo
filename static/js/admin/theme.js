// Toggle tema gelap dan terang
function toggleTheme() {
    const html = document.documentElement;
    html.classList.toggle("dark");

    // Simpan ke localStorage
    if (html.classList.contains("dark")) {
        localStorage.setItem("theme", "dark");
    } else {
        localStorage.setItem("theme", "light");
    }
}

// Cek preferensi tema
if (localStorage.getItem("theme") === "dark") {
    document.documentElement.classList.add("dark");
} else {
    document.documentElement.classList.remove("dark");
}
