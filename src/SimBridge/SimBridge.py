import pygame
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel


class SimBridge(QWidget):
    def __init__(self, game_loop_target_ms : int =20):
        super().__init__()
        self.init_ui()
        self.init_game_loop(game_loop_target_ms)
        pygame.init()

    def init_ui(self):
        self.resize(800, 600)
        self.setWindowTitle('SimBridge')

        # Top-level layout is a vertical box
        layout = QVBoxLayout()
        self.setLayout(layout)

        banner = self.init_banner()
        banner.setStyleSheet("background-color: #00fff0; ")
        layout.addWidget(banner)
        # Push content to the top
        layout.addStretch()

        # Create a form
        form = self.init_form()
        form.setStyleSheet("background-color: #fff0f0; ")
        layout.addWidget(form)
        layout.addStretch()


        self.show()

    def init_game_loop(self, target_ms : int = 20):
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.game_loop)
        self.game_timer.start(target_ms)

        self.game_loop_subscribers = []

    # Subscriber must implement on_game_loop
    def subscribe_to_game_loop(self, subscriber : object) -> None:
        self.game_loop_subscribers.append(subscriber)

    def unsubscribe_from_game_loop(self, subscriber : object) -> None:
        self.game_loop_subscribers.remove(subscriber)

    @staticmethod
    def init_banner():
        banner = QLabel("Press 'Esc' key to quit")
        banner.setAlignment(Qt.AlignCenter)  # Center horizontally
        banner.setStyleSheet("font-size: 24pt; font-weight: bold;")  # H1 style
        return banner

    def init_form(self):
        form = QWidget()
        layout = QVBoxLayout()
        form.setLayout(layout)

        # Add a label
        self.quick_label = QLabel("This is a form")
        self.quick_label.setStyleSheet("font-size: 16pt;")
        layout.addWidget(self.quick_label)
        layout.addStretch()

        return form

    def keyPressEvent(self, event : pygame.event.Event) -> None:
        if event.key() == Qt.Key_Escape:
            # Quit the application
            self.close()

    def set_quick_label(self, text : str) -> None:
        self.quick_label.setText(text)

    def game_loop(self):
        pygame.event.pump()
        for subscribers in self.game_loop_subscribers:
            subscribers.on_game_loop()
