# ShoppingWonder
#### Video Demo: https://youtu.be/cVERsWkSGdE?si=uJcc3c7TuUB-kD0-

### Description:
ShoppingWonder is a cosmetics shopping website for customers as well as a stock and customer order management system for the seller or admin. It was developed with Django (including a comprehensive set of models) on the back-end and JavaScript on the front-end. The website is mobile-responsive, especially on its grid-heavy templates.

# Distinctiveness and Complexity
The web app significantly utilizes Django models and its ORM including context processors to keep track of product hierachy (category, parent product and product), product variations (e.g. size and color), user's shopping bag/cart, stock quantity update, order status, and insightful data for the seller's analysis. The seller basically maintains data via Django admin page. Behind the scene, signals are also used to ensure stock quantity in the related fields in Stock and Product models are in sync. The seller can also use the website interface for order management and order & stock analysis in which methods from the models are frequently called to calculate/render results.

The highlights of the application are:

**Product variations**: Product variations of the same product are grouped under one parent. The products listed on the index page are the parents and those without parent (meaning without variations). Each one is linked to the product page where product variations (if any) are presented as options for the customers to add to their cart. A set of corresponding images are presented based on product option selection with the use of JavaScript.

**Shopping Bag**: Context processor 'cart' is available so that the users can always view their cart in any page they are at. In there, they can view the count of products in the bag, a list of products with images that are linked to the product page, product prices, quantities they added into the cart, total cart amount and the functionality to adjust the product quantity. The quantity change reflects realtime with the use of JavaScript. The quantity cannot exceed the product remaining quantity as the increase button will be disabled and the check is implemented at the backend. If the quantity is reduced to zero, it will be removed from the cart. After placing order, the cart will be empty.

**Order Management**: Users can view their purchase orders with similar details as their cart and additional order details which are order status (ordered, paid, shipped and delivered) and status change dates. The customer can confirm they receive the delivery after the shiped status. The seller or staff can also view sales orders with additional financial details which are cost and product at the item and order levels. The cost of the products sold is based on FIFO (or linked with older stock first) and if there are more than one related stock. The cost presented is average of the related stock costs. The seller can update order status via UI to confirm payment and shipping. There is a side menu to display each specific status or all statuses. After the product update, the users will be redirected to the page of the next status (After comfirm delivery, the redirected page is "Completed" with all completed orders).

**Stock Management**: The seller or staff can only view this page to see lists of products that are in-stock, out-of-stock and inactive. Each product shows its remaining stock quantity, average costs derived from all stock-in records, and numbers of product page views, favorites added and sold quantity. There will be a warning sign to restock if stock quantity is at or below the minium quantity set by the seller via admin page. These are all managed with the relationship between Product and Stock models.

# File Walkthrough
**views.py**:  Backend functionalities with SQLite connection

**urls.py**: URL routes of the application

**models.py**:  Database models with methods. Addtional MartorField for product details to be able to format text and display in an easy-to-read manner

**admin.py**: Configuration of models for admin page e.g. what fields are to be displayed, and functionality to update Image model right on Product model page

**context_processors.py**: Setup categories and cart functions to be used at any page on the website

**signals.py**: Function that will be implemented after a stock record (restock on the seller side) is created in Stock model in order to update/increase product remaining quantity in Product model and its parent remaining quantity (if any)

**/static**:  Besides CSS and images, this path contains two JavaScript files:

 -   **cart.js**: linked with layout page to create items in cart and update cart quantity
 -   **product.js**  linked with product page to toggle product favorite, add product items to cart with pop-up notification and view correspending images of each product variation

**/templates**:  In this path, there are HTML forms mainly styled with Bootstrap.

 - register, login and logout: for user access
 - index: list of active products with menu to view by category, new items (last 3 products created) and best sellers (top 3 based on quantity sold)
 - layout: main layout of top menu for other files including search and cart placeholder
 - cart: additon cart for layout to be rendered separately when JavaScript is used to update cart quantity
 - pagination: page selection for index, sales and purchases
 - favorites: list of favorite products
 - contact and profile: for seller and customer info
 - purchases: list of user's purchase orders
 - sales: list of all sales orders for the seller
 - stocks: list of stocks for the seller

# How to run

 Run the following commands:

> python manage.py migrate

> python manage.py runserver

and go to the ShoppingWonder website and have a wonderul day!
