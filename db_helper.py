import pymysql

# 데이터베이스 연결
DB_CONFIG = dict(
    host="localhost",
    user="root",
    password="Azsx06^06^", 
    database="inventory_db",
    charset="utf8"
)

class DBHelper:
    def __init__(self,**config):
        self.config = config

    def connect(self):
        config_with_dict = self.config.copy()
        config_with_dict['cursorclass'] = pymysql.cursors.DictCursor
        return pymysql.connect(**config_with_dict)

    #로그인 검증
    def login_user(self, login_id, password):
        sql = "SELECT user_ID, user_name, role FROM users WHERE login_ID=%s AND password=%s"
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (login_id, password))
                return cur.fetchone()

    #회원가입
    def register_user(self, login_id, password, user_name, email):
        sql = "INSERT INTO users (login_ID, password, user_name, email) VALUES (%s, %s, %s, %s)"
        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (login_id, password, user_name, email))
                conn.commit()
                return True
            except pymysql.err.IntegrityError:
                print("이미 존재하는 아이디입니다.")
                conn.rollback()
                return False
            except Exception as e:
                print(f"회원가입 에러: {e}")
                conn.rollback()
                return False

    # user의 상품 구매 리스트 및 root의 재고주문 리스트
    def get_all_products(self):
        sql = "SELECT product_ID, product_name, product_price FROM products"
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                return cur.fetchall()

    # root의 메인 화면 재고 현황
    def get_all_parts(self):
        sql = "SELECT part_ID, part_name, stock, part_price FROM parts"
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                return cur.fetchall()

    # 회원정보 출력
    def get_all_users(self):
        sql = "SELECT user_ID, login_ID, user_name, email FROM users WHERE role = 'user'"
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                return cur.fetchall()

    # user ID가 주어진 경우 user의 정보면 WHERE로 추가하여 제공
    def get_orders(self, user_id=None):
        sql = """
            SELECT o.order_ID, u.user_name, p.product_name, o.orders_qty, o.order_date
            FROM orders o
            JOIN users u ON o.user_ID = u.user_ID
            JOIN products p ON o.product_ID = p.product_ID
        """
        with self.connect() as conn:
            with conn.cursor() as cur:
                if user_id:
                    sql += " WHERE o.user_ID = %s ORDER BY o.order_date DESC"
                    cur.execute(sql, (user_id,))
                else:
                    sql += " ORDER BY o.order_date DESC"
                    cur.execute(sql)
                return cur.fetchall()

    def add_part_stock(self, part_id, add_qty):
        sql = "UPDATE parts SET stock = stock + %s WHERE part_ID = %s"
        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (add_qty, part_id))
                conn.commit()
                return True
            except Exception as e:
                print(f"재고 업데이트 에러: {e}")
                conn.rollback()
                return False

    def insert_part(self, part_name, part_price, stock):
        sql = "INSERT INTO parts (part_name, part_price, stock) VALUES (%s, %s, %s)"
        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (part_name, part_price, stock))
                conn.commit()
                return True
            except Exception as e:
                print(f"부품 등록 에러: {e}")
                conn.rollback()
                return False

    def insert_product_with_bom(self, product_name, product_price, bom_list):
        insert_prod_sql = "INSERT INTO products (product_name, product_price) VALUES (%s, %s)"
        insert_bom_sql = "INSERT INTO product_boms (product_ID, part_ID, required_qty) VALUES (%s, %s, %s)"

        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(insert_prod_sql, (product_name, product_price))

                    new_product_id = cur.lastrowid

                    for bom in bom_list:
                        cur.execute(insert_bom_sql, (new_product_id, bom['part_id'], bom['qty']))

                # 모두 성공했을 때만 DB에 최종 저장!
                conn.commit()
                return True

            except Exception as e:
                print(f"완제품 및 BOM 등록 에러 (롤백 처리됨): {e}")
                conn.rollback() # 중간에 에러 나면 제품 등록도 취소!
                return False

    def delete_product(self, product_id):
        delete_bom_sql = "DELETE FROM product_boms WHERE product_ID = %s"
        delete_prod_sql = "DELETE FROM products WHERE product_ID = %s"
        
        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(delete_bom_sql, (product_id,)) # FK 에러 방지 선삭제
                    cur.execute(delete_prod_sql, (product_id,))
                conn.commit()
                return True
            except Exception as e:
                print(f"제품 삭제 에러: {e}")
                conn.rollback()
                return False

    def delete_part(self, part_id):
        sql = "DELETE FROM parts WHERE part_ID = %s"
        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (part_id,))
                conn.commit()
                return True
            except pymysql.err.IntegrityError:
                print("BOM에 등록되어 삭제할 수 없습니다.")
                return False
            except Exception as e:
                print(f"부품 삭제 에러: {e}")
                conn.rollback()
                return False

    def get_product_bom_detail(self, product_id):
        sql = """
            SELECT pt.part_name, b.required_qty, pt.stock
            FROM product_boms b
            JOIN parts pt ON b.part_ID = pt.part_ID
            WHERE b.product_ID = %s
        """
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (product_id,))
                return cur.fetchall()

    def place_order(self, user_id, product_id, order_qty):
        insert_order_sql = "INSERT INTO orders (user_ID, product_ID, orders_qty) VALUES (%s, %s, %s)"
        get_bom_sql = "SELECT part_ID, required_qty FROM product_boms WHERE product_ID = %s"
        update_stock_sql = "UPDATE parts SET stock = stock - %s WHERE part_ID = %s"

        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(insert_order_sql, (user_id, product_id, order_qty))
                    cur.execute(get_bom_sql, (product_id,))
                    bom_list = cur.fetchall()
                    
                    for bom in bom_list:
                        total_deduct = order_qty * bom['required_qty']
                        cur.execute(update_stock_sql, (total_deduct, bom['part_ID']))
                
                conn.commit()
                return True
            except Exception as e:
                print(f"주문 처리 중 에러 발생 (롤백됨): {e}")
                conn.rollback()
                return False