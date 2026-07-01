import psycopg2

class DBConnector:
    def __init__(self, host="localhost", database="payroll_db", user="postgres", password="0000"):
        try:
            self.conn = psycopg2.connect(
                host=host,
                database=database,
                user=user,
                password=password
            )
            self.cur = self.conn.cursor()
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            raise

    def execute_query(self, query, params=None):
        try:
            self.cur.execute(query, params)
            if query.strip().lower().startswith("select"):
                return self.cur.fetchall()
            self.conn.commit()
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            self.conn.rollback()
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