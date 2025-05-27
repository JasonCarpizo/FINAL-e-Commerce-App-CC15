import os
import shutil
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from ui.AddProduct_UI import Ui_addProduct_MainWindow
from db import connect_to_database


class AddProductWindow(QMainWindow):
    def __init__(self, seller_id, refresh_callback):
        super().__init__()
        self.ui = Ui_addProduct_MainWindow()
        self.ui.setupUi(self)
        self.seller_id = seller_id
        self.refresh_callback = refresh_callback

        self.ui.addProduct_pushButton_back.clicked.connect(self.close)
        self.ui.addProduct_pushButton_browseFiles.clicked.connect(self.browse_image)
        self.ui.addProduct_pushButton_savePublish.clicked.connect(self.save_product)
        self.image_path = None

    def browse_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Select Product Image", "", "Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            filename = os.path.basename(file_path)
            new_path = os.path.join("images", filename)
            shutil.copy(file_path, new_path)
            self.image_path = new_path
            self.ui.addProduct_lineEdit_productImage.setText(new_path)

    def save_product(self):
        name = self.ui.addProduct_lineEdit_productName.text().strip()
        category = self.ui.addProduct_comboBox_category.currentText()
        price_text = self.ui.addProduct_lineEdit_price.text().strip()
        stock_text = self.ui.addProduct_lineEdit_stock.text().strip()

        if not name or not category or not price_text or not stock_text:
            self.ui.addProduct_label_Error.setText("All fields except image are required.")
            return

        try:
            price = float(price_text)
            stock = int(stock_text)

            if price <= 0:
                self.ui.addProduct_label_Error.setText("Price must be greater than 0.")
                return
            if stock < 0:
                self.ui.addProduct_label_Error.setText("Stock cannot be negative.")
                return
        except ValueError:
            self.ui.addProduct_label_Error.setText("Price must be decimal, stock must be integer.")
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO products (seller_id, name, category, price, stock, image_path)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (self.seller_id, name, category, price, stock, self.image_path))
            conn.commit()
            self.refresh_callback()
            QMessageBox.information(self, "Success", "Product added successfully!")
            self.close()
        except Exception as e:
            self.ui.addProduct_label_Error.setText(f"DB Error: {str(e)}")
        finally:
            if conn:
                conn.close()
