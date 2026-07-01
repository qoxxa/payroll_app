import tkinter as tk
import requests
from tkinter import ttk, messagebox, filedialog
from fpdf import FPDF
from decimal import Decimal

API_URL = "http://127.0.0.1:5000/api"


class PDF(FPDF):
    def __init__(self):
        super().__init__()
        # Добавляем шрифт DejaVuSans с поддержкой кириллицы
        self.add_font("DejaVuSans", "", "DejaVuSans.ttf", uni=True)
        self.set_font("DejaVuSans", size=12)

    def header(self):
        # Заголовок документа
        self.cell(0, 10, "Расчет заработной платы", ln=True, align="C")
        self.ln(10)

    def footer(self):
        # Нижний колонтитул
        self.set_y(-15)
        self.cell(0, 10, f"Страница {self.page_no()}", align="C")


class PayrollAppUI:
    def __init__(self, root):
        # Инициализация основных переменных и элементов интерфейса
        self.root = root
        self.root.title("Система расчета заработной платы")
        self.api_url = API_URL
        self.create_main_menu()
        root.geometry("700x650")

    def create_main_menu(self):
        # Очистка окна
        for widget in self.root.winfo_children():
            widget.destroy()

        # Кнопки главного меню
        tk.Label(self.root, text="ID сотрудника:").grid(row=0, column=0, padx=10, pady=80)
        self.employee_id_entry = tk.Entry(self.root)
        self.employee_id_entry.grid(row=0, column=1, padx=10, pady=5)
        tk.Button(self.root, text="Найти", command=self.search_employee).grid(row=0, column=2, padx=1, pady=10)
        tk.Button(self.root, text="Добавить сотрудника", command=self.add_employee_form).grid(row=1, column=0, padx=10,
                                                                                              pady=5)
        tk.Button(self.root, text="Просмотр сотрудников", command=self.view_employees).grid(row=1, column=1, padx=10,
                                                                                            pady=5)
        tk.Button(self.root, text="Добавить должность", command=self.add_position_form).grid(row=2, column=0, padx=10,
                                                                                             pady=5)
        tk.Button(self.root, text="Просмотр должностей", command=self.view_positions).grid(row=2, column=1, padx=10,
                                                                                            pady=5)
        tk.Button(self.root, text="Добавить отдел", command=self.add_department_form).grid(row=3, column=0, padx=10,
                                                                                           pady=5)
        tk.Button(self.root, text="Просмотр отделов", command=self.view_departments).grid(row=3, column=1, padx=10,
                                                                                           pady=5)
        tk.Button(self.root, text="Генерировать отчет", command=self.generate_report).grid(row=13, column=1, padx=10,
                                                                                           pady=5)

        # Поле для отображения результатов поиска
        self.result_label = tk.Label(self.root, text="", wraplength=400)
        self.result_label.grid(row=0, column=3, padx=50, pady=10)

        # Начисления
        tk.Label(self.root, text="Начисления:").grid(row=6, column=0, padx=10, pady=5)
        self.accrual_entry = tk.Entry(self.root)
        self.accrual_entry.grid(row=6, column=1, padx=10, pady=5)
        self.accrual_type_var = tk.StringVar(self.root)
        self.accrual_type_var.set("Зарплата")  # Значение по умолчанию
        accrual_type_menu = ttk.Combobox(self.root, textvariable=self.accrual_type_var,
                                         values=["Зарплата", "Премия", "Компенсация"])
        accrual_type_menu.grid(row=7, column=1, padx=10, pady=5)

        # Удержания
        tk.Label(self.root, text="Удержания:").grid(row=8, column=0, padx=10, pady=5)
        self.deduction_entry = tk.Entry(self.root)
        self.deduction_entry.grid(row=8, column=1, padx=10, pady=5)
        self.deduction_type_var = tk.StringVar(self.root)
        self.deduction_type_var.set("Налог")  # Значение по умолчанию
        self.deduction_type_menu = ttk.Combobox(self.root, textvariable=self.deduction_type_var,
                                                values=["Налог", "Штраф", "Вычет"])
        self.deduction_type_menu.grid(row=9, column=1, padx=10, pady=5)

        # Отсутствие
        tk.Label(self.root, text="Отсутствие:").grid(row=10, column=0, padx=10, pady=5)
        self.absence_entry = tk.Entry(self.root)
        self.absence_entry.grid(row=10, column=1, padx=10, pady=5)
        self.absence_type_var = tk.StringVar(self.root)
        self.absence_type_var.set("Отпуск")  # Значение по умолчанию
        self.absence_type_menu = ttk.Combobox(self.root, textvariable=self.absence_type_var,
                                              values=["Отпуск", "Больничный", "Прогул"])
        self.absence_type_menu.grid(row=11, column=1, padx=10, pady=5)

        # Кнопка расчета
        tk.Button(self.root, text="Рассчитать", command=self.calculate_salary).grid(row=13, column=0, columnspan=1,
                                                                                    pady=7)
        # Кнопка экспорта в PDF
        tk.Button(self.root, text="Экспорт в PDF", command=self.export_to_pdf).grid(row=14, column=0, columnspan=1,
                                                                                    pady=15)

    def search_employee(self):
        """Поиск сотрудника по ID"""
        try:
            employee_id = int(self.employee_id_entry.get())
            response = requests.get(f"{self.api_url}/employee/{employee_id}")

            if response.status_code == 200:
                employee_data = response.json()
                self.result_label.config(
                    text=f"Сотрудник найден:\n"
                         f"ФИО: {employee_data['full_name']}\n"
                         f"Должность: {employee_data['position']}\n"
                         f"Отдел: {employee_data['department']}\n"
                         f"Оклад: {employee_data['base_salary']} руб."
                )
            else:
                self.result_label.config(text="Сотрудник с таким ID не найден.")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректный ID сотрудника!")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к серверу!")

    def add_employee_form(self):
        """Окно добавления сотрудника"""
        form_window = tk.Toplevel(self.root)
        form_window.title("Добавить сотрудника")
        tk.Label(form_window, text="ФИО:").grid(row=0, column=0, padx=10, pady=5)
        full_name = tk.Entry(form_window)
        full_name.grid(row=0, column=1, padx=10, pady=5)
        tk.Label(form_window, text="Должность (ID):").grid(row=1, column=0, padx=10, pady=5)
        position_id = tk.Entry(form_window)
        position_id.grid(row=1, column=1, padx=10, pady=5)
        tk.Label(form_window, text="Отдел (ID):").grid(row=2, column=0, padx=10, pady=5)
        department_id = tk.Entry(form_window)
        department_id.grid(row=2, column=1, padx=10, pady=5)

        def save_employee():
            try:
                response = requests.post(f"{self.api_url}/employee", json={
                    'full_name': full_name.get(),
                    'position_id': int(position_id.get()),
                    'department_id': int(department_id.get())
                })

                if response.status_code == 201:
                    messagebox.showinfo("Успех", "Сотрудник добавлен!")
                    form_window.destroy()
                else:
                    messagebox.showerror("Ошибка", response.json().get('error', 'Неизвестная ошибка'))
            except requests.exceptions.ConnectionError:
                messagebox.showerror("Ошибка", "Не удалось подключиться к серверу!")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        tk.Button(form_window, text="Сохранить", command=save_employee).grid(row=3, column=0, columnspan=2, pady=10)

    def view_employees(self):
        """Окно просмотра сотрудников"""
        try:
            response = requests.get(f"{self.api_url}/employees")

            if response.status_code == 200:
                employees = response.json()
                if not employees:
                    messagebox.showinfo("Информация", "Сотрудники не найдены.")
                    return

                form_window = tk.Toplevel(self.root)
                form_window.title("Список сотрудников")
                tree = ttk.Treeview(form_window, columns=("ID", "ФИО", "Должность", "Отдел"), show="headings")
                tree.heading("ID", text="ID")
                tree.heading("ФИО", text="ФИО")
                tree.heading("Должность", text="Должность")
                tree.heading("Отдел", text="Отдел")
                tree.pack(padx=10, pady=10)

                for employee in employees:
                    tree.insert("", "end", values=employee)
            else:
                messagebox.showerror("Ошибка", "Не удалось получить список сотрудников")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к серверу!")

    def add_position_form(self):
        """Окно добавления должности"""
        form_window = tk.Toplevel(self.root)
        form_window.title("Добавить должность")
        tk.Label(form_window, text="Название:").grid(row=0, column=0, padx=10, pady=5)
        name = tk.Entry(form_window)
        name.grid(row=0, column=1, padx=10, pady=5)
        tk.Label(form_window, text="Базовая зарплата:").grid(row=1, column=0, padx=10, pady=5)
        base_salary = tk.Entry(form_window)
        base_salary.grid(row=1, column=1, padx=10, pady=5)

        def save_position():
            try:
                response = requests.post(f"{self.api_url}/position", json={
                    'name': name.get(),
                    'base_salary': float(base_salary.get())
                })

                if response.status_code == 201:
                    messagebox.showinfo("Успех", "Должность добавлена!")
                    form_window.destroy()
                else:
                    messagebox.showerror("Ошибка", response.json().get('error', 'Неизвестная ошибка'))
            except requests.exceptions.ConnectionError:
                messagebox.showerror("Ошибка", "Не удалось подключиться к серверу!")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        tk.Button(form_window, text="Сохранить", command=save_position).grid(row=2, column=0, columnspan=2, pady=10)

    def add_department_form(self):
        """Окно добавления отдела"""
        form_window = tk.Toplevel(self.root)
        form_window.title("Добавить отдел")
        tk.Label(form_window, text="Название:").grid(row=0, column=0, padx=10, pady=5)
        name = tk.Entry(form_window)
        name.grid(row=0, column=1, padx=10, pady=5)

        def save_department():
            try:
                response = requests.post(f"{self.api_url}/department", json={
                    'name': name.get()
                })

                if response.status_code == 201:
                    messagebox.showinfo("Успех", "Отдел добавлен!")
                    form_window.destroy()
                else:
                    messagebox.showerror("Ошибка", response.json().get('error', 'Неизвестная ошибка'))
            except requests.exceptions.ConnectionError:
                messagebox.showerror("Ошибка", "Не удалось подключиться к серверу!")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        tk.Button(form_window, text="Сохранить", command=save_department).grid(row=1, column=0, columnspan=2, pady=10)

    def view_departments(self):
        """Окно просмотра отделов"""
        try:
            response = requests.get(f"{self.api_url}/departments")

            if response.status_code == 200:
                departments = response.json()
                if not departments:
                    messagebox.showinfo("Информация", "Отделы не найдены.")
                    return

                form_window = tk.Toplevel(self.root)
                form_window.title("Список отделов")
                tree = ttk.Treeview(form_window, columns=("ID", "Название"), show="headings")
                tree.heading("ID", text="ID")
                tree.heading("Название", text="Название отдела")
                tree.pack(padx=10, pady=10)

                for department in departments:
                    tree.insert("", "end", values=department)
            else:
                messagebox.showerror("Ошибка", "Не удалось получить список отделов")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к серверу!")

    def view_positions(self):
        """Окно просмотра должностей"""
        try:
            response = requests.get(f"{self.api_url}/positions")

            if response.status_code == 200:
                positions = response.json()
                if not positions:
                    messagebox.showinfo("Информация", "Должности не найдены.")
                    return

                form_window = tk.Toplevel(self.root)
                form_window.title("Список должностей")
                tree = ttk.Treeview(form_window, columns=("ID", "Название", "Оклад"), show="headings")
                tree.heading("ID", text="ID")
                tree.heading("Название", text="Название")
                tree.heading("Оклад", text="Оклад (руб.)")
                tree.pack(padx=10, pady=10)

                for position in positions:
                    tree.insert("", "end", values=position)
            else:
                messagebox.showerror("Ошибка", "Не удалось получить список должностей")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к серверу!")

    def generate_report(self):
        """Окно генерации отчета"""
        form_window = tk.Toplevel(self.root)
        form_window.title("Генерация отчета")
        tk.Label(form_window, text="Период (YYYY-MM-DD):").grid(row=0, column=0, padx=10, pady=5)
        period = tk.Entry(form_window)
        period.grid(row=0, column=1, padx=10, pady=5)

        def generate():
            try:
                response = requests.get(f"{self.api_url}/report", params={'period': period.get()})

                if response.status_code == 200:
                    report_data = response.json()
                    messagebox.showinfo("Отчет", f"Общая зарплата: {report_data['total_salary']:.2f} руб.")
                else:
                    messagebox.showerror("Ошибка", response.json().get('error', 'Неизвестная ошибка'))
            except requests.exceptions.ConnectionError:
                messagebox.showerror("Ошибка", "Не удалось подключиться к серверу!")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        tk.Button(form_window, text="Сформировать", command=generate).grid(row=1, column=0, columnspan=2, pady=10)

    def calculate_salary(self):
        """Расчет заработной платы с учетом начислений, удержаний и отсутствия."""
        try:
            # Получение ID сотрудника
            employee_id = int(self.employee_id_entry.get())

            # Загрузка базового оклада из базы данных через API
            base_salary = self.load_base_salary(employee_id)

            # Преобразование остальных значений в Decimal
            accrual = Decimal(self.accrual_entry.get() or 0)  # Начисления (по умолчанию 0)
            deduction = Decimal(self.deduction_entry.get() or 0)  # Удержания (по умолчанию 0)
            absence_days = Decimal(self.absence_entry.get() or 0)  # Дни отсутствия (по умолчанию 0)

            # Расчет дневного оклада
            daily_salary = base_salary / Decimal(30)

            # Расчет чистой зарплаты
            net_salary = base_salary - (daily_salary * absence_days) + accrual - deduction

            # Получение данных сотрудника через API
            response = requests.get(f"{self.api_url}/employee/{employee_id}")
            if response.status_code == 200:
                employee_data = response.json()

                self.result_label.config(
                    text=f"ФИО: {employee_data['full_name']}\n"
                         f"Чистая зарплата: {net_salary:.2f} руб.\n"
                         f"Должность: {employee_data['position']}\n"
                         f"Отдел: {employee_data['department']}\n"
                         f"Базовый оклад: {base_salary:.2f} руб.\n"
                         f"Начисления: {accrual:.2f} руб.\n"
                         f"Удержания: {deduction:.2f} руб.\n"
                         f"Отсутствие: {absence_days} дней"
                )

                # Сохраняем данные для экспорта в PDF
                self.pdf_data = {
                    "ФИО": employee_data['full_name'],
                    "Чистая зарплата": net_salary,
                    "Должность": employee_data['position'],
                    "Отдел": employee_data['department'],
                    "Базовый оклад": base_salary,
                    "Начисления": accrual,
                    "Удержания": deduction,
                    "Отсутствие": absence_days,
                }
            else:
                messagebox.showerror("Ошибка", "Не удалось получить данные сотрудника")

        except ValueError as e:
            self.result_label.config(text=f"Ошибка: {str(e)}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к серверу!")

    def export_to_pdf(self):
        """Экспорт данных расчета в PDF с выбором папки."""
        if not hasattr(self, 'pdf_data'):
            messagebox.showerror("Ошибка", "Нет данных для экспорта. Сначала выполните расчет.")
            return

        # Выбор папки для сохранения
        folder_selected = filedialog.askdirectory(title="Выберите папку для сохранения")
        if not folder_selected:
            messagebox.showinfo("Отмена", "Экспорт отменен.")
            return

        # Создаем PDF-документ
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_font("DejaVuSans", "", "DejaVuSans.ttf", uni=True)
        pdf.set_font("DejaVuSans", size=12)

        # Добавляем заголовок
        pdf.cell(200, 10, txt="Расчет заработной платы", ln=True, align="C")
        pdf.ln(10)

        for key, value in self.pdf_data.items():
            if isinstance(value, Decimal):
                pdf.cell(200, 10, txt=f"{key}: {value:.2f}", ln=True)
            else:
                pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)

        # Формируем путь к файлу
        file_path = f"{folder_selected}/salary_calculation.pdf"

        # Сохраняем файл
        try:
            pdf.output(file_path)
            messagebox.showinfo("Успех", f"Расчет успешно экспортирован в файл:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать PDF: {str(e)}")

    def load_base_salary(self, employee_id):
        """
        Загрузка базового оклада через API по ID сотрудника.
        """
        try:
            response = requests.get(f"{self.api_url}/employee/{employee_id}")
            if response.status_code == 200:
                employee_data = response.json()
                return Decimal(employee_data['base_salary'])
            else:
                raise ValueError("Сотрудник с таким ID не найден.")
        except requests.exceptions.ConnectionError:
            raise ValueError("Не удалось подключиться к серверу!")
        except Exception as e:
            raise ValueError(f"Ошибка при загрузке базового оклада: {str(e)}")