import os
from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QSizePolicy
from PyQt6.QtGui import QPixmap
from PyQt6 import QtCore
from ui.Customer_UI import Ui_customer_MainWindow
from db import connect_to_database
from windows.ProductDetails_Window import ProductDetailsWindow

class CustomerWindow(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.ui = Ui_customer_MainWindow()
        self.ui.setupUi(self)
        self.user = user_data

        # Setup grid layout spacing
        self.ui.customer_gridLayout_products.setSpacing(20)
        self.ui.customer_gridLayout_products.setContentsMargins(10, 10, 10, 10)
        self.ui.customer_gridLayout_products.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.ui.customer_scrollAreaWidgetContents.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        # Category buttons
        self.category_buttons = [
            self.ui.customer_pushButton_booksStationary,
            self.ui.customer_pushButton_clothingFashion,
            self.ui.customer_pushButton_electronicsGadgets,
            self.ui.customer_pushButton_foodSnacks,
            self.ui.customer_pushButton_healthBeauty,
            self.ui.customer_pushButton_homeLiving,
            self.ui.customer_pushButton_others,
        ]
        for button in self.category_buttons:
            button.setCheckable(True)
            button.clicked.connect(self.update_category_filter)

        self.selected_category = None

        self.ui.customer_pushButton_logOut.clicked.connect(self.logout)
        self.ui.customer_pushButton_shoppingCart.clicked.connect(self.open_cart)
        self.ui.customer_pushButton_purchases.clicked.connect(self.open_purchases)

        self.load_products()

    def logout(self):
        from windows.Access_Window import AccessWindow
        self.access = AccessWindow()
        self.access.show()
        self.close()

    def open_cart(self):
        from windows.ShoppingCart_Window import ShoppingCartWindow
        self.cart_window = ShoppingCartWindow(self.user)
        self.cart_window.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.cart_window.show()

    def open_purchases(self):
        from windows.Purchases_Window import PurchasesWindow
        self.purchases_window = PurchasesWindow(self.user)
        self.purchases_window.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.purchases_window.show()

    def update_category_filter(self):
        # Uncheck all others when one is clicked
        clicked_button = self.sender()

        # Deselect if it was already selected
        if self.selected_category == clicked_button.text():
            clicked_button.setChecked(False)
            self.selected_category = None
        else:
            self.selected_category = clicked_button.text()
            for btn in self.category_buttons:
                btn.setChecked(btn == clicked_button)

        self.load_products()

    def load_products(self):
        while self.ui.customer_gridLayout_products.count():
            item = self.ui.customer_gridLayout_products.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            if self.selected_category:
                cursor.execute("SELECT * FROM products WHERE category = %s AND stock > 0", (self.selected_category,))
            else:
                cursor.execute("SELECT * FROM products WHERE stock > 0")
            products = cursor.fetchall()

            for i, product in enumerate(products):
                widget = QWidget()
                layout = QVBoxLayout(widget)
                widget.setFixedSize(180, 200)
                widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

                label_img = QLabel()
                label_img.setFixedSize(100, 100)
                label_img.setScaledContents(True)

                if product['image_path'] and os.path.exists(product['image_path']):
                    label_img.setPixmap(QPixmap(product['image_path']).scaled(100, 100, QtCore.Qt.AspectRatioMode.KeepAspectRatio))

                label_name = QPushButton(product['name'])
                label_name.clicked.connect(lambda _, p=product: self.open_product_details(p))

                label_stock = QLabel(f"Stock: {product['stock']}")
                label_price = QLabel(f"₱{product['price']:.2f}")

                layout.addWidget(label_img)
                layout.addWidget(label_name)
                layout.addWidget(label_stock)
                layout.addWidget(label_price)

                layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
                self.ui.customer_gridLayout_products.addWidget(widget, i // 4, i % 4)  # 4 per row

        finally:
            if conn:
                conn.close()

    def open_product_details(self, product_data):
        self.details_window = ProductDetailsWindow(self.user, product_data)
        self.details_window.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.details_window.show()