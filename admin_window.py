from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QPushButton, QLabel, QLineEdit, QListWidget, 
                             QListWidgetItem, QMessageBox, QDialog, QFormLayout,
                             QSpinBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

# [다이얼로그] 부품 추가 창
class AddPartDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("새 부품 추가")
        self.resize(300, 200)

        self.name_input = QLineEdit()
        self.price_input = QLineEdit()
        self.stock_input = QSpinBox()
        self.stock_input.setMaximum(99999)

        form = QFormLayout()
        form.addRow("부품명:", self.name_input)
        form.addRow("단가(가격):", self.price_input)
        form.addRow("초기 재고:", self.stock_input)

        self.btn_save = QPushButton("부품 등록")
        self.btn_save.clicked.connect(self.check_and_accept)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.btn_save)
        self.setLayout(layout)

    def check_and_accept(self):
        if not self.name_input.text() or not self.price_input.text():
            QMessageBox.warning(self, "경고", "모든 항목을 입력하세요.")
            return
        self.accept()

    def get_data(self):
        return (self.name_input.text(), int(self.price_input.text()), self.stock_input.value())

# [다이얼로그] 제품 추가 창
class AddProductDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("새 제품 및 BOM 추가")
        self.resize(500, 400)

        self.name_input = QLineEdit()
        self.price_input = QLineEdit()

        form = QFormLayout()
        form.addRow("제품명:", self.name_input)
        form.addRow("판매가:", self.price_input)

        self.part_table = QTableWidget()
        self.part_table.setColumnCount(3)
        self.part_table.setHorizontalHeaderLabels(["선택", "부품명", "필요 수량"])
        self.part_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.load_parts_to_table()

        self.btn_save = QPushButton("등록 전 확인")
        self.btn_save.clicked.connect(self.confirm_and_accept)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(QLabel("구성 부품 선택"))
        layout.addWidget(self.part_table)
        layout.addWidget(self.btn_save)
        self.setLayout(layout)

    def load_parts_to_table(self):
        parts = self.db.get_all_parts()
        self.part_table.setRowCount(len(parts))
        
        for row, part in enumerate(parts):
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chk_item.setCheckState(Qt.Unchecked)
            chk_item.setData(Qt.UserRole, part['part_ID']) 
            
            name_item = QTableWidgetItem(part['part_name'])
            name_item.setFlags(Qt.ItemIsEnabled) 
            
            spin_qty = QSpinBox()
            spin_qty.setMinimum(1)
            
            self.part_table.setItem(row, 0, chk_item)
            self.part_table.setItem(row, 1, name_item)
            self.part_table.setCellWidget(row, 2, spin_qty)

    def confirm_and_accept(self):
        name = self.name_input.text()
        price = self.price_input.text()
        
        if not name or not price:
            QMessageBox.warning(self, "경고", "제품명과 가격을 입력하세요.")
            return

        self.selected_boms = []
        bom_names = [] 
        
        for row in range(self.part_table.rowCount()):
            chk_item = self.part_table.item(row, 0)
            if chk_item.checkState() == Qt.Checked:
                part_id = chk_item.data(Qt.UserRole)
                part_name = self.part_table.item(row, 1).text()
                qty = self.part_table.cellWidget(row, 2).value()
                
                self.selected_boms.append({'part_id': part_id, 'qty': qty})
                bom_names.append(f"{part_name} (x{qty})")

        if not self.selected_boms:
            QMessageBox.warning(self, "경고", "최소 1개 이상의 부품을 선택해야 합니다.")
            return

        confirm_msg = f"제품명: {name}\n가격: {price}원\n\n[구성 부품]\n"
        confirm_msg += "\n".join(bom_names)
        confirm_msg += "\n\n이 내용으로 등록하시겠습니까?"

        reply = QMessageBox.question(self, '등록 확인', confirm_msg, QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.accept()

    def get_data(self):
        return (self.name_input.text(), int(self.price_input.text()), self.selected_boms)


# [메인] 관리자 창
class AdminWindow(QWidget):
    def __init__(self, user_info, db):
        super().__init__()
        self.user_info = user_info
        self.db = db
        self.setWindowTitle(f"관리자 시스템 - {self.user_info['user_name']} (root)")
        self.resize(900, 600)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.tabs = QTabWidget()
        
        self.tab_dashboard = QWidget()
        self.tab_restock = QWidget()
        self.tab_products = QWidget() 
        self.tab_parts = QWidget()    
        self.tab_orders = QWidget()
        self.tab_users = QWidget()
        
        self.tabs.addTab(self.tab_dashboard, "재고현황")
        self.tabs.addTab(self.tab_restock, "재고주문")
        self.tabs.addTab(self.tab_products, "제품 목록")
        self.tabs.addTab(self.tab_parts, "부품 목록")
        self.tabs.addTab(self.tab_orders, "전체 주문내역")
        self.tabs.addTab(self.tab_users, "회원정보")
        
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

        # 모든 탭 구성 함수 호출
        self.setup_dashboard_tab()
        self.setup_restock_tab()
        self.setup_products_tab()
        self.setup_parts_tab()
        self.setup_orders_tab()
        self.setup_users_tab()
        
        self.tabs.currentChanged.connect(self.refresh_data)

    # 탭: 재고현황
    def setup_dashboard_tab(self):
        layout = QVBoxLayout()
        self.table_stock = QTableWidget()
        self.table_stock.setColumnCount(3)
        self.table_stock.setHorizontalHeaderLabels(["부품 번호", "부품명", "현재 재고"])
        self.table_stock.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_stock.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(QLabel(""))
        layout.addWidget(self.table_stock)
        self.tab_dashboard.setLayout(layout)
        self.load_dashboard_data()

    def load_dashboard_data(self):
        parts = self.db.get_all_parts()
        if parts is None: return
        self.table_stock.setRowCount(len(parts))
        for row, part in enumerate(parts):
            id_item = QTableWidgetItem(str(part['part_ID']))
            name_item = QTableWidgetItem(part['part_name'])
            stock_item = QTableWidgetItem(f"{part['stock']}개")
            
            if part['stock'] <= 0:
                id_item.setForeground(QColor("red"))
                name_item.setForeground(QColor("red"))
                stock_item.setForeground(QColor("red"))
            elif part['stock'] < 10:
                id_item.setForeground(QColor("orange"))
                name_item.setForeground(QColor("orange"))
                stock_item.setForeground(QColor("orange"))
                
            self.table_stock.setItem(row, 0, id_item)
            self.table_stock.setItem(row, 1, name_item)
            self.table_stock.setItem(row, 2, stock_item)

    # 탭: 재고주문
    def setup_restock_tab(self):
        layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("1. 부품 선택"))
        self.list_parts_restock = QListWidget()
        left_layout.addWidget(self.list_parts_restock)
        
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("2. 입고 수량 입력"))
        self.input_qty = QLineEdit("0")
        right_layout.addWidget(self.input_qty)
        
        btn_layout = QHBoxLayout()
        btn_plus_1 = QPushButton("+1")
        btn_plus_10 = QPushButton("+10")
        btn_plus_100 = QPushButton("+100")
        
        btn_plus_1.clicked.connect(lambda: self.add_to_qty(1))
        btn_plus_10.clicked.connect(lambda: self.add_to_qty(10))
        btn_plus_100.clicked.connect(lambda: self.add_to_qty(100))
        
        btn_layout.addWidget(btn_plus_1)
        btn_layout.addWidget(btn_plus_10)
        btn_layout.addWidget(btn_plus_100)
        right_layout.addLayout(btn_layout)
        
        btn_apply = QPushButton("재고 반영")
        btn_apply.setMinimumHeight(50)
        btn_apply.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        btn_apply.clicked.connect(self.apply_restock)
        right_layout.addWidget(btn_apply)
        right_layout.addStretch()
        
        layout.addLayout(left_layout, 1)
        layout.addLayout(right_layout, 1)
        self.tab_restock.setLayout(layout)
        self.load_restock_list()

    def add_to_qty(self, amount):
        try:
            current = int(self.input_qty.text())
        except ValueError:
            current = 0
        self.input_qty.setText(str(current + amount))

    def load_restock_list(self):
        self.list_parts_restock.clear()
        parts = self.db.get_all_parts()
        if parts is None: return
        for p in parts:
            item = QListWidgetItem(f"{p['part_name']} (현재: {p['stock']}개)")
            item.setData(Qt.UserRole, p['part_ID'])
            self.list_parts_restock.addItem(item)

    def apply_restock(self):
        selected_item = self.list_parts_restock.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "경고", "목록에서 부품을 먼저 선택해주세요.")
            return
        try:
            add_qty = int(self.input_qty.text())
            if add_qty <= 0: raise ValueError
        except ValueError:
            QMessageBox.warning(self, "경고", "올바른 수량을 입력해주세요.")
            return
            
        part_id = selected_item.data(Qt.UserRole)
        if self.db.add_part_stock(part_id, add_qty):
            QMessageBox.information(self, "성공", f"재고 {add_qty}개가 추가되었습니다!")
            self.input_qty.setText("0")
            self.refresh_data()
        else:
            QMessageBox.critical(self, "실패", "재고 반영에 실패했습니다.")

    # 탭: 완제품
    def setup_products_tab(self):
        layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        self.list_products = QListWidget()
        self.list_products.itemClicked.connect(self.show_product_detail)
        left_layout.addWidget(QLabel("제품 목록"))
        left_layout.addWidget(self.list_products)
        
        right_layout = QVBoxLayout()
        self.product_info = QLabel("좌측에서 제품을 선택하세요.")
        self.product_info.setAlignment(Qt.AlignTop)
        self.product_info.setStyleSheet("background-color: white; padding: 10px; border: 1px solid #ccc;")
        
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("제품 추가")
        btn_del = QPushButton("선택 제품 삭제")
        btn_add.clicked.connect(self.open_add_product_dialog)
        btn_del.clicked.connect(self.delete_selected_product)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_del)
        
        right_layout.addWidget(QLabel("상세 정보 및 BOM"))
        right_layout.addWidget(self.product_info, 1) 
        right_layout.addLayout(btn_layout)
        
        layout.addLayout(left_layout, 1)
        layout.addLayout(right_layout, 2)
        self.tab_products.setLayout(layout)
        self.load_products_list()

    def load_products_list(self):
        self.list_products.clear()
        products = self.db.get_all_products()
        if products is None: return
        for p in products:
            item = QListWidgetItem(p['product_name'])
            item.setData(Qt.UserRole, p)
            self.list_products.addItem(item)
            
    def show_product_detail(self, item):
        product = item.data(Qt.UserRole)
        bom_details = self.db.get_product_bom_detail(product['product_ID'])
        
        text = f"<h3>{product['product_name']}</h3>"
        text += f"<b>가격:</b> {product['product_price']:,}원<hr>"
        text += "<b>[구성 부품]</b><ul>"
        for bom in bom_details:
            text += f"<li>{bom['part_name']} (x{bom['required_qty']})</li>"
        text += "</ul>"
        self.product_info.setText(text)

    def open_add_product_dialog(self):
        dialog = AddProductDialog(self.db, self)
        if dialog.exec_() == QDialog.Accepted:
            name, price, bom_list = dialog.get_data()
            if self.db.insert_product_with_bom(name, price, bom_list):
                QMessageBox.information(self, "성공", "제품이 성공적으로 등록되었습니다.")
                self.refresh_data()
            else:
                QMessageBox.critical(self, "실패", "등록 중 오류가 발생했습니다.")

    def delete_selected_product(self):
        item = self.list_products.currentItem()
        if not item: return
        product = item.data(Qt.UserRole)
        reply = QMessageBox.question(self, '삭제 확인', f"'{product['product_name']}'을(를) 정말 삭제하시겠습니까?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.db.delete_product(product['product_ID']):
                QMessageBox.information(self, "성공", "삭제되었습니다.")
                self.product_info.setText("")
                self.refresh_data()

    # 탭: 부품
    def setup_parts_tab(self):
        layout = QVBoxLayout()
        self.table_parts = QTableWidget()
        self.table_parts.setColumnCount(3)
        self.table_parts.setHorizontalHeaderLabels(["부품명", "단가", "현재 재고"])
        self.table_parts.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("새 부품 추가")
        btn_del = QPushButton("선택 부품 삭제")
        btn_add.clicked.connect(self.open_add_part_dialog)
        btn_del.clicked.connect(self.delete_selected_part)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_del)
        
        layout.addWidget(self.table_parts)
        layout.addLayout(btn_layout)
        self.tab_parts.setLayout(layout)
        self.load_parts_table()

    def load_parts_table(self):
        parts = self.db.get_all_parts()
        if parts is None: return
        self.table_parts.setRowCount(len(parts))
        for row, part in enumerate(parts):
            name_item = QTableWidgetItem(part['part_name'])
            name_item.setData(Qt.UserRole, part['part_ID']) 
            self.table_parts.setItem(row, 0, name_item)
            self.table_parts.setItem(row, 1, QTableWidgetItem(f"{part['part_price']}원"))
            self.table_parts.setItem(row, 2, QTableWidgetItem(f"{part['stock']}개"))

    def open_add_part_dialog(self):
        dialog = AddPartDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name, price, stock = dialog.get_data()
            if self.db.insert_part(name, price, stock):
                QMessageBox.information(self, "성공", "새 부품이 등록되었습니다.")
                self.refresh_data()

    def delete_selected_part(self):
        row = self.table_parts.currentRow()
        if row < 0: return
        part_id = self.table_parts.item(row, 0).data(Qt.UserRole)
        part_name = self.table_parts.item(row, 0).text()
        
        reply = QMessageBox.question(self, '삭제 확인', f"부품 '{part_name}'을(를) 삭제하시겠습니까?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.db.delete_part(part_id):
                QMessageBox.information(self, "성공", "삭제되었습니다.")
                self.refresh_data()
            else:
                QMessageBox.warning(self, "경고", "BOM에 등록되어 삭제할 수 없습니다.")

    # 탭: 전체 주문내역 
    def setup_orders_tab(self):
        layout = QVBoxLayout()
        self.table_orders = QTableWidget()
        self.table_orders.setColumnCount(5)
        self.table_orders.setHorizontalHeaderLabels(["주문번호", "주문자명", "제품명", "수량", "주문일시"])
        self.table_orders.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_orders.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.table_orders)
        self.tab_orders.setLayout(layout)

    def load_orders_table(self):
        orders = self.db.get_orders()
        if orders is None: return
        self.table_orders.setRowCount(len(orders))
        for row, order in enumerate(orders):
            self.table_orders.setItem(row, 0, QTableWidgetItem(str(order['order_ID'])))
            self.table_orders.setItem(row, 1, QTableWidgetItem(order['user_name']))
            self.table_orders.setItem(row, 2, QTableWidgetItem(order['product_name']))
            self.table_orders.setItem(row, 3, QTableWidgetItem(f"{order.get('orders_qty', 0)}개"))
            self.table_orders.setItem(row, 4, QTableWidgetItem(str(order['order_date'])))

    # 탭: 회원정보 
    def setup_users_tab(self):
        layout = QVBoxLayout()
        self.table_users = QTableWidget()
        self.table_users.setColumnCount(4)
        self.table_users.setHorizontalHeaderLabels(["회원번호", "아이디", "이름", "이메일"])
        self.table_users.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_users.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.table_users)
        self.tab_users.setLayout(layout)

    def load_users_table(self):
        users = self.db.get_all_users()
        if users is None: return
        self.table_users.setRowCount(len(users))
        for row, user in enumerate(users):
            self.table_users.setItem(row, 0, QTableWidgetItem(str(user['user_ID'])))
            self.table_users.setItem(row, 1, QTableWidgetItem(user['login_ID']))
            self.table_users.setItem(row, 2, QTableWidgetItem(user['user_name']))
            self.table_users.setItem(row, 3, QTableWidgetItem(user['email']))

    # 데이터 새로고침
    def refresh_data(self):
        self.load_dashboard_data()
        self.load_restock_list()
        self.load_products_list()
        self.load_parts_table()
        self.load_orders_table()
        self.load_users_table()