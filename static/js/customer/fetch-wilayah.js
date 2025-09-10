// Fungsi fetch API wilayah
async function fetchWilayahIndo(apiLink, uid = null) {
    let link = uid ? `${apiLink}/${uid}` : apiLink;

    try {
        const respon = await fetch(link);
        const data = await respon.json();
        if (!respon.ok) {
            throw new Error(data.message || "Terjadi Kesalahan");
        }
        return data.data;
    } catch (error) {
        console.error("Gagal fetch: ", error);
        return [];
    }
}

// Fungsi isi select (bisa untuk tambah data & edit data)
async function isiSelect({
    apiLink,
    parentId = null,
    selectEl,
    placeholder,
    selectedId = null,
}) {
    // Kosongkan isi select
    selectEl.options.length = 0;
    selectEl.setAttribute("disabled", true);

    // Tambah opsi default
    const opsiDefault = new Option(placeholder, "", true, true);
    selectEl.add(opsiDefault);

    // Fetch data
    const data = await fetchWilayahIndo(apiLink, parentId);
    data.forEach((item) => {
        const option = new Option(item.name, item.id);
        if (selectedId && item.id == selectedId) {
            option.selected = true;
        }
        selectEl.add(option);
    });

    // Aktifkan kembali jika ada data
    if (data.length > 0) {
        selectEl.removeAttribute("disabled");
    }
}

// Inisialisasi chain wilayah
async function initWilayah({
    selectProvinsi,
    selectKabupaten,
    selectKecamatan,
    selectKelurahan,
    dataWilayah = null, // kalau edit data, isinya {provinsi_id, kabupaten_id, kecamatan_id, kelurahan_id}
}) {
    // Provinsi
    await isiSelect({
        apiLink: "/api/data/provinsi",
        selectEl: selectProvinsi,
        placeholder: "Pilih provinsi",
        selectedId: dataWilayah?.provinsi.id || null,
    });

    // Kabupaten
    if (dataWilayah?.provinsi.id) {
        await isiSelect({
            apiLink: "/api/data/kabupaten",
            parentId: dataWilayah.provinsi.id,
            selectEl: selectKabupaten,
            placeholder: "Pilih kabupaten",
            selectedId: dataWilayah.kabupaten.id,
        });
    }

    // Kecamatan
    if (dataWilayah?.kabupaten.id) {
        await isiSelect({
            apiLink: "/api/data/kecamatan",
            parentId: dataWilayah.kabupaten.id,
            selectEl: selectKecamatan,
            placeholder: "Pilih kecamatan",
            selectedId: dataWilayah.kecamatan.id,
        });
    }

    // Kelurahan
    if (dataWilayah?.kecamatan.id) {
        await isiSelect({
            apiLink: "/api/data/kelurahan",
            parentId: dataWilayah.kecamatan.id,
            selectEl: selectKelurahan,
            placeholder: "Pilih kelurahan",
            selectedId: dataWilayah.kelurahan.id,
        });
    }

    // Event Listener
    selectProvinsi.addEventListener("change", async () => {
        await isiSelect({
            apiLink: "/api/data/kabupaten",
            parentId: selectProvinsi.value,
            selectEl: selectKabupaten,
            placeholder: "Pilih kabupaten",
        });
        await isiSelect({
            apiLink: "/api/data/kecamatan",
            selectEl: selectKecamatan,
            placeholder: "Pilih kecamatan",
        });
        await isiSelect({
            apiLink: "/api/data/kelurahan",
            selectEl: selectKelurahan,
            placeholder: "Pilih kelurahan",
        });
    });

    selectKabupaten.addEventListener("change", async () => {
        await isiSelect({
            apiLink: "/api/data/kecamatan",
            parentId: selectKabupaten.value,
            selectEl: selectKecamatan,
            placeholder: "Pilih kecamatan",
        });
        await isiSelect({
            apiLink: "/api/data/kelurahan",
            selectEl: selectKelurahan,
            placeholder: "Pilih kelurahan",
        });
    });

    selectKecamatan.addEventListener("change", async () => {
        await isiSelect({
            apiLink: "/api/data/kelurahan",
            parentId: selectKecamatan.value,
            selectEl: selectKelurahan,
            placeholder: "Pilih kelurahan",
        });
    });
}
