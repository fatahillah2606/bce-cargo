function formatTanggalGMT7(dateString) {
    // 1. Parse string jadi objek Date
    const date = new Date(dateString);

    // 2. Ubah ke GMT+7 (WIB)
    const offset = 7 * 60; // menit offset GMT+7
    const localTime = new Date(date.getTime() + offset * 60 * 1000);

    // 3. Ambil bagian Hari, Tanggal, Jam
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

    return { hari, tanggal, jam };
}
