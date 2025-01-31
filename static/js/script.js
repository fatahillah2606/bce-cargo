// jQuery
// Owl carousel
$(document).ready(function () {
  $(".owl-carousel").owlCarousel({
    loop: true,
    margin: 10,
    autoplay: true,
    autoplayTimeout: 3000,
    autoWidth: true,
    responsiveClass: true,
    responsive: {
      0: {
        items: 1,
        nav: true,
      },
      600: {
        items: 3,
        nav: false,
      },
      1000: {
        items: 5,
        nav: true,
      },
    },
  });
});

// dropdown
const dropdown = document.querySelector(".dropdown");
const dropdownmenu = document.querySelector(".dropdown-menu");

dropdown.addEventListener("click", function () {
  dropdownmenu.classList.toggle("show");
});
dropdownmenu.addEventListener("click", () => {
  if (dropdownmenu.classList.contains("show")) {
    dropdownmenu.classList.remove("show");
  }
});

// Padding navigasi berubah ketika di scroll
window.onscroll = function () {
  let navigasi = document.querySelector(".navbar");

  if (
    document.body.scrollTop > 120 ||
    document.documentElement.scrollTop > 120
  ) {
    navigasi.classList.add("scroll");
  } else {
    navigasi.classList.remove("scroll");
  }
};

// Mobile menu
const mobileMenu = document.querySelector(".mobile-menu");
const menuCont = document.querySelectorAll(".menu-content li");
const menuBtn = document.querySelector(".menu-btn");
const closeMenuBtn = document.querySelector(".close-menu-btn");

function openMenu() {
  if (!mobileMenu.classList.contains("show")) {
    mobileMenu.classList.add("show");
  }
}

function closeMenu() {
  if (mobileMenu.classList.contains("show")) {
    mobileMenu.classList.remove("show");
  }
}

menuBtn.addEventListener("click", openMenu);
closeMenuBtn.addEventListener("click", closeMenu);
menuCont.forEach((menu) => {
  menu.addEventListener("click", closeMenu);
});

// Galeri
let foto = [
  "fadel.jpeg",
  "fatah.jpeg",
  "fieldoffice.jpeg",
  "galang.jpeg",
  "headoffice.jpeg",
  "foto_1.jpg",
  "foto_2.jpg",
  "foto_3.jpg",
  "foto_4.jpg",
  "foto_5.jpg",
  "foto_6.jpg",
  "foto_7.jpg",
  "foto_8.jpg",
  "foto_9.jpg",
  "foto_10.jpg",
  "foto_11.jpg",
];

let folder = "static/images/gallery_bce/";
let imgContainer = document.getElementById("galeri");

let tagImg = "";
foto.forEach((element) => {
  tagImg += `
    <div class="foto">
      <img src="${folder}${element}"/>
      <p>Lihat foto</p>
    </div>
    `;
});

imgContainer.innerHTML = tagImg;

// Dark mode toggle
function toggleDarkMode() {
  let tema = document.body.getAttribute("data-theme");
  if (tema === "light") {
    document.body.setAttribute("data-theme", "dark");
  } else {
    document.body.setAttribute("data-theme", "light");
  }
}
