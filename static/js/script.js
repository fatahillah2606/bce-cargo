// Load clients
function loadClients() {
    let clientListContainer = document.querySelector("#client-list");
    let clientListElm = "";
    let clientList = [
        "access.svg",
        "akr.webp",
        "binakarir.jpg",
        "ganex.jpg",
        "gledex.jpg",
        "indomarco.jpg",
        "iskent.png",
        "kenko.jpg",
        "kerry.png",
        "onecare.jpg",
        "pbd.jpg",
        "sinar.jpg",
        "slank.jpg",
        "spt.webp",
        "tgs.png",
        "ua.png",
        "unilab.jpg",
    ];

    clientList.forEach((images) => {
        clientListElm += `
            <swiper-slide>
                <img src="static/images/client_bce/${images}" alt="${images}" class="client-img" />
            </swiper-slide>
        `;
    });
    clientListContainer.innerHTML = clientListElm;
}
loadClients();
