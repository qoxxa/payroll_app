from flask import Flask, jsonify, request
from flask_cors import CORS
from db_connector import DBConnector
from business_logic import PayrollCalculator

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для локальной разработки

# Инициализируем подключение к БД
db = DBConnector()
calculator = PayrollCalculator

# ============ API для сотрудников ============

@app.route('/api/employee/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    """Получить данные сотрудника по ID"""
    try:
        employee_data = db.get_employee_data_by_id(employee_id)
        if employee_data:
            return jsonify(employee_data), 200
        else:
            return jsonify({'error': 'Сотрудник не найден'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/employee/search', methods=['GET'])
def search_employee_by_name():
    """Поиск сотрудника по фамилии"""
    try:
        name = request.args.get('name', '').strip()
        if not name:
            return jsonify({'error': 'Введите фамилию для поиска'}), 400

        employees = db.search_employee_by_name(name)

        if not employees:
            return jsonify({'error': 'Сотрудники не найдены'}), 404

        # Форматируем результат
        result = []
        for emp in employees:
            result.append({
                'id': emp[0],
                'full_name': emp[1],
                'position': emp[2],
                'department': emp[3],
                'base_salary': emp[4]
            })

        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/employees', methods=['GET'])
def get_all_employees():
    """Получить всех сотрудников"""
    try:
        employees = db.get_all_employees()
        return jsonify(employees), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/employee', methods=['POST'])
def add_employee():
    """Добавить нового сотрудника"""
    try:
        data = request.json
        db.add_employee(
            full_name=data['full_name'],
            position_id=int(data['position_id']),
            department_id=int(data['department_id'])
        )
        return jsonify({'message': 'Сотрудник добавлен'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ API для должностей ============

@app.route('/api/positions', methods=['GET'])
def get_positions():
    """Получить все должности"""
    try:
        # Добавь этот метод в db_connector.py если нет
        positions = db.get_all_positions()
        return jsonify(positions), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/position', methods=['POST'])
def add_position():
    """Добавить должность"""
    try:
        data = request.json
        db.add_position(
            name=data['name'],
            base_salary=float(data['base_salary'])
        )
        return jsonify({'message': 'Должность добавлена'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ API для отделов ============

@app.route('/api/departments', methods=['GET'])
def get_departments():
    """Получить все отделы"""
    try:
        # Добавь этот метод в db_connector.py если нет
        departments = db.get_all_departments()
        return jsonify(departments), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/department', methods=['POST'])
def add_department():
    """Добавить отдел"""
    try:
        data = request.json
        db.add_department(name=data['name'])
        return jsonify({'message': 'Отдел добавлен'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ API для расчета зарплаты ============

@app.route('/api/calculate', methods=['POST'])
@app.route('/api/calculate', methods=['POST'])
def calculate():
    """Рассчитать зарплату"""
    try:
        data = request.json
        employee_id = int(data['employee_id'])
        worked_hours = float(data.get('worked_hours', 160))

        result = calculator.calculate_salary(employee_id, worked_hours)
        return jsonify({'total_salary': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ API для отчетов ============

@app.route('/api/report', methods=['GET'])
def generate_report():
    """Сгенерировать отчет"""
    try:
        period = request.args.get('period')
        report = db.generate_payroll_report(period)
        return jsonify({'total_salary': report}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, host='127.0.0.1', port=5000)