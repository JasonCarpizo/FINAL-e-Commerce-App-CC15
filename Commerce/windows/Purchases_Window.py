from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from ui.Purchases_UI import Ui_myPurchases_MainWindow
from db import connect_to_database
import os
from PyQt6.QtGui import QIcon

class PurchasesWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.ui = Ui_myPurchases_MainWindow()
        self.ui.setupUi(self)
        self.user = user

        self.ui.myPurchases_pushButton_back.clicked.connect(self.close)

        self.ui.myPurchases_tableWidget_transactionHistory.setColumnCount(5)
        self.ui.myPurchases_tableWidget_transactionHistory.setHorizontalHeaderLabels(["Image", "Name", "Price", "Amount", "Total"])
        self.ui.myPurchases_tableWidget_transactionHistory.horizontalHeader().setStretchLastSection(True)

        self.load_purchases()

    def load_purchases(self):
        self.ui.myPurchases_tableWidget_transactionHistory.setRowCount(0)

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.quantity, p.name, p.image_path, p.price
                FROM orders o
                JOIN products p ON o.product_id = p.id
                WHERE o.buyer_id = %s
            """, (self.user['id'],))

            orders = cursor.fetchall()

            for row, order in enumerate(orders):
                self.ui.myPurchases_tableWidget_transactionHistory.insertRow(row)

                img_item = QTableWidgetItem()
                if order['image_path'] and os.path.exists(order['image_path']):
                    pixmap = QPixmap(order['image_path'])
                    if not pixmap.isNull():
                        img_item.setIcon(QIcon(pixmap))
                img_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.ui.myPurchases_tableWidget_transactionHistory.setItem(row, 0, img_item)

                name_item = QTableWidgetItem(order['name'])
                name_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.ui.myPurchases_tableWidget_transactionHistory.setItem(row, 1, name_item)

                price_item = QTableWidgetItem(f"₱{order['price']:.2f}")
                price_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.ui.myPurchases_tableWidget_transactionHistory.setItem(row, 2, price_item)

                qty_item = QTableWidgetItem(str(order['quantity']))
                qty_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.ui.myPurchases_tableWidget_transactionHistory.setItem(row, 3, qty_item)

                total = order['quantity'] * order['price']
                total_item = QTableWidgetItem(f"₱{total:.2f}")
                total_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.ui.myPurchases_tableWidget_transactionHistory.setItem(row, 4, total_item)

        finally:
            if conn:
                conn.close()