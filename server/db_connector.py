import psycopg2

import time


class DBConnector:
    def __init__(self, host="127.0.0.1", database="payroll_db",
                 user="postgres", password="0000", port=5432):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.conn = None
        self.cur = None
        self._connect()

    def _connect(self):
        """Создаёт новое соединение"""
        try:
            # Закрываем старое соединение, если есть
            if self.cur:
                self.cur.close()
            if self.conn:
                self.conn.close()

            # Создаём новое соединение
            self.conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            self.cur = self.conn.cursor()
            print("✅ Подключение к БД установлено")
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            raise

    def reconnect(self):
        """Принудительное переподключение"""
        print("🔄 Переподключение к БД...")
        self._connect()

    def check_connection(self):
        """Проверяет, активно ли соединение"""
        try:
            if self.conn is None or self.cur is None:
                return False
            self.cur.execute("SELECT 1")
            return True
        except:
            return False

    def execute_query(self, query, params=None):
        """Выполняет запрос с автоматическим переподключением"""
        # Проверяем соединение перед запросом
        if not self.check_connection():
            print("⚠️ Соединение потеряно, переподключаемся...")
            self.reconnect()

        try:
            if params:
                self.cur.execute(query, params)
            else:
                self.cur.execute(query)

            if query.strip().lower().startswith("select"):
                return self.cur.fetchall()

            self.conn.commit()
            return None
        except psycopg2.OperationalError as e:
            # Если соединение потерялось во время запроса
            print(f"⚠️ Ошибка соединения: {e}")
            print("🔄 Пробуем переподключиться...")
            self.reconnect()
            # Пробуем ещё раз
            if params:
                self.cur.execute(query, params)
            else:
                self.cur.execute(query)

            if query.strip().lower().startswith("select"):
                return self.cur.fetchall()

            self.conn.commit()
            return None

    def get_cursor(self):
        return self.cur

    def add_employee(self, full_name, position_id, department_id):
        self.execute_query(
            "INSERT INTO Employee (FullName, Position_Id, Department_Id) VALUES (%s, %s, %s)",
            (full_name, position_id, department_id)
        )

    def get_all_employees(self):
        return self.execute_query("""
            SELECT e.Id, e.FullName, p.Name AS Position, d.Name AS Department
            FROM Employee e
            JOIN Positions p ON e.Position_Id = p.Id
            JOIN Department d ON e.Department_Id = d.Id
        """)

    def add_position(self, name, base_salary):
        self.execute_query(
            "INSERT INTO Positions (Name, BaseSalary) VALUES (%s, %s)",
            (name, base_salary)
        )

    def get_all_positions(self):
        """Получить все должности"""
        query = "SELECT Id, Name, BaseSalary FROM positions"
        return self.execute_query(query)

    def add_department(self, name):
        self.execute_query(
            "INSERT INTO Department (Name) VALUES (%s)",
            (name,)
        )

    def get_all_departments(self):
        """Получить все отделы"""
        query = "SELECT Id, Name FROM department"
        return self.execute_query(query)

    def generate_payroll_report(self, period):
        result = self.execute_query(
            "SELECT SUM(NetSalary) FROM Salary WHERE Period = %s",
            (period,)
        )
        if result and result[0][0] is not None:
            return result[0][0]
        return 0.0

    def get_employee_data_by_id(self, employee_id):
        query = """
            SELECT e.Id, e.FullName, p.Name AS Position, d.Name AS Department, p.BaseSalary
            FROM Employee e
            JOIN Positions p ON e.Position_Id = p.Id
            JOIN Department d ON e.Department_Id = d.Id
            WHERE e.Id = %s
        """
        result = self.execute_query(query, (employee_id,))
        if result:
            row = result[0]
            return {
                "id": row[0],
                "full_name": row[1],
                "position": row[2],
                "department": row[3],
                "base_salary": row[4]
            }
        return None

    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()