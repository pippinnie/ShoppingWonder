document.addEventListener("DOMContentLoaded", function () {
  addRemove();

  // // Search product items
  // $(document).ready(function () {
  //   $("#search-input").on("keyup", function () {
  //     var value = $(this).val().toLowerCase();
  //     $(".product-list li").filter(function () {
  //       console.log(this);
  //       $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
  //     });
  //   });
  // });

});

function addRemove() {
  // Add product quantity in cart
  document.querySelectorAll(".cart-add").forEach((product) => {
    product.addEventListener("click", function () {
      console.log(this);
      const productId = this.dataset.prdId;
      addToCart(productId);
    });
  });

  // Remove product quantity from cart
  document.querySelectorAll(".cart-remove").forEach((product) => {
    product.addEventListener("click", function () {
      const productId = this.dataset.prdId;
      removeFromCart(productId);
    });
  });
}

function addToCart(productId) {
  return fetch(`/cart/${productId}/add`, {
    method: "PUT",
  })
    .then((response) => response.json())
    .then((result) => {
      // Display the updated content
      document.querySelector("#cart-items").innerHTML = result["cartPage"];
      addRemove();

      // Update cart product count
      document.querySelectorAll(".cart-qty").forEach((element) => {
        element.innerHTML = result["cartCount"];
      });
    });
}

function removeFromCart(productId) {
  fetch(`/cart/${productId}/remove`, {
    method: "PUT",
  })
    .then((response) => response.json())
    .then((result) => {
      // Display the updated content
      document.querySelector("#cart-items").innerHTML = result["cartPage"];
      addRemove();

      // Update cart product count
      document.querySelectorAll(".cart-qty").forEach((element) => {
        element.innerHTML = result["cartCount"];
      });
    });
}
