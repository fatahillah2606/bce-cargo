// banner error
function tampilkanError(pesan) {
    let errorBanner = document.getElementById("pesan-error");

    if (pesan) {
        errorBanner.textContent = pesan;
        errorBanner.classList.remove("hidden");
    } else {
        errorBanner.classList.add("hidden");
    }
}

// Tampilkan sandi
// const showpwcheckbox = document.getElementById("show-pw");
// const pwfield = document.getElementById("password");

// showpwcheckbox.addEventListener("change", () => {
//     if (showpwcheckbox.checked) {
//         pwfield.setAttribute("type", "text");
//     } else {
//         pwfield.setAttribute("type", "password");
//     }
// });

function loginCustomer(event) {
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
        fetch("/customer/api/auth", {
            method: "POST",
            body: formulir,
        })
            .then(async (response) => {
                const data = await response.json();
                if (!response.ok) {
                    tampilkanError(data.message);
                    throw new Error(data.message);
                }
                return data;
            })
            .then((data) => {
                tampilkanError(); // Hapus banner error
                location.href = "/";
            })
            .catch((error) => {
                console.error(error);
            });
    } else {
        // Jika "false" tampilkan banner
        tampilkanError("Mohon isi kolom yang dibutuhkan");
    }
}

// Tampilkan sandi
const lihatPw = document.getElementById("lihat-pw");
const kolomPw = document.getElementById("password");

lihatPw.addEventListener("change", () => {
    if (lihatPw.checked) {
        kolomPw.setAttribute("type", "text");
    } else {
        kolomPw.setAttribute("type", "password");
    }
});
