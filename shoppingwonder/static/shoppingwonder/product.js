document.addEventListener("DOMContentLoaded", function () {
  // Toggle product favorite
  document.querySelector("#fav-toggle").addEventListener("click", toggleFav);

  // Change product options views
  document.querySelectorAll(".btn-check").forEach((button) => {
    button.addEventListener("click", optionClick);
  });

  // Add products into cart
  document.querySelector("#cart-btn").addEventListener("click", () => {
    productId = document.querySelector(
      'input[name="variations"]:checked'
    ).value;
    addToCart(productId).then(() => {
      // Open the cart page
      // cartPage = document.querySelector("#offcanvasScrolling");
      // cartOffCanvas = new bootstrap.Offcanvas(cartPage);
      // cartOffCanvas.show();

      // Show a toast message
      var toastLiveExample = document.getElementById("liveToast");
      var toast = new bootstrap.Toast(toastLiveExample);
      toast.show();
    });
  });
});

function toggleFav() {
  parent = this.dataset.parentId;

  fetch(`/product/${parent}/toggle-fav`)
    .then((response) => response.json())
    .then((result) => {
      const fav_toggle = result["fav_toggle"];

      // Update the heart font icon to be heart filled if fav_toggle is true
      if (fav_toggle) {
        document
          .querySelector(".fav-toggle")
          .classList.replace("heart", "heart-full");
      } else {
        document
          .querySelector(".fav-toggle")
          .classList.replace("heart-full", "heart");
      }
    });
}

function optionClick() {
  child = this.dataset.childId;
  var divsToHide = document.getElementsByClassName("parent");
  for (var i = 0; i < divsToHide.length; i++) {
    divsToHide[i].style.display = "none";
  }

  var divsToHide = document.getElementsByClassName("children");
  for (var i = 0; i < divsToHide.length; i++) {
    divsToHide[i].classList.add("d-none");
  }

  document.querySelector(`#carousel-${child}`).classList.remove("d-none");
  document.querySelector(`#price-${child}`).classList.remove("d-none");
}
