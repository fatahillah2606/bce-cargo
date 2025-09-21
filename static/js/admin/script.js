// Format tanggal
function formatTanggalGMT7(dateString) {
    // Parse string jadi objek Date
    const date = new Date(dateString);

    // Ubah ke GMT+7 (WIB)
    const offset = 7 * 60; // menit offset GMT+7
    const localTime = new Date(date.getTime() + offset * 60 * 1000);

    // Ambil bagian Hari, Tanggal, Jam
    const hari = localTime.toLocaleDateString("id-ID", { weekday: "long" });
    const tanggal = localTime.toLocaleDateString("id-ID", {
        day: "2-digit",
        month: "long",
        year: "numeric",
    });
    const jam = localTime.toLocaleTimeString("id-ID", {
        hour: "2-digit",
        minute: "2-digit",
    });

    // Balikin hasil dalam bentuk Object
    return { hari, tanggal, jam };
}

function formatTanggal(dateString, jenis) {
    let date;
    let day;
    let month;
    let year;

    switch (jenis) {
        case "short":
            date = new Date(dateString);
            day = String(date.getDate()).padStart(2, "0"); // Mengambil hari dan menambahkan nol di depan jika perlu
            month = String(date.getMonth() + 1).padStart(2, "0"); // Mengambil bulan (0-11) dan menambah 1
            year = String(date.getFullYear()).slice(-2); // Mengambil dua digit terakhir dari tahun

            return `${day}/${month}/${year}`;

        case "formatISO":
            date = new Date(dateString);
            year = date.getFullYear(); // Mengambil tahun
            month = String(date.getMonth() + 1).padStart(2, "0"); // Mengambil bulan (0-11) dan menambah 1
            day = String(date.getDate()).padStart(2, "0"); // Mengambil hari dan menambahkan nol di depan jika perlu

            return `${year}-${month}-${day}`;

        default:
            const options = { day: "2-digit", month: "short", year: "numeric" };
            date = new Date(dateString);
            return date.toLocaleDateString("en-GB", options);
    }
}

// Label warna untuk status pesanan
function labelWarna(statusPesanan) {
    switch (statusPesanan) {
        case "Pending":
            return "bg-yellow-500";
        case "Diproses":
            return "bg-blue-500";
        case "Ditolak":
            return "bg-red-500";
        case "Menunggu pick-up":
            return "bg-orange-500";
        case "Dalam pengiriman":
            return "bg-indigo-500";
        case "Sampai tujuan":
            return "bg-teal-500";
        case "Selesai":
            return "bg-green-500";
        case "Gagal dikirim":
            return "bg-rose-500";
        default:
            return "bg-zinc-500"; // fallback warna default
    }
}

// Warna text untuk status pesanan
function labelText(statusPesanan) {
    switch (statusPesanan) {
        case "Pending":
            return "text-yellow-600";
        case "Diproses":
            return "text-blue-600";
        case "Ditolak":
            return "text-red-600";
        case "Menunggu pick-up":
            return "text-orange-600";
        case "Dalam pengiriman":
            return "text-indigo-600";
        case "Sampai tujuan":
            return "text-teal-600";
        case "Selesai":
            return "text-green-600";
        case "Gagal dikirim":
            return "text-rose-600";
        default:
            return "text-zinc-600"; // fallback warna default
    }
}

// Untuk label status pesanan
function labelStatusPesanan(statusPesanan, elm) {
    let base = "text-xs font-medium me-2 px-2.5 py-0.5 rounded-sm ";
    let color = "";

    switch (statusPesanan) {
        case "Pending":
            color =
                "bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-300";
            break;
        case "Diproses":
            color =
                "bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-300";
            break;
        case "Ditolak":
            color = "bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-300";
            break;
        case "Menunggu pick-up":
            color =
                "bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-300";
            break;
        case "Dalam pengiriman":
            color =
                "bg-indigo-100 dark:bg-indigo-900 text-indigo-800 dark:text-indigo-300";
            break;
        case "Sampai tujuan":
            color =
                "bg-teal-100 dark:bg-teal-900 text-teal-800 dark:text-teal-300";
            break;
        case "Selesai":
            color =
                "bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-300";
            break;
        case "Gagal dikirim":
            color =
                "bg-rose-100 dark:bg-rose-900 text-rose-800 dark:text-rose-300";
            break;
    }

    base += color;
    elm.setAttribute("class", base);
}

// Konversi rupiah
function formatRupiah(angka) {
    const number = parseInt(angka, 10);
    return "Rp. " + number.toLocaleString("id-ID") + ",-";
}

// Ubah warna form input jika error
function inputSalah(parElm, pesan) {
    let label = parElm.querySelector("label");
    let input = parElm.querySelector("input");
    let select = parElm.querySelector("select");
    let pesanError = parElm.querySelector("p");

    label.setAttribute(
        "class",
        "block mb-2 text-sm font-medium text-red-700 dark:text-red-500"
    );

    if (input) {
        input.setAttribute(
            "class",
            "bg-red-50 border border-red-500 text-red-900 placeholder-red-700 text-sm rounded-lg focus:ring-red-500 dark:bg-zinc-700 focus:border-red-500 block w-full p-2.5 dark:text-red-500 dark:placeholder-red-500 dark:border-red-500"
        );
    }

    if (select) {
        select.setAttribute(
            "class",
            "bg-red-50 border border-red-500 text-red-900 placeholder-red-700 text-sm rounded-lg focus:ring-red-500 dark:bg-zinc-700 focus:border-red-500 block w-full p-2.5 dark:text-red-500 dark:placeholder-red-500 dark:border-red-500"
        );
    }

    pesanError.textContent = pesan;
    pesanError.classList.remove("hidden");
}

// Kembalikan form input ke normal
function inputNormal(parElm) {
    let label = parElm.querySelector("label");
    let input = parElm.querySelector("input");
    let select = parElm.querySelector("select");
    let pesanError = parElm.querySelector("p");

    label.setAttribute(
        "class",
        "block mb-2 text-sm font-medium text-zinc-900 dark:text-white"
    );

    if (input) {
        input.setAttribute(
            "class",
            "bg-zinc-50 border border-zinc-300 text-zinc-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-zinc-600 dark:border-zinc-500 dark:placeholder-zinc-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"
        );
    }

    if (select) {
        select.setAttribute(
            "class",
            "bg-zinc-50 border border-zinc-300 text-zinc-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-zinc-600 dark:border-zinc-500 dark:placeholder-zinc-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"
        );
    }

    pesanError.classList.add("hidden");
}

// Alert
const alertContainer = document.querySelector("#alert-toaster");
let hapusOtomatis;

function tampilkanAlertBerhasil(judul, pesan) {
    clearTimeout(hapusOtomatis);

    alertContainer.innerHTML = `
        <div
            class="p-4 text-green-800 border border-green-300 rounded-lg bg-green-50 dark:bg-zinc-800 dark:text-green-400 dark:border-green-800 shadow-lg relative"
            role="alert"
        >
            <div class="flex items-center">
                <i class="material-symbols-rounded shrink-0 me-2">check_circle</i>
                <h3 class="text-lg font-medium">${judul}</h3>
            </div>
            <div class="mt-2 mb-2 text-sm">${pesan}</div>
            <button
                id="close-alert"
                class="absolute top-2 right-2 cursor-pointer"
                onclick="hapusAlert()"
            >
                <span
                    class="material-symbols-rounded text-green-800 dark:text-green-400"
                >
                    close_small
                </span>
            </button>
        </div>
    `;
    alertContainer.classList.remove("hidden");

    hapusOtomatis = setTimeout(() => {
        hapusAlert();
    }, 5000);
}

function tampilkanAlertKesalahan(judul, pesan) {
    clearTimeout(hapusOtomatis);

    alertContainer.innerHTML = `
        <div
            class="p-4 text-red-800 border border-red-300 rounded-lg bg-red-50 dark:bg-zinc-800 dark:text-red-400 dark:border-red-800 shadow-lg relative"
            role="alert"
        >
            <div class="flex items-center">
                <i class="material-symbols-rounded shrink-0 me-2">error</i>
                <h3 class="text-lg font-medium">${judul}</h3>
            </div>
            <div class="mt-2 mb-2 text-sm">${pesan}</div>
            <button
                id="close-alert"
                class="absolute top-2 right-2 cursor-pointer"
                onclick="hapusAlert()"
            >
                <span
                    class="material-symbols-rounded text-red-800 dark:text-red-400"
                >
                    close_small
                </span>
            </button>
        </div>
    `;
    alertContainer.classList.remove("hidden");

    hapusOtomatis = setTimeout(() => {
        hapusAlert();
    }, 5000);
}

function hapusAlert() {
    alertContainer.classList.add("hidden");
    alertContainer.innerHTML = "";
}

// Ubah true/false jadi Ya/Tidak
function ubahTrueFalse(isi) {
    if (isi) {
        return "Ya";
    } else {
        return "Tidak";
    }
}

// Ubah aray menjadi list
function ubahArrayKeList(dataArray) {
    let container = `<ul class="max-w-md space-y-1 text-zinc-500 list-disc dark:text-zinc-400">`;
    dataArray.forEach((data) => {
        container += `
            <li>${data}</li>
        `;
    });
    container += `</ul>`;
    return container;
}

// Cek pesan belum dibaca
function checkUnread() {
    const unreadIndicator = document.getElementById("unread-indicator");
    const unreadCount = document.getElementById("unread-count");

    fetch("/admin/api/data/feedback?unread=true", {
        method: "GET",
        headers: { "Content-Type": "application/json" },
    })
        .then(async (respon) => {
            const data = await respon.json();
            if (!respon.ok) {
                throw new Error(data.message || "Terjadi kesalahan");
            }

            return data;
        })
        .then((data) => {
            const listKeluhan = data.data;
            if (listKeluhan.length === 0) {
                unreadIndicator.classList.add("hidden");
            } else {
                const unreadData = data.data;
                unreadCount.textContent = unreadData.unread;
                unreadIndicator.classList.remove("hidden");
            }
        })
        .catch((error) => {
            console.error(error);
        });
}

checkUnread();

// Untuk tombol aksi pada detail pesanan
function actionButtonsDetailPesanan(status) {
    switch (status) {
        case "Pending":
            return `
                <button
                    class="flex items-center gap-2.5 cursor-pointer px-4 py-2 text-sm text-red-500 border border-red-500 rounded-lg hover:bg-red-500 hover:text-white grow"
                    onclick="modalTolakPesanan.toggle()"
                >
                    <span class="material-symbols-rounded"> block </span>
                    <span>Tolak</span>
                </button>
                <button
                    class="flex items-center gap-2.5 cursor-pointer px-4 py-2 text-sm text-white bg-green-600 rounded-lg hover:bg-green-700 grow"
                    onclick="modalTerimaPesanan.toggle()"
                >
                    <span class="material-symbols-rounded"> check </span>
                    <span>Terima</span>
                </button>
            `;

        case "Ditolak":
            return ``;

        case "Gagal dikirim":
            return ``;

        case "Selesai":
            return ``;

        default:
            return `
                <button
                    class="flex items-center gap-2.5 cursor-pointer px-4 py-2 text-sm text-white bg-green-600 rounded-lg hover:bg-green-700 grow"
                    onclick="modalUpdateStatus.toggle()"
                >
                    <span class="material-symbols-rounded">
                        published_with_changes
                    </span>
                    <span>Update status</span>
                </button>
            `;
    }
}
