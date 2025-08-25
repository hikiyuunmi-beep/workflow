import sys
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout,
                             QHeaderView, QMessageBox)
from add_task_dialog import AddTaskDialog

class MainWindow(QMainWindow):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.base_url = "http://127.0.0.1:5000"

        self.setWindowTitle('Sistema de Tarefas')
        self.setGeometry(100, 100, 800, 600)

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Table for tasks ---
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(4)
        self.task_table.setHorizontalHeaderLabels(['ID', 'Título', 'Status', 'Data de Vencimento'])
        self.task_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.task_table.setEditTriggers(QTableWidget.NoEditTriggers) # Make table read-only
        main_layout.addWidget(self.task_table)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        self.add_task_button = QPushButton('Adicionar Tarefa')
        self.refresh_button = QPushButton('Atualizar')
        self.logout_button = QPushButton('Logout')

        button_layout.addStretch(1)
        button_layout.addWidget(self.add_task_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.logout_button)
        main_layout.addLayout(button_layout)

        # --- Button Connections ---
        self.add_task_button.clicked.connect(self.open_add_task_dialog)
        self.refresh_button.clicked.connect(self.load_tasks)
        # self.logout_button.clicked.connect(self.handle_logout) # Will implement later

        # --- Initial data load ---
        self.load_tasks()

    def open_add_task_dialog(self):
        dialog = AddTaskDialog(self.session, self.base_url, self)
        # Connect the dialog's signal to the load_tasks slot
        dialog.task_added.connect(self.load_tasks)
        dialog.exec_()

    def load_tasks(self):
        try:
            response = self.session.get(f"{self.base_url}/api/tasks")

            if response.status_code == 200:
                tasks = response.json()
                self.task_table.setRowCount(len(tasks))

                for row, task in enumerate(tasks):
                    self.task_table.setItem(row, 0, QTableWidgetItem(str(task.get('id'))))
                    self.task_table.setItem(row, 1, QTableWidgetItem(task.get('title')))
                    self.task_table.setItem(row, 2, QTableWidgetItem(task.get('status')))
                    due_date = task.get('due_date') or 'N/A'
                    self.task_table.setItem(row, 3, QTableWidgetItem(due_date))
            elif response.status_code == 401:
                QMessageBox.critical(self, 'Erro de Autenticação', 'Sua sessão expirou. Por favor, faça login novamente.')
                self.close() # Or redirect to login
            else:
                QMessageBox.warning(self, 'Erro', f"Não foi possível carregar as tarefas: {response.json().get('error')}")

        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, 'Erro de Conexão', 'Não foi possível conectar ao servidor.')
            self.task_table.setRowCount(0) # Clear table on error


if __name__ == '__main__':
    # This part is for testing the MainWindow directly.
    # In the final app, it will be launched from login.py
    class MockSession:
        def get(self, url):
            print(f"Mocking GET request to {url}")
            class MockResponse:
                status_code = 200
                def json(self):
                    return [
                        {'id': 1, 'title': 'Teste 1', 'status': 'Pendente', 'due_date': '2025-01-01'},
                        {'id': 2, 'title': 'Teste 2', 'status': 'Concluída', 'due_date': None},
                    ]
            return MockResponse()

        def post(self, url, json):
            print(f"Mocking POST request to {url} with data {json}")
            class MockResponse:
                status_code = 201
                def json(self):
                    return {'id': 3, **json}
            return MockResponse()

    app = QApplication(sys.argv)
    mock_session = MockSession()
    main_win = MainWindow(session=mock_session)
    main_win.show()
    sys.exit(app.exec_())
