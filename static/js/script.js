// jQuery
$(document).ready(function () {
  $(".owl-carousel").owlCarousel({
    loop: true,
    margin: 10,
    nav: true,
    autoplay: true,
    autoplayTimeout: 5000,
    autoplayHoverPause: true,
    autoWidth: true,
  });
});

const dropdown = document.querySelector(".dropdown");
const dropdownmenu = document.querySelector(".dropdown-menu");

dropdown.addEventListener("click", function () {
  dropdownmenu.classList.toggle("show");
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
