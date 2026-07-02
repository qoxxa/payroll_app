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
        self.current_employee_id = None
        self.create_main_menu()
        root.geometry("800x570")
        root.minsize(800, 570)  # Минимум 900x600

    def create_main_menu(self):
        # Очистка окна
        for widget in self.root.winfo_children():
            widget.destroy()

        # Кнопки главного меню
        # Поиск по ID
        tk.Label(self.root, text="ID сотрудника:").grid(row=0, column=0, padx=10, pady=15)
        self.employee_id_entry = tk.Entry(self.root)
        self.employee_id_entry.grid(row=0, column=1, padx=10, pady=5)
        tk.Button(self.root, text="Найти по ID", command=self.search_employee).grid(row=0, column=2, padx=1, pady=15)

        # Поиск по фамилии
        tk.Label(self.root, text="ФИО:").grid(row=1, column=0, padx=10, pady=5)
        self.employee_name_entry = tk.Entry(self.root)
        self.employee_name_entry.grid(row=1, column=1, padx=10, pady=5)
        tk.Button(self.root, text="Найти по ФИО", command=self.search_employee_by_name).grid(row=1, column=2,
                                                                                                 padx=1, pady=5)

        tk.Button(self.root, text="Добавить сотрудника", command=self.add_employee_form).grid(row=2, column=0, padx=10,
                                                                                              pady=15)
        tk.Button(self.root, text="Просмотр сотрудников", command=self.view_employees).grid(row=2, column=1, padx=10,
                                                                                            pady=15)
        tk.Button(self.root, text="Добавить должность", command=self.add_position_form).grid(row=3, column=0, padx=10,
                                                                                             pady=15)
        tk.Button(self.root, text="Просмотр должностей", command=self.view_positions).grid(row=3, column=1, padx=10,
                                                                                           pady=15)
        tk.Button(self.root, text="Добавить отдел", command=self.add_department_form).grid(row=4, column=0, padx=10,
                                                                                           pady=15)
        tk.Button(self.root, text="Просмотр отделов", command=self.view_departments).grid(row=4, column=1, padx=10,
                                                                                          pady=15)
        tk.Button(self.root, text="Генерировать отчет", command=self.generate_report).grid(row=13, column=1, padx=10,
                                                                                           pady=15)
        # Кнопка расчета
        tk.Button(self.root, text="Рассчитать", command=self.calculate_salary).grid(row=13, column=0, columnspan=1,
                                                                                    pady=15)
        # Кнопка экспорта в PDF
        tk.Button(self.root, text="Экспорт в PDF", command=self.export_to_pdf).grid(row=14, column=0, columnspan=1,
                                                                                    pady=15)

        # Создаём отдельный Frame для окна вывода (справа от кнопок)
        result_frame = tk.Frame(self.root)
        result_frame.grid(row=0, column=3, rowspan=5, padx=20, pady=10, sticky="n")

        # Поле для отображения результатов поиска
        self.result_text = tk.Text(result_frame, width=45, height=10, wrap="word")
        self.result_text.pack(fill="both", expand=True)
        self.result_text.config(state="disabled")

        # Начисления
        tk.Label(self.root, text="Начисления:").grid(row=6, column=0, padx=10, pady=5)
        self.accrual_entry = tk.Entry(self.root)
        self.accrual_entry.grid(row=7, column=1, padx=10, pady=5)
        self.accrual_type_var = tk.StringVar(self.root)
        self.accrual_type_var.set("Бонус")  # Значение по умолчанию
        accrual_type_menu = ttk.Combobox(self.root, textvariable=self.accrual_type_var,
                                         values=["Бонус", "Премия", "Компенсация"])
        accrual_type_menu.grid(row=6, column=1, padx=10, pady=5)

        # Удержания
        tk.Label(self.root, text="Удержания:").grid(row=8, column=0, padx=10, pady=5)
        self.deduction_entry = tk.Entry(self.root)
        self.deduction_entry.grid(row=9, column=1, padx=10, pady=5)
        self.deduction_type_var = tk.StringVar(self.root)
        self.deduction_type_var.set("Налог")  # Значение по умолчанию
        self.deduction_type_menu = ttk.Combobox(self.root, textvariable=self.deduction_type_var,
                                                values=["Налог", "Штраф", "Вычет"])
        self.deduction_type_menu.grid(row=8, column=1, padx=10, pady=5)

        # Отсутствие
        tk.Label(self.root, text="Отсутствие:").grid(row=10, column=0, padx=10, pady=5)
        self.absence_entry = tk.Entry(self.root)
        self.absence_entry.grid(row=11, column=1, padx=10, pady=5)
        self.absence_type_var = tk.StringVar(self.root)
        self.absence_type_var.set("Отпуск")  # Значение по умолчанию
        self.absence_type_menu = ttk.Combobox(self.root, textvariable=self.absence_type_var,
                                              values=["Отпуск", "Больничный", "Прогул"])
        self.absence_type_menu.grid(row=10, column=1, padx=10, pady=5)

    def search_employee(self):
        """Поиск сотрудника по ID"""
        try:
            employee_id = int(self.employee_id_entry.get())
            response = requests.get(f"{self.api_url}/employee/{employee_id}")

            if response.status_code == 200:
                employee_data = response.json()

                # Сохраняем текущий ID
                self.current_employee_id = employee_id

                # Вывод результата
                self.result_text.config(state="normal")
                self.result_text.delete("1.0", tk.END)
                self.result_text.insert(tk.END,
                                        f"Сотрудник найден:\n"
                                        f"ФИО: {employee_data['full_name']}\n"
                                        f"Должность: {employee_data['position']}\n"
                                        f"Отдел: {employee_data['department']}\n"
                                        f"Оклад: {employee_data['base_salary']} руб."
                                        )
                self.result_text.config(state="disabled")
            else:
                self.result_text.config(state="normal")
                self.result_text.delete("1.0", tk.END)
                self.result_text.insert(tk.END, "Сотрудник с таким ID не найден.")
                self.result_text.config(state="disabled")
                self.current_employee_id = None  # Сбрасываем ID
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректный ID сотрудника!")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к серверу!")

    def search_employee_by_name(self):
        """Поиск сотрудника по ФИО"""
        try:
            name = self.employee_name_entry.get().strip()
            if not name:
                messagebox.showerror("Ошибка", "Введите ФИО для поиска!")
                return

            response = requests.get(f"{self.api_url}/employee/search", params={'name': name})

            if response.status_code == 200:
                employees = response.json()

                if len(employees) == 1:
                    emp = employees[0]
                    # Сохраняем ID найденного сотрудника
                    self.current_employee_id = emp['id']

                    result_msg = (f"Сотрудник найден:\n"
                                  f"ID: {emp['id']}\n"
                                  f"ФИО: {emp['full_name']}\n"
                                  f"Должность: {emp['position']}\n"
                                  f"Отдел: {emp['department']}\n"
                                  f"Оклад: {emp['base_salary']} руб.")
                else:
                    # Если несколько — показываем список, но не сохраняем ID
                    self.current_employee_id = None
                    result_msg = f"Найдено сотрудников: {len(employees)}\n\n"
                    for emp in employees:
                        result_msg += f"ID: {emp['id']}, {emp['full_name']}, {emp['position']}, {emp['department']}\n"

                self.result_text.config(state="normal")
                self.result_text.delete("1.0", tk.END)
                self.result_text.insert(tk.END, result_msg)
                self.result_text.config(state="disabled")
            else:
                self.result_text.config(state="normal")
                self.result_text.delete("1.0", tk.END)
                self.result_text.insert(tk.END, "Сотрудники не найдены.")
                self.result_text.config(state="disabled")
                self.current_employee_id = None
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к серверу!")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def add_employee_form(self):
        """Окно добавления сотрудника с выпадающими списками"""
        try:
            # Загружаем список должностей с сервера
            pos_response = requests.get(f"{self.api_url}/positions")
            if pos_response.status_code != 200:
                messagebox.showerror("Ошибка", "Не удалось загрузить должности")
                return
            positions = pos_response.json()

            # Загружаем список отделов с сервера
            dep_response = requests.get(f"{self.api_url}/departments")
            if dep_response.status_code != 200:
                messagebox.showerror("Ошибка", "Не удалось загрузить отделы")
                return
            departments = dep_response.json()

            # Создаём словари для маппинга {Название: ID}
            positions_dict = {f"{p[1]} (ID: {p[0]})": p[0] for p in positions}
            departments_dict = {f"{d[1]} (ID: {d[0]})": d[0] for d in departments}

            # Открываем окно
            form_window = tk.Toplevel(self.root)
            form_window.title("Добавить сотрудника")

            # ФИО
            tk.Label(form_window, text="ФИО:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
            full_name = tk.Entry(form_window, width=35)
            full_name.grid(row=0, column=1, padx=10, pady=5)

            # Должность (выпадающий список)
            tk.Label(form_window, text="Должность:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
            position_var = tk.StringVar(form_window)
            position_names = list(positions_dict.keys())
            position_menu = ttk.Combobox(form_window, textvariable=position_var,
                                         values=position_names, state="readonly", width=32)
            position_menu.grid(row=1, column=1, padx=10, pady=5)
            if position_names:
                position_menu.current(0)  # Выбираем первый элемент по умолчанию

            # Отдел (выпадающий список)
            tk.Label(form_window, text="Отдел:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
            department_var = tk.StringVar(form_window)
            department_names = list(departments_dict.keys())
            department_menu = ttk.Combobox(form_window, textvariable=department_var,
                                           values=department_names, state="readonly", width=32)
            department_menu.grid(row=2, column=1, padx=10, pady=5)
            if department_names:
                department_menu.current(0)  # Выбираем первый элемент по умолчанию

            def save_employee():
                try:
                    # Получаем ФИО
                    name = full_name.get().strip()
                    if not name:
                        messagebox.showerror("Ошибка", "Введите ФИО сотрудника!")
                        return

                    # Получаем ID выбранной должности и отдела
                    position_id = positions_dict.get(position_var.get())
                    department_id = departments_dict.get(department_var.get())

                    if not position_id or not department_id:
                        messagebox.showerror("Ошибка", "Выберите должность и отдел!")
                        return

                    # Отправляем данные на сервер
                    response = requests.post(f"{self.api_url}/employee", json={
                        'full_name': name,
                        'position_id': position_id,
                        'department_id': department_id
                    })

                    if response.status_code == 201:
                        messagebox.showinfo("Успех", f"Сотрудник '{name}' успешно добавлен!")
                        form_window.destroy()
                    else:
                        error_msg = response.json().get('error', 'Неизвестная ошибка')
                        messagebox.showerror("Ошибка", f"Не удалось добавить: {error_msg}")
                except requests.exceptions.ConnectionError:
                    messagebox.showerror("Ошибка", "Не удалось подключиться к серверу!")
                except Exception as e:
                    messagebox.showerror("Ошибка", str(e))

            # Кнопка "Сохранить"
            tk.Button(form_window, text="Сохранить", command=save_employee,
                       width=15).grid(row=3, column=0, columnspan=2, pady=15)

        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к серверу!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке формы: {str(e)}")

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
                    total = float(report_data['total_salary'])
                    messagebox.showinfo("Отчет", f"Общая зарплата: {total:.2f} руб.")
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
            # Проверяем, найден ли сотрудник
            if self.current_employee_id is None:
                messagebox.showerror("Ошибка", "Сначала найдите сотрудника по ID или ФИО!")
                return

            employee_id = self.current_employee_id

            # Загрузка базового оклада из базы данных через API
            base_salary = self.load_base_salary(employee_id)

            # Преобразование остальных значений в Decimal
            accrual = Decimal(self.accrual_entry.get() or 0)
            deduction = Decimal(self.deduction_entry.get() or 0)
            absence_days = Decimal(self.absence_entry.get() or 0)

            # Расчет дневного оклада
            daily_salary = base_salary / Decimal(30)

            # Расчет чистой зарплаты
            net_salary = base_salary - (daily_salary * absence_days) + accrual - deduction

            # Получение данных сотрудника через API
            response = requests.get(f"{self.api_url}/employee/{employee_id}")
            if response.status_code == 200:
                employee_data = response.json()

                # === НОВОЕ: Сохраняем в базу данных ===
                from datetime import date
                today = date.today().strftime('%Y-%m-%d')  # Формат: 2026-07-02

                save_response = requests.post(f"{self.api_url}/salary", json={
                    'employee_id': employee_id,
                    'period': today,
                    'base_salary': float(base_salary),
                    'deduction': float(deduction),
                    'accrual': float(accrual),
                    'net_salary': float(net_salary)
                })

                if save_response.status_code != 201:
                    messagebox.showwarning("Внимание", "Расчёт выполнен, но не удалось сохранить в БД")

                # Вывод результата
                result_msg = (f"ФИО: {employee_data['full_name']}\n"
                              f"Чистая зарплата: {net_salary:.2f} руб.\n"
                              f"Должность: {employee_data['position']}\n"
                              f"Отдел: {employee_data['department']}\n"
                              f"Базовый оклад: {base_salary:.2f} руб.\n"
                              f"Начисления: {accrual:.2f} руб.\n"
                              f"Удержания: {deduction:.2f} руб.\n"
                              f"Отсутствие: {absence_days} дней\n"
                              f"Период: {today}")

                self.result_text.config(state="normal")
                self.result_text.delete("1.0", tk.END)
                self.result_text.insert(tk.END, result_msg)
                self.result_text.config(state="disabled")

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
                    "Период": today,
                }
            else:
                self.result_text.config(state="normal")
                self.result_text.delete("1.0", tk.END)
                self.result_text.insert(tk.END, "Не удалось получить данные сотрудника")
                self.result_text.config(state="disabled")

        except ValueError as e:
            self.result_text.config(state="normal")
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, f"Ошибка: {str(e)}")
            self.result_text.config(state="disabled")
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