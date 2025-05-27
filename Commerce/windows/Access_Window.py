from PyQt6 import QtWidgets
from ui.Access_UI import Ui_access_MainWindow
from db import connect_to_database


class AccessWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_access_MainWindow()
        self.ui.setupUi(self)

        self.ui.accessLogin_pushButton_login.clicked.connect(self.login)
        self.ui.accessLogin_pushButton_createAcc.clicked.connect(lambda: self.ui.access_stackedWidget.setCurrentIndex(1))
        self.ui.accessSignup_pushButton_logintoAcc.clicked.connect(lambda: self.ui.access_stackedWidget.setCurrentIndex(0))
        self.ui.accessSignup_pushButton_signup.clicked.connect(self.signup)

    def login(self):
        username = self.ui.accessLogin_lineEdit_username.text().strip()
        password = self.ui.accessLogin_lineEdit_password.text().strip()
        account_type = self.ui.accessLogin_comboBox_custSeller.currentText()

        if not username or not password:
            self.ui.accessLogin_label_Error.setText("All fields are required.")
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()

            table = "customers" if account_type == "Customer" else "sellers"
            cursor.execute(f"SELECT * FROM {table} WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()

            if user:
                self.ui.accessLogin_label_Error.setText("")
                self.launch_main_window(user, account_type)
            else:
                self.ui.accessLogin_label_Error.setText("Invalid username or password.")
        except Exception as e:
            self.ui.accessLogin_label_Error.setText(f"Login error: {e}")
        finally:
            if conn:
                conn.close()

    def launch_main_window(self, user, account_type):
        if account_type == "Customer":
            from windows.Customer_Window import CustomerWindow
            self.new_window = CustomerWindow(user)
        else:
            from windows.Seller_Window import SellerWindow
            self.new_window = SellerWindow(user)

        self.new_window.show()
        self.close()

    def signup(self):
        username = self.ui.accessSignup_lineEdit_username.text().strip()
        password = self.ui.accessSignup_lineEdit_password.text().strip()
        fullname = self.ui.accessSignup_lineEdit_fullname.text().strip()
        number = self.ui.accessSignup_lineEdit_number.text().strip()
        address = self.ui.accessSignup_lineEdit_address.text().strip()
        account_type = self.ui.accessSignup_comboBox_custSeller.currentText()

        if not all([username, password, fullname, number, address]):
            self.ui.accessSignup_label_Error.setText("All fields are required.")
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()

            table = "customers" if account_type == "Customer" else "sellers"
            cursor.execute(f"SELECT id FROM {table} WHERE username = %s", (username,))
            if cursor.fetchone():
                self.ui.accessSignup_label_Error.setText("Username already exists.")
                return

            cursor.execute(
                f"INSERT INTO {table} (username, password, fullname, number, address) VALUES (%s, %s, %s, %s, %s)",
                (username, password, fullname, number, address)
            )
            conn.commit()
            self.ui.accessSignup_label_Error.setText("Account created. Please log in.")
            self.ui.access_stackedWidget.setCurrentIndex(0)
        except Exception as e:
            self.ui.accessSignup_label_Error.setText(f"Signup error: {e}")
        finally:
            if conn:
                conn.close()
