import sys
from PyQt5.QtWidgets import QApplication, QDialog
from login_dialog import LoginDialog
from user_window import UserWindow
from admin_window import AdminWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 로그인 창
    login = LoginDialog()
    
    # 로그인이 성공적으로 완료때만 다음으로 진행
    if login.exec_() == QDialog.Accepted:
        user = login.logged_in_user # 로그인 창에서 저장해둔 유저 정보 딕셔너리
        db_instance = login.db      # 로그인 창에서 사용했던 DB 연결 객체 재사용
        
        print(f"로그인 성공: {user['user_name']}님 (권한: {user['role']})")
        
        # 3. role에 따라 다른 화면 띄우기
        if user['role'] in ('admin', 'root'):
            window = AdminWindow(user, db_instance)
        else:
            # 일반 유저일 경우
            window = UserWindow(user, db_instance)
             
        window.show()
        sys.exit(app.exec_())
        
    else:
        # 로그인 창을 그냥 닫거나 취소한 경우 프로그램 종료
        print("프로그램을 종료합니다.")
        sys.exit(0)