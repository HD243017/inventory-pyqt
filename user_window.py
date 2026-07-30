from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QListWidgetItem, QLabel, QPushButton, QSpinBox, 
                             QTextEdit, QMessageBox, QDialog, QTableWidget, 
                             QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt

class OrderHistoryDialog(QDialog):
    def __init__(self, orders, parent=None):
        super().__init__(parent)
        self.setWindowTitle("내 주문 내역")
        self.resize(500, 300)
        
        # 메인 창에서 이미 가져온 orders 변수에 저장합니다.
        self.orders = orders 
        
        self.init_ui()
        self.load_history()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # 테이블 위젯 설정
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["주문 번호", "제품명", "수량", "주문 일자"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) # 읽기 전용
        
        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_history(self):
        # DB를 다시 조회할 필요 없이 넘겨받은 self.orders로 바로 표를 그림
        self.table.setRowCount(len(self.orders))
        for row, order in enumerate(self.orders):
            self.table.setItem(row, 0, QTableWidgetItem(str(order['order_ID'])))
            self.table.setItem(row, 1, QTableWidgetItem(order['product_name']))
            
            self.table.setItem(row, 2, QTableWidgetItem(f"{order.get('orders_qty', order.get('qty', 0))}개"))
            
            self.table.setItem(row, 3, QTableWidgetItem(str(order['order_date'])))


class UserWindow(QWidget):
    def __init__(self, user_info, db):
        super().__init__()
        self.user_info = user_info # 로그인 창에서 넘겨받은 딕셔너리
        self.db = db
        
        self.setWindowTitle(f"주문 시스템 - {self.user_info['user_name']}님 환영합니다")
        self.resize(700, 500)
        
        self.selected_product = None # 현재 선택된 상품 정보 저장용
        
        self.init_ui()
        self.load_products()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # 좌측 레이아웃
        left_layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.on_product_selected)
        left_layout.addWidget(QLabel("완제품 목록"))
        left_layout.addWidget(self.list_widget)
        
        # 우측 레이아웃
        right_layout = QVBoxLayout()
        
        # [주문내역] 버튼 (맨 위)
        self.btn_history = QPushButton("내 주문내역 보기")
        self.btn_history.clicked.connect(self.show_order_history)
        right_layout.addWidget(self.btn_history)
        
        # 상품 정보 표시 창
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setPlaceholderText("왼쪽에서 제품을 선택해주세요.")
        right_layout.addWidget(QLabel("상품 상세 정보"))
        right_layout.addWidget(self.info_text)
        
        # 수량 및 총액 레이아웃 (가로 정렬)
        price_layout = QHBoxLayout()
        
        price_layout.addWidget(QLabel("수량:"))
        self.spin_qty = QSpinBox()
        self.spin_qty.setMinimum(1)
        self.spin_qty.setValue(1)
        self.spin_qty.valueChanged.connect(self.update_total_price) # 수량 변경 시 총액 업데이트
        price_layout.addWidget(self.spin_qty)
        
        price_layout.addStretch() # 중간 빈 공간 확보
        
        self.lbl_total_price = QLabel("총 결제 금액: 0원")
        self.lbl_total_price.setStyleSheet("font-weight: bold; font-size: 14px; color: blue;")
        price_layout.addWidget(self.lbl_total_price)
        
        right_layout.addLayout(price_layout)
        
        # [주문 확정] 버튼 (맨 아래)
        self.btn_order = QPushButton("주문 확정")
        self.btn_order.setMinimumHeight(40)
        self.btn_order.clicked.connect(self.place_order)
        right_layout.addWidget(self.btn_order)

        # 메인 레이아웃 병합
        main_layout.addLayout(left_layout, 1) # 좌측 비율 1
        main_layout.addLayout(right_layout, 2) # 우측 비율 2
        
        self.setLayout(main_layout)

    def load_products(self):
        # DB에서 완제품 목록을 가져와 리스트에 뿌림
        self.list_widget.clear()
        products = self.db.get_all_products()
        
        for p in products:
            item = QListWidgetItem(p['product_name'])
            item.setData(Qt.UserRole, p)
            self.list_widget.addItem(item)

    def on_product_selected(self, item):
        # 제품을 클릭했을 때 우측 정보를 업데이트
        self.selected_product = item.data(Qt.UserRole)
        p_id = self.selected_product['product_ID']
        p_name = self.selected_product['product_name']
        p_price = self.selected_product['product_price']
        
        # DB에서 해당 제품의 BOM 가져옴
        bom_details = self.db.get_product_bom_detail(p_id)
        
        # 정보 텍스트 포맷팅
        info = f"<h2>{p_name}</h2>"
        info += f"<p><b>가격:</b> {p_price:,}원</p>"
        info += "<hr><p><b>[주요 구성 부품]</b></p><ul>"
        
        for bom in bom_details:
            info += f"<li>{bom['part_name']} (x{bom['required_qty']})</li>"
        info += "</ul>"
        
        self.info_text.setHtml(info)
        
        # 수량 1로 초기화 및 총액 업데이트
        self.spin_qty.setValue(1)
        self.update_total_price()

    def update_total_price(self):
        # 수량 증감 시 총액 라벨을 변경
        if not self.selected_product:
            return
            
        qty = self.spin_qty.value()
        price = self.selected_product['product_price']
        total = qty * price
        
        self.lbl_total_price.setText(f"총 결제 금액: {total:,}원")

    def place_order(self):
        # 주문 확정 버튼 클릭 시 DB에 주문
        if not self.selected_product:
            QMessageBox.warning(self, "안내", "먼저 구매할 제품을 선택해주세요.")
            return
            
        product_id = self.selected_product['product_ID']
        product_name = self.selected_product['product_name']
        qty = self.spin_qty.value()
        
        # 확인창 띄우기
        reply = QMessageBox.question(
            self, '주문 확인', 
            f"{product_name} {qty}개를 주문하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # db_helper의 place_order 호출
            success = self.db.place_order(self.user_info['user_ID'], product_id, qty)
            
            if success:
                QMessageBox.information(self, "성공", "주문이 완료되었습니다!")
                self.spin_qty.setValue(1) # 수량 초기화
            else:
                QMessageBox.critical(self, "실패", "주문 처리 중 오류가 발생했습니다.")

    def show_order_history(self):
        orders = self.db.get_orders(self.user_info['user_ID'])
        
        if not orders:
            QMessageBox.information(self, "알림", "주문내역이 없습니다.")
            return
            
        dialog = OrderHistoryDialog(orders, self)
        dialog.exec_()