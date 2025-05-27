import os
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QMainWindow, QSpinBox, QTableWidgetItem, QAbstractItemView, QMessageBox

from Customer_Window import CustomerWindow
from ui.ShoppingCart_UI import Ui_shoppingCart_MainWindow
from db import connect_to_database

class ShoppingCartWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.ui = Ui_shoppingCart_MainWindow()
        self.ui.setupUi(self)
        self.user = user

        self.ui.shoppingCart_pushButton_back.clicked.connect(self.close)
        self.ui.shoppingCart_pushButton_removeItem.clicked.connect(self.remove_item)
        self.ui.shoppingCart_pushButton_placeOrder.clicked.connect(self.place_order)

        self.ui.shoppingCart_tableWidget_shoppingCart.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.ui.shoppingCart_tableWidget_shoppingCart.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.ui.shoppingCart_tableWidget_shoppingCart.setColumnCount(5)
        self.ui.shoppingCart_tableWidget_shoppingCart.setHorizontalHeaderLabels(["Image", "Name", "Price", "Amount", "Subtotal"])
        self.ui.shoppingCart_tableWidget_shoppingCart.horizontalHeader().setStretchLastSection(True)

        self.ui.shoppingCart_tableWidget_shoppingCart.itemSelectionChanged.connect(self.update_totals)

        self.cart_data = []
        self.load_cart()

    def load_cart(self):
        self.ui.shoppingCart_tableWidget_shoppingCart.setRowCount(0)
        self.cart_data.clear()

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.id AS cart_id, c.quantity, p.* FROM cart c
                JOIN products p ON c.product_id = p.id
                WHERE c.customer_id = %s
            """, (self.user['id'],))
            cart_items = cursor.fetchall()

            for row, item in enumerate(cart_items):
                self.ui.shoppingCart_tableWidget_shoppingCart.insertRow(row)

                image_item = QTableWidgetItem()
                if item['image_path'] and os.path.exists(item['image_path']):
                    pixmap = QPixmap(item['image_path'])
                    if not pixmap.isNull():
                        image_item.setIcon(QIcon(pixmap))
                image_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.ui.shoppingCart_tableWidget_shoppingCart.setItem(row, 0, image_item)

                name_item = QTableWidgetItem(item['name'])
                name_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.ui.shoppingCart_tableWidget_shoppingCart.setItem(row, 1, name_item)

                price_item = QTableWidgetItem(f"₱{item['price']:.2f}")
                price_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.ui.shoppingCart_tableWidget_shoppingCart.setItem(row, 2, price_item)

                spinbox = QSpinBox()
                spinbox.setRange(1, item['stock'])
                spinbox.setValue(item['quantity'])
                spinbox.valueChanged.connect(self.update_totals)
                self.ui.shoppingCart_tableWidget_shoppingCart.setCellWidget(row, 3, spinbox)

                subtotal = item['price'] * item['quantity']
                subtotal_item = QTableWidgetItem(f"₱{subtotal:.2f}")
                subtotal_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.ui.shoppingCart_tableWidget_shoppingCart.setItem(row, 4, subtotal_item)

                self.cart_data.append({
                    'cart_id': item['cart_id'],
                    'product_id': item['id'],
                    'stock': item['stock'],
                    'price': item['price'],
                    'spinbox': spinbox
                })

            self.update_totals()

        finally:
            if conn:
                conn.close()

    def update_totals(self):
        try:
            for row, data in enumerate(self.cart_data):
                qty = data['spinbox'].value()
                subtotal = data['price'] * qty
                subtotal_item = QTableWidgetItem(f"₱{subtotal:.2f}")
                subtotal_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.ui.shoppingCart_tableWidget_shoppingCart.setItem(row, 4, subtotal_item)

            total = 0
            selected = self.ui.shoppingCart_tableWidget_shoppingCart.selectionModel().selectedRows()
            for index in selected:
                row = index.row()
                item = self.ui.shoppingCart_tableWidget_shoppingCart.item(row, 4)
                if item:
                    subtotal_value = float(item.text().replace("₱", ""))
                    total += subtotal_value
            self.ui.shoppingCart_label_totalAmount.setText(f"₱{total:.2f}")
        except Exception as e:
            print(f"Update total error: {e}")

    def remove_item(self):
        selected_rows = sorted(set(index.row() for index in self.ui.shoppingCart_tableWidget_shoppingCart.selectedIndexes()), reverse=True)
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            for row in selected_rows:
                cart_id = self.cart_data[row]['cart_id']
                cursor.execute("DELETE FROM cart WHERE id = %s", (cart_id,))
            conn.commit()
            self.load_cart()
        finally:
            if conn:
                conn.close()

    def place_order(self):
        selected_rows = sorted(set(index.row() for index in self.ui.shoppingCart_tableWidget_shoppingCart.selectedIndexes()))
        if not selected_rows:
            self.ui.shoppingCart_label_Error.setText("Please select items to order.")
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            bought_items = []

            for row in selected_rows:
                data = self.cart_data[row]
                qty = data['spinbox'].value()

                if qty > data['stock']:
                    QMessageBox.warning(self, "Stock Error", f"Not enough stock for product ID {data['product_id']}")
                    return

                cursor.execute("""
                    INSERT INTO orders (product_id, buyer_id, quantity) VALUES (%s, %s, %s)
                """, (data['product_id'], self.user['id'], qty))

                cursor.execute("UPDATE products SET stock = stock - %s WHERE id = %s", (qty, data['product_id']))
                cursor.execute("DELETE FROM cart WHERE id = %s", (data['cart_id'],))

                cursor.execute("SELECT name FROM products WHERE id = %s", (data['product_id'],))
                product_name = cursor.fetchone()['name']

                bought_items.append((product_name, qty, data['price']))

            conn.commit()

            from windows.Confirm_Window import ConfirmWindow
            self.confirm_window = ConfirmWindow(bought_items, refresh_callback=self.back_to_customer)
            self.confirm_window.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
            self.confirm_window.show()
            self.close()

        finally:
            if conn:
                conn.close()

    def back_to_customer(self):
        self.customer_window = CustomerWindow(self.user)
        self.customer_window.show()