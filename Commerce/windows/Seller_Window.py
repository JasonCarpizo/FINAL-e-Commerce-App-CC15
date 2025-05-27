from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QDialog, QTableWidgetItem
from ui.Seller_UI import Ui_seller_MainWindow
from db import connect_to_database
from PyQt6.QtGui import QPixmap
from PyQt6 import QtCore
from PyQt6.QtWidgets import QSizePolicy
import os
from PyQt6.QtGui import QIcon
from windows.AddProduct_Window import AddProductWindow
from windows.EditProduct_Window import EditProductWindow


class SellerWindow(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.ui = Ui_seller_MainWindow()
        self.ui.setupUi(self)
        self.user = user_data

        self.ui.seller_gridLayout_myProducts.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.ui.seller_scrollAreaWidgetContents.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.ui.seller_pushButton_logOut.clicked.connect(self.logout)
        self.ui.seller_pushButton_addProduct.clicked.connect(self.open_add_product)

        self.load_products()
        self.load_orders()

    def logout(self):
        from windows.Access_Window import AccessWindow
        self.access = AccessWindow()
        self.access.show()
        self.close()

    def open_add_product(self):
        self.add_window = AddProductWindow(self.user['id'], self.load_products)
        self.add_window.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.add_window.show()

    def open_edit_product(self, product_id):
        self.edit_window = EditProductWindow(product_id, self.load_products)
        self.edit_window.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.edit_window.show()

    def load_products(self):
        # clear layout first
        while self.ui.seller_gridLayout_myProducts.count():
            item = self.ui.seller_gridLayout_myProducts.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.ui.seller_gridLayout_myProducts.setSpacing(20)
        self.ui.seller_gridLayout_myProducts.setContentsMargins(10, 10, 10, 10)

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE seller_id = %s", (self.user['id'],))
            products = cursor.fetchall()
            for i, product in enumerate(products):
                widget = QWidget()
                layout = QVBoxLayout(widget)

                # Set fixed size for the product card
                widget.setFixedSize(200, 200)
                widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

                label_img = QLabel()
                label_img.setFixedSize(100, 100)
                label_img.setScaledContents(True)

                if product['image_path'] and os.path.exists(product['image_path']):
                    label_img.setPixmap(
                        QPixmap(product['image_path']).scaled(100, 100, QtCore.Qt.AspectRatioMode.KeepAspectRatio))

                label_name = QPushButton(product['name'])
                label_name.clicked.connect(lambda _, pid=product['id']: self.open_edit_product(pid))

                label_stock = QLabel(f"Stock: {product['stock']}")
                label_price = QLabel(f"₱{product['price']:.2f}")

                layout.addWidget(label_img)
                layout.addWidget(label_name)
                layout.addWidget(label_stock)
                layout.addWidget(label_price)

                layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

                # Add to grid layout in row/column
                self.ui.seller_gridLayout_myProducts.addWidget(widget, i // 3, i % 3)
        finally:
            if conn:
                conn.close()

    def load_orders(self):
        self.ui.seller_tableWidget_productOrders.setRowCount(0)

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.quantity, p.name, p.image_path, p.price
                FROM orders o
                JOIN products p ON o.product_id = p.id
                WHERE p.seller_id = %s
            """, (self.user['id'],))

            orders = cursor.fetchall()

            self.ui.seller_tableWidget_productOrders.setColumnCount(5)
            self.ui.seller_tableWidget_productOrders.setHorizontalHeaderLabels(
                ["Image", "Name", "Price", "Amount Sold", "Total"])
            self.ui.seller_tableWidget_productOrders.horizontalHeader().setStretchLastSection(True)

            for row, order in enumerate(orders):
                self.ui.seller_tableWidget_productOrders.insertRow(row)

                img_item = QTableWidgetItem()
                if order['image_path'] and os.path.exists(order['image_path']):
                    pixmap = QPixmap(order['image_path'])
                    if not pixmap.isNull():
                        img_item.setIcon(QIcon(pixmap))
                img_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.ui.seller_tableWidget_productOrders.setItem(row, 0, img_item)

                name_item = QTableWidgetItem(order['name'])
                name_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.ui.seller_tableWidget_productOrders.setItem(row, 1, name_item)

                price_item = QTableWidgetItem(f"₱{order['price']:.2f}")
                price_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.ui.seller_tableWidget_productOrders.setItem(row, 2, price_item)

                qty_item = QTableWidgetItem(str(order['quantity']))
                qty_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.ui.seller_tableWidget_productOrders.setItem(row, 3, qty_item)

                total = order['quantity'] * order['price']
                total_item = QTableWidgetItem(f"₱{total:.2f}")
                total_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.ui.seller_tableWidget_productOrders.setItem(row, 4, total_item)

        finally:
            if conn:
                conn.close()