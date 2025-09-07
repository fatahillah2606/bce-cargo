// Tampilkan sandi
const showpwcheckbox = document.getElementById("show-pw");
const pwfield = document.getElementById("password");

showpwcheckbox.addEventListener("change", () => {
    if (showpwcheckbox.checked) {
        pwfield.setAttribute("type", "text");
    } else {
        pwfield.setAttribute("type", "password");
    }
});

// banner error
function tampilkanError(pesan) {
    let errorBanner = document.getElementById("error-banner");
    let errorText = errorBanner.querySelector("p");

    if (pesan) {
        errorText.textContent = pesan;
        errorBanner.classList.remove("hidden");
    } else {
        errorBanner.classList.add("hidden");
    }
}

function loginAdmin(event) {
    event.preventDefault();

    // formulir
    const formElm = document.getElementById("login");
    const formulir = new FormData(formElm);
    formulir.append("login", true);

    // Cek kolom kosong
    let validasi = true;
    const inputElm = document.querySelectorAll("input[required]");
    inputElm.forEach((kolom) => {
        if (kolom.value == "") {
            kolom.focus();
            validasi = false;
        }
    });

    // Proses form jika validasi "true"
    if (validasi) {
        fetch("/admin/api/auth", {
            method: "POST",
            body: formulir,
        })
            .then(async (response) => {
                const data = await response.json();
                if (!response.ok) {
                    tampilkanError(data.message);
                    throw new Error(data.message || "Terjadi kesalahan");
                }
                return data;
            })
            .then((data) => {
                if (data.code === 200) {
                    tampilkanError(); // Hapus banner error
                    location.href = "/admin/dashboard";
                } else {
                    tampilkanError("Email atau Sandi salah");
                }
            })
            .catch((error) => {
                console.error(error);
            });
    } else {
        // Jika "false" tampilkan banner
        tampilkanError("Mohon isi kolom yang dibutuhkan");
    }
}
