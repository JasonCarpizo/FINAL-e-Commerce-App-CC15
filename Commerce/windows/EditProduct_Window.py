from PyQt6.QtWidgets import QMainWindow, QMessageBox
from ui.EditProduct_UI import Ui_editProduct_MainWindow
from db import connect_to_database


class EditProductWindow(QMainWindow):
    def __init__(self, product_id, refresh_callback):
        super().__init__()
        self.ui = Ui_editProduct_MainWindow()
        self.ui.setupUi(self)
        self.product_id = product_id
        self.refresh_callback = refresh_callback

        self.ui.editProduct_pushButton_back.clicked.connect(self.close)
        self.ui.editProduct_comboBox_options.currentTextChanged.connect(self.toggle_input_visibility)
        self.ui.editProduct_lineEdit_editValue.hide()

        self.ui.editProduct_pushButton_confirm.clicked.connect(self.confirm_action)
        self.load_product_info()

    def toggle_input_visibility(self, text):
        self.ui.editProduct_lineEdit_editValue.setVisible(text != "Remove Product")

    def load_product_info(self):
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("SELECT name, stock FROM products WHERE id = %s", (self.product_id,))
            result = cursor.fetchone()
            if result:
                self.ui.editProduct_label_productName.setText(result['name'])
                self.ui.editProduct_label_stock.setText(f"Stock: {result['stock']}")
        finally:
            if conn:
                conn.close()

    def confirm_action(self):
        action = self.ui.editProduct_comboBox_options.currentText()
        value = self.ui.editProduct_lineEdit_editValue.text().strip()

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            if action == "Remove Product":
                cursor.execute("DELETE FROM products WHERE id = %s", (self.product_id,))
            elif action == "Edit Stock":
                if not value.isdigit() or int(value) < 0:
                    self.ui.editProduct_label_Error.setText("Invalid stock value.")
                    return
                cursor.execute("UPDATE products SET stock = %s WHERE id = %s", (int(value), self.product_id))
            elif action == "Edit Price":
                try:
                    price = float(value)
                    if price <= 0:
                        raise ValueError
                    cursor.execute("UPDATE products SET price = %s WHERE id = %s", (price, self.product_id))
                except:
                    self.ui.editProduct_label_Error.setText("Invalid price value.")
                    return

            conn.commit()
            self.refresh_callback()
            QMessageBox.information(self, "Success", f"{action} successful.")
            self.close()
        except Exception as e:
            self.ui.editProduct_label_Error.setText(f"DB Error: {e}")
        finally:
            if conn:
                conn.close()
