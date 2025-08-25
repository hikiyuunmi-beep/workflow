import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from main_window import MainWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.main_win = None
        self.session = requests.Session()
        self.base_url = "http://127.0.0.1:5000"
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Login do Sistema de Tarefas')
        self.setGeometry(300, 300, 300, 150)

        layout = QVBoxLayout()

        # Username
        self.user_label = QLabel('Usuário:')
        self.user_input = QLineEdit()
        layout.addWidget(self.user_label)
        layout.addWidget(self.user_input)

        # Password
        self.pass_label = QLabel('Senha:')
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pass_label)
        layout.addWidget(self.pass_input)

        # Login Button
        self.login_button = QPushButton('Login')
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def handle_login(self):
        username = self.user_input.text()
        password = self.pass_input.text()

        if not username or not password:
            QMessageBox.warning(self, 'Erro', 'Usuário e senha são obrigatórios.')
            return

        try:
            response = self.session.post(
                f"{self.base_url}/api/login",
                json={"username": username, "password": password}
            )

            if response.status_code == 200:
                self.open_main_window()
            else:
                error_message = response.json().get("error", "Erro desconhecido")
                QMessageBox.critical(self, 'Falha no Login', error_message)

        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, 'Erro de Conexão', 'Não foi possível conectar ao servidor. Verifique se o backend está rodando.')

    def open_main_window(self):
        # Pass the authenticated session to the main window
        self.main_win = MainWindow(self.session)
        self.main_win.show()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_win = LoginWindow()
    login_win.show()
    sys.exit(app.exec_())
