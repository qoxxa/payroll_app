import sys
import os

# Добавляем родительскую папку в путь поиска модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from db_connector import DBConnector
from business_logic import PayrollCalculator

app = Flask(__name__)

db_connector = DBConnector()  # Параметры по умолчанию уже прописаны
payroll_calculator = PayrollCalculator(db_connector)

@app.route('/calculate_salary', methods=['POST'])
def calculate_salary():
    data = request.json
    employee_id = data['employee_id']
    worked_hours = data['worked_hours']

    total_salary = payroll_calculator.calculate_salary(employee_id, worked_hours)
    return jsonify({"total_salary": total_salary})

if __name__ == "__main__":
    app.run(debug=True)