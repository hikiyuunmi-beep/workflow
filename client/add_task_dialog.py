from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                             QTextEdit, QPushButton, QDialogButtonBox, QMessageBox, QCalendarWidget)
from PyQt5.QtCore import pyqtSignal

class AddTaskDialog(QDialog):
    # Signal that will be emitted when a task is successfully added
    task_added = pyqtSignal()

    def __init__(self, session, base_url, parent=None):
        super().__init__(parent)
        self.session = session
        self.base_url = base_url

        self.setWindowTitle('Adicionar Nova Tarefa')
        layout = QVBoxLayout(self)

        # Title
        self.title_label = QLabel('Título:')
        self.title_input = QLineEdit()
        layout.addWidget(self.title_label)
        layout.addWidget(self.title_input)

        # Description
        self.desc_label = QLabel('Descrição:')
        self.desc_input = QTextEdit()
        layout.addWidget(self.desc_label)
        layout.addWidget(self.desc_input)

        # Due Date
        self.date_label = QLabel('Data de Vencimento:')
        self.date_input = QCalendarWidget()
        layout.addWidget(self.date_label)
        layout.addWidget(self.date_input)

        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def accept(self):
        title = self.title_input.text()
        description = self.desc_input.toPlainText()
        due_date = self.date_input.selectedDate().toString("yyyy-MM-ddT00:00:00")

        if not title:
            QMessageBox.warning(self, 'Erro', 'O título da tarefa é obrigatório.')
            return

        payload = {
            "title": title,
            "description": description,
            "due_date": due_date
        }

        try:
            response = self.session.post(f"{self.base_url}/api/tasks", json=payload)
            if response.status_code == 201:
                QMessageBox.information(self, 'Sucesso', 'Tarefa adicionada com sucesso!')
                self.task_added.emit() # Emit the signal
                super().accept()
            else:
                error_message = response.json().get("error", "Erro desconhecido")
                QMessageBox.critical(self, 'Erro ao Salvar', error_message)
        except Exception as e:
            QMessageBox.critical(self, 'Erro de Conexão', f'Não foi possível adicionar a tarefa: {e}')
            super().reject()
