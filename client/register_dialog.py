import requests
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QDialogButtonBox, QMessageBox)

class RegisterDialog(QDialog):
    def __init__(self, base_url, parent=None):
        super().__init__(parent)
        self.base_url = base_url

        self.setWindowTitle('Registrar Novo Usuário')
        layout = QVBoxLayout(self)

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

        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Ok).setText("Registrar")
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def accept(self):
        username = self.user_input.text()
        password = self.pass_input.text()

        if not username or not password:
            QMessageBox.warning(self, 'Erro', 'Usuário e senha são obrigatórios.')
            return

        payload = {"username": username, "password": password}

        try:
            response = requests.post(f"{self.base_url}/api/register", json=payload)

            if response.status_code == 201:
                QMessageBox.information(self, 'Sucesso', 'Usuário registrado com sucesso! Você já pode fazer login.')
                super().accept()
            else:
                error_message = response.json().get("error", "Erro desconhecido ao registrar.")
                QMessageBox.critical(self, 'Erro de Registro', error_message)

        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, 'Erro de Conexão', 'Não foi possível conectar ao servidor.')
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Ocorreu um erro inesperado: {e}')
