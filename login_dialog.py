from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLineEdit, QPushButton, QMessageBox)
from db_helper import DBHelper, DB_CONFIG
import re

class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("회원가입")
        self.resize(300, 200)
        self.db = DBHelper(**DB_CONFIG)

        # 입력 위젯 생성
        self.login_id = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.user_name = QLineEdit()
        self.email = QLineEdit()

        # 폼 레이아웃 설정
        form = QFormLayout()
        form.addRow("아이디", self.login_id)
        form.addRow("비밀번호", self.password)
        form.addRow("이름", self.user_name)
        form.addRow("이메일", self.email)

        # 가입 버튼
        self.btn_register = QPushButton("가입 완료")
        self.btn_register.clicked.connect(self.try_register)

        # 전체 레이아웃
        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.btn_register)
        self.setLayout(layout)

    def try_register(self):
        uid = self.login_id.text().strip()
        pw = self.password.text().strip()
        name = self.user_name.text().strip()
        email = self.email.text().strip()

        if not uid or not pw or not name or not email:
            QMessageBox.warning(self, "오류", "모든 항목을 빠짐없이 입력하세요.")
            return

        # 이메일 유효성 검사
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            QMessageBox.warning(self, "입력 오류", "유효한 이메일이 아닙니다.")
            return

        # 회원가입 시도
        success = self.db.register_user(uid, pw, name, email)
        if success:
            QMessageBox.information(self, "성공", "회원가입이 완료되었습니다.")
            self.accept()
        else:
            QMessageBox.critical(self, "실패", "회원가입에 실패\n아이디 중복 확인")


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("로그인")
        self.resize(300, 150)
        self.db = DBHelper(**DB_CONFIG)
        
        # 성공 시 딕셔너리변수
        self.logged_in_user = None 

        # 입력 위젯 생성
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)

        # 폼 설정
        form = QFormLayout()
        form.addRow("아이디", self.username)
        form.addRow("비밀번호", self.password)

        # 버튼 생성
        self.btn_login = QPushButton("로그인")
        self.btn_register = QPushButton("회원가입")

        # 이벤트 연결
        self.btn_login.clicked.connect(self.try_login)
        self.btn_register.clicked.connect(self.open_register)

        # 하단 버튼 레이아웃
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_login)
        btn_layout.addWidget(self.btn_register)

        # 전체 레이아웃
        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def try_login(self):
        uid = self.username.text().strip()
        pw = self.password.text().strip()
        
        if not uid or not pw:
            QMessageBox.warning(self, "오류", "아이디와 비밀번호를 모두 입력하세요.")
            return

        # DB에서 유저 정보 딕셔너리를 받아옴
        user_info = self.db.login_user(uid, pw)
        
        if user_info:
            # role, ID가 담긴 딕셔너리를 클래스 변수에 저장
            self.logged_in_user = user_info 
            self.accept()
        else:
            QMessageBox.critical(self, "실패", "아이디 또는 비밀번호가 올바르지 않습니다.")

    def open_register(self):
        # 회원가입 다이얼로그 호출
        reg_dialog = RegisterDialog(self)
        reg_dialog.exec_()    