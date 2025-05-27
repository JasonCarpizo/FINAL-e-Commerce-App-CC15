from PyQt6.QtWidgets import QMainWindow, QMessageBox
from ui.ProductDetails_UI import Ui_productDetails_MainWindow
from db import connect_to_database
from PyQt6.QtGui import QPixmap
from PyQt6 import QtCore
import os

class ProductDetailsWindow(QMainWindow):
    def __init__(self, user, product):
        super().__init__()
        self.ui = Ui_productDetails_MainWindow()
        self.ui.setupUi(self)
        self.user = user
        self.product = product

        self.ui.productDetails_pushButton_back.clicked.connect(self.close)
        self.ui.productDetails_pushButton_addCart.clicked.connect(self.add_to_cart)

        self.fill_product_details()

    def fill_product_details(self):
        if self.product['image_path'] and os.path.exists(self.product['image_path']):
            pixmap = QPixmap(self.product['image_path']).scaled(200, 200, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
            self.ui.productDetails_label_productImage.setPixmap(pixmap)

        self.ui.productDetails_label_productName.setText(self.product['name'])
        self.ui.productDetails_label_price.setText(f"₱{self.product['price']:.2f}")
        self.ui.productDetails_label_categoryName.setText(self.product['category'])

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("SELECT fullname FROM sellers WHERE id = %s", (self.product['seller_id'],))
            seller = cursor.fetchone()
            seller_name = seller['fullname'] if seller else "Unknown"
            self.ui.productDetails_label_sellerName.setText(seller_name)
        finally:
            if conn:
                conn.close()

        self.stock = self.product['stock']
        self.ui.productDetails_label_stock.setText(f"Available: {self.stock}")
        self.ui.productDetails_spinBox_quantity.setRange(1, self.stock)

    def add_to_cart(self):
        quantity = self.ui.productDetails_spinBox_quantity.value()

        if quantity < 1 or quantity > self.stock:
            self.ui.productDetails_label_Error.setText("Invalid quantity.")
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()

            # Check if product already in cart
            cursor.execute("""
                SELECT * FROM cart WHERE customer_id = %s AND product_id = %s
            """, (self.user['id'], self.product['id']))
            existing = cursor.fetchone()

            if existing:
                new_quantity = existing['quantity'] + quantity
                if new_quantity > self.stock:
                    self.ui.productDetails_label_Error.setText("Exceeds available stock.")
                    return
                cursor.execute("UPDATE cart SET quantity = %s WHERE id = %s", (new_quantity, existing['id']))
            else:
                cursor.execute("""
                    INSERT INTO cart (customer_id, product_id, quantity)
                    VALUES (%s, %s, %s)
                """, (self.user['id'], self.product['id'], quantity))

            conn.commit()
            QMessageBox.information(self, "Success", "Item added to cart.")
            self.close()

        except Exception as e:
            self.ui.productDetails_label_Error.setText(f"Error: {e}")
        finally:
            if conn:
                conn.close()