-- 1. Создание таблицы Position (Должность)
CREATE TABLE Positions (
    Id SERIAL PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    BaseSalary DECIMAL(10, 2) NOT NULL
);

-- 2. Создание таблицы Department (Отдел)
CREATE TABLE Department (
    Id SERIAL PRIMARY KEY,
    Name VARCHAR(255) NOT NULL
);

-- 3. Создание таблицы Employee (Сотрудник)
-- Ссылки на таблицы Position и Department
CREATE TABLE Employee (
    Id SERIAL PRIMARY KEY,
    FullName VARCHAR(255) NOT NULL,
    Position_Id INT NOT NULL,
    Department_Id INT NOT NULL,
    FOREIGN KEY (Position_Id) REFERENCES Position(Id),
    FOREIGN KEY (Department_Id) REFERENCES Department(Id)
);

-- 4. Создание таблицы WorkSchedule (График работы)
-- Ссылка на таблицу Employee
CREATE TABLE WorkSchedule (
    Id SERIAL PRIMARY KEY,
    Employee_Id INT NOT NULL,
    WorkDate DATE NOT NULL,
    HoursWorked INT NOT NULL,
    FOREIGN KEY (Employee_Id) REFERENCES Employee(Id)
);

-- 5. Создание таблицы AccrualType (Тип начисления)
CREATE TABLE AccrualType (
    Id SERIAL PRIMARY KEY,
    Name VARCHAR(255) NOT NULL
);

-- 6. Создание таблицы Accrual (Начисления)
-- Ссылка на таблицу AccrualType
CREATE TABLE Accrual (
    Id SERIAL PRIMARY KEY,
    AccrualType_Id INT NOT NULL,
    Amount DECIMAL(10, 2) NOT NULL,
    Conditions TEXT,
    FOREIGN KEY (AccrualType_Id) REFERENCES AccrualType(Id)
);

-- 7. Создание таблицы DeductionType (Тип удержания)
CREATE TABLE DeductionType (
    Id SERIAL PRIMARY KEY,
    Name VARCHAR(255) NOT NULL
);

-- 8. Создание таблицы Deduction (Удержания)
-- Ссылка на таблицу DeductionType
CREATE TABLE Deduction (
    Id SERIAL PRIMARY KEY,
    DeductionType_Id INT NOT NULL,
    Amount DECIMAL(10, 2) NOT NULL,
    Reason TEXT,
    FOREIGN KEY (DeductionType_Id) REFERENCES DeductionType(Id)
);

-- 9. Создание таблицы Salary (Зарплата)
-- Ссылка на таблицу Employee
CREATE TABLE Salary (
    Id SERIAL PRIMARY KEY,
    Employee_Id INT NOT NULL,
    Period DATE NOT NULL,
    BaseAmount DECIMAL(10, 2) NOT NULL,
    Deduction DECIMAL(10, 2) NOT NULL,
	Accrual DECIMAL(10, 2) NOT NULL,
    NetSalary DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (Employee_Id) REFERENCES Employee(Id)
);

-- 10. Создание таблицы PayrollReport (Отчет об оплате труда)
-- Ссылка на таблицу Salary
CREATE TABLE PayrollReport (
    Id SERIAL PRIMARY KEY,
    Period DATE NOT NULL,
    TotalDeduction DECIMAL(15, 2),
    TotalAccrual DECIMAL(15, 2),
    TotalSalary DECIMAL(15, 2), -- Добавлено поле для общей суммы зарплаты
    Salary_Id INT NOT NULL,
    FOREIGN KEY (Salary_Id) REFERENCES Salary(Id)
);

-- 11. Создание промежуточной таблицы Salary_Accrual (Связь между зарплатой и начислениями)
CREATE TABLE Salary_Accrual (
    Salary_Id INT NOT NULL,
    Accrual_Id INT NOT NULL,
    Amount DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (Salary_Id, Accrual_Id),
    FOREIGN KEY (Salary_Id) REFERENCES Salary(Id),
    FOREIGN KEY (Accrual_Id) REFERENCES Accrual(Id)
);

-- 12. Создание промежуточной таблицы Salary_Deduction (Связь между зарплатой и удержаниями)
CREATE TABLE Salary_Deduction (
    Salary_Id INT NOT NULL,
    Deduction_Id INT NOT NULL,
    Amount DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (Salary_Id, Deduction_Id),
    FOREIGN KEY (Salary_Id) REFERENCES Salary(Id),
    FOREIGN KEY (Deduction_Id) REFERENCES Deduction(Id)
);

-- 13. Создание таблицы AbsenceType (Тип отсутствия)
CREATE TABLE AbsenceType (
    Id SERIAL PRIMARY KEY,
    Name VARCHAR(255) NOT NULL
);

-- 14. Создание таблицы Absence (Отсутствие)
-- Ссылки на таблицы Employee и AbsenceType
CREATE TABLE Absence (
    Id SERIAL PRIMARY KEY,
    Employee_Id INT NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,
    AbsenceType_Id INT NOT NULL,
    FOREIGN KEY (Employee_Id) REFERENCES Employee(Id),
    FOREIGN KEY (AbsenceType_Id) REFERENCES AbsenceType(Id)
);
-- 15. Создание таблицы Experience (Стаж)
CREATE TABLE Experience (
    Id SERIAL PRIMARY KEY,
	Employee_Id INT NOT NULL,
    Years INT DEFAULT 0,
    CONSTRAINT fk_employee FOREIGN KEY (Employee_Id) REFERENCES Employee(Id)
);

