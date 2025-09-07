// Toggle tema gelap dan terang
const themeSwitch = document.getElementById("theme-input-switch");
const html = document.documentElement;

function toggleTheme() {
    html.classList.toggle("dark");

    // Simpan ke localStorage
    if (html.classList.contains("dark")) {
        localStorage.setItem("theme", "dark");
        themeSwitch.setAttribute("checked", "");
    } else {
        localStorage.setItem("theme", "light");
        themeSwitch.removeAttribute("checked");
    }
}

// Cek preferensi tema
if (localStorage.getItem("theme") === "dark") {
    document.documentElement.classList.add("dark");
    themeSwitch.setAttribute("checked", "");
} else {
    document.documentElement.classList.remove("dark");
    themeSwitch.removeAttribute("checked");
}
