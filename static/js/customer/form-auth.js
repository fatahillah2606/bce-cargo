function fieldError(parentElm, pesan) {
    const labelForm = parentElm.querySelector("label");
    const kolomIsian = parentElm.querySelector("input");
    const kolomPilihan = parentElm.querySelector("select");
    const pesanError = parentElm.querySelector(".err-msg");

    labelForm.setAttribute(
        "class",
        "block text-sm font-medium text-red-700 dark:text-red-500"
    );
    if (kolomIsian) {
        kolomIsian.setAttribute(
            "class",
            "peer block w-full rounded-lg border pl-10 pr-3 py-2 text-sm transition bg-red-50 border-red-500 text-red-900 placeholder-red-700 focus:ring-red-500 dark:bg-gray-700 focus:border-red-500 dark:text-red-500 dark:placeholder-red-500 dark:border-red-500"
        );
    }

    if (kolomPilihan) {
        kolomPilihan.setAttribute(
            "class",
            "peer block w-full rounded-lg border pl-10 pr-3 py-2 text-sm transition cursor-pointer bg-red-50 border-red-500 text-red-900 placeholder-red-700 focus:ring-red-500 dark:bg-gray-700 focus:border-red-500 dark:text-red-500 dark:placeholder-red-500 dark:border-red-500"
        );
    }
    pesanError.textContent = pesan;
    pesanError.classList.remove("hidden");
}

function fieldNormal(parentElm) {
    const labelForm = parentElm.querySelector("label");
    const kolomIsian = parentElm.querySelector("input");
    const kolomPilihan = parentElm.querySelector("select");
    const pesanError = parentElm.querySelector(".err-msg");

    labelForm.setAttribute("class", "block text-sm font-medium text-gray-700");
    if (kolomIsian) {
        kolomIsian.setAttribute(
            "class",
            "peer block w-full rounded-lg border border-gray-300 pl-10 pr-3 py-2 text-sm text-gray-900 focus:border-green-500 focus:ring-green-500 transition"
        );
    }
    if (kolomPilihan) {
        kolomPilihan.setAttribute(
            "class",
            "peer block w-full rounded-lg border border-gray-300 text-gray-900 pl-10 pr-3 py-2 text-sm focus:border-green-500 focus:ring-green-500 transition cursor-pointer"
        );
    }
    pesanError.textContent = "";
    pesanError.classList.add("hidden");
}
