import psycopg2


class DBConnector:
    def __init__(self, host="127.0.0.1", database="payroll_db",
                 user="postgres", password="0000", port=5432):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

    def get_connection(self):
        """Создаёт НОВОЕ соединение каждый раз"""
        return psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password,
            port=self.port
        )

    def execute_query(self, query, params=None):
        """Создаёт новое соединение для каждого запроса"""
        conn = None
        cur = None
        try:
            # Создаём НОВОЕ соединение
            conn = self.get_connection()
            cur = conn.cursor()

            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)

            if query.strip().lower().startswith("select"):
                result = cur.fetchall()
                cur.close()
                conn.close()
                return result

            conn.commit()
            cur.close()
            conn.close()
            return None

        except Exception as e:
            print(f"❌ Ошибка SQL: {e}")
            if cur:
                cur.close()
            if conn:
                conn.close()
            raise

    # ============ СОТРУДНИКИ ============

    def get_employee_data_by_id(self, employee_id):
        """Получить данные сотрудника по ID"""
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

    def search_employee_by_name(self, name):
        """Поиск сотрудника по фамилии (частичное совпадение, нечувствительно к регистру)"""
        query = """
            SELECT e.Id, e.FullName, p.Name AS Position, d.Name AS Department, p.BaseSalary
            FROM Employee e
            JOIN Positions p ON e.Position_Id = p.Id
            JOIN Department d ON e.Department_Id = d.Id
            WHERE e.FullName ILIKE %s
            ORDER BY e.Id
        """
        # Добавляем % для поиска по частичному совпадению
        search_pattern = f"%{name}%"
        return self.execute_query(query, (search_pattern,))

    def get_all_employees(self):
        """Получить всех сотрудников"""
        return self.execute_query("""
            SELECT e.Id, e.FullName, p.Name AS Position, d.Name AS Department
            FROM Employee e
            JOIN Positions p ON e.Position_Id = p.Id
            JOIN Department d ON e.Department_Id = d.Id
            ORDER BY e.Id
        """)

    def add_employee(self, full_name, position_id, department_id):
        """Добавить нового сотрудника"""
        self.execute_query(
            "INSERT INTO Employee (FullName, Position_Id, Department_Id) VALUES (%s, %s, %s)",
            (full_name, position_id, department_id)
        )

    # ============ ДОЛЖНОСТИ ============

    def get_all_positions(self):
        """Получить все должности"""
        return self.execute_query("SELECT Id, Name, BaseSalary FROM Positions ORDER BY Id")

    def add_position(self, name, base_salary):
        """Добавить должность"""
        self.execute_query(
            "INSERT INTO Positions (Name, BaseSalary) VALUES (%s, %s)",
            (name, base_salary)
        )

    # ============ ОТДЕЛЫ ============

    def get_all_departments(self):
        """Получить все отделы"""
        return self.execute_query("SELECT Id, Name FROM Department ORDER BY Id")

    def add_department(self, name):
        """Добавить отдел"""
        self.execute_query(
            "INSERT INTO Department (Name) VALUES (%s)",
            (name,)
        )

    # ============ ОТЧЁТЫ ============

    def generate_payroll_report(self, period):
        """Сгенерировать отчет по периоду"""
        result = self.execute_query(
            "SELECT SUM(NetSalary) FROM Salary WHERE Period = %s",
            (period,)
        )
        if result and result[0][0] is not None:
            return result[0][0]
        return 0.0

    # ============ ЗАКРЫТИЕ ============

    def close(self):
        """Заглушка, так как соединения создаются и закрываются в execute_query"""
        pass