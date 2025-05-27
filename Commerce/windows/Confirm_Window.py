from PyQt6.QtWidgets import QMainWindow, QListWidgetItem
from ui.Confirm_UI import Ui_confirm_MainWindow

class ConfirmWindow(QMainWindow):
    def __init__(self, bought_items, refresh_callback=None):
        super().__init__()
        self.ui = Ui_confirm_MainWindow()
        self.ui.setupUi(self)
        self.refresh_callback = refresh_callback

        self.ui.confirm_pushButton_continueShopping.clicked.connect(self.continue_shopping)

        total_amount = 0
        for product_name, quantity, price in bought_items:
            subtotal = quantity * price
            total_amount += subtotal
            item_text = f"{quantity}x {product_name} — ₱{subtotal:.2f}"
            list_item = QListWidgetItem(item_text)
            self.ui.confirm_listWidget_list.addItem(list_item)

        self.ui.confirm_label_totalValue.setText(f"₱{total_amount:.2f}")

    def continue_shopping(self):
        if self.refresh_callback:
            self.refresh_callback()
        self.close()
