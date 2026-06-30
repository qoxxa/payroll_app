class PayrollCalculator:
    def __init__(self, db_connector):
        self.db = db_connector

    def calculate_salary(self, employee_id, worked_hours):
        query = "SELECT BaseSalary FROM Employees WHERE Id = %s"
        result = self.db.execute_query(query, (employee_id,))
        if not result:
            raise ValueError(f"Сотрудник с ID {employee_id} не найден.")
        base_salary = result[0][0]

        hourly_rate = base_salary / 160
        total_salary = hourly_rate * worked_hours

        query = "SELECT SUM(Amount) FROM Accruals WHERE EmployeeId = %s"
        accruals = self.db.execute_query(query, (employee_id,))[0][0] or 0

        query = "SELECT SUM(Amount) FROM Deductions WHERE EmployeeId = %s"
        deductions = self.db.execute_query(query, (employee_id,))[0][0] or 0

        total_salary += accruals - deductions
        return total_salary
