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
            return "bg-gray-500"; // fallback warna default
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
            return "text-gray-600"; // fallback warna default
    }
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
            "bg-red-50 border border-red-500 text-red-900 placeholder-red-700 text-sm rounded-lg focus:ring-red-500 dark:bg-gray-700 focus:border-red-500 block w-full p-2.5 dark:text-red-500 dark:placeholder-red-500 dark:border-red-500"
        );
    }

    if (select) {
        select.setAttribute(
            "class",
            "bg-red-50 border border-red-500 text-red-900 placeholder-red-700 text-sm rounded-lg focus:ring-red-500 dark:bg-gray-700 focus:border-red-500 block w-full p-2.5 dark:text-red-500 dark:placeholder-red-500 dark:border-red-500"
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
        "block mb-2 text-sm font-medium text-gray-900 dark:text-white"
    );

    if (input) {
        input.setAttribute(
            "class",
            "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-600 dark:border-gray-500 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"
        );
    }

    if (select) {
        select.setAttribute(
            "class",
            "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-600 dark:border-gray-500 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"
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
            class="p-4 text-green-800 border border-green-300 rounded-lg bg-green-50 dark:bg-gray-800 dark:text-green-400 dark:border-green-800 shadow-lg relative"
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
            class="p-4 text-red-800 border border-red-300 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400 dark:border-red-800 shadow-lg relative"
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
