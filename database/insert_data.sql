-- ============================================
-- Тестовые данные для Payroll App
-- ============================================

-- Справочники типов (ID: 1, 2, 3...)
INSERT INTO AccrualType (Name)
VALUES 
    ('Премия за эффективность'),
    ('Надбавка за стаж'),
    ('Выплата за сверхурочные'),
    ('Бонус за достижения');

INSERT INTO DeductionType (Name)
VALUES 
    ('НДФЛ'),
    ('Штраф'),
    ('Прочие удержания');

INSERT INTO AbsenceType (Name)
VALUES 
    ('Отпуск'),
    ('Больничный'),
    ('Отгул'),
    ('Командировка');

-- Должности (ID: 1, 2, 3...)
INSERT INTO Positions (Name, BaseSalary)
VALUES 
    ('Врач-терапевт участковый', 50000),
    ('Медицинская сестра', 35000),
    ('Медицинский регистратор', 40000),
    ('Врач-хирург', 60000),
    ('Старшая медицинская сестра', 45000);

-- Отделы (ID: 1, 2, 3...)
INSERT INTO Department (Name)
VALUES 
    ('Терапия'),
    ('Хирургия'),
    ('Регистратура'),
    ('Лаборатория'),
    ('Администрация');

-- Сотрудники (ID: 1, 2, 3...)
-- Используем подзапросы для связи с должностями и отделами
INSERT INTO Employee (FullName, Position_id, Department_Id)
VALUES
    ('Иванов Иван Иванович', 
     (SELECT Id FROM Positions WHERE Name = 'Врач-терапевт участковый'),
     (SELECT Id FROM Department WHERE Name = 'Терапия')),
    
    ('Петрова Алина Сергеевна', 
     (SELECT Id FROM Positions WHERE Name = 'Медицинская сестра'),
     (SELECT Id FROM Department WHERE Name = 'Хирургия')),
    
    ('Сидорова Анна Александровна', 
     (SELECT Id FROM Positions WHERE Name = 'Медицинский регистратор'),
     (SELECT Id FROM Department WHERE Name = 'Регистратура')),
    
    ('Кузнецов Дмитрий Владимирович', 
     (SELECT Id FROM Positions WHERE Name = 'Врач-хирург'),
     (SELECT Id FROM Department WHERE Name = 'Хирургия')),
    
    ('Михайлова Елена Николаевна', 
     (SELECT Id FROM Positions WHERE Name = 'Старшая медицинская сестра'),
     (SELECT Id FROM Department WHERE Name = 'Администрация'));

-- Начисления (связь через подзапросы)
INSERT INTO Accrual (AccrualType_Id, Amount, Conditions)
VALUES 
    ((SELECT Id FROM AccrualType WHERE Name = 'Премия за эффективность'), 5000, 'Премия за выполнение плана'),
    ((SELECT Id FROM AccrualType WHERE Name = 'Надбавка за стаж'), 3000, 'Надбавка за 5 лет стажа'),
    ((SELECT Id FROM AccrualType WHERE Name = 'Выплата за сверхурочные'), 2000, 'Оплата за сверхурочные часы'),
    ((SELECT Id FROM AccrualType WHERE Name = 'Бонус за достижения'), 1000, 'Премия');

-- Удержания (связь через подзапросы)
INSERT INTO Deduction (DeductionType_Id, Amount, Reason)
VALUES 
    ((SELECT Id FROM DeductionType WHERE Name = 'НДФЛ'), 7000, 'Налог на доходы физических лиц'),
    ((SELECT Id FROM DeductionType WHERE Name = 'Штраф'), 500, 'Штраф'),
    ((SELECT Id FROM DeductionType WHERE Name = 'Прочие удержания'), 2000, 'Прочие удержания');

-- Рабочие часы (связь через подзапросы)
INSERT INTO WorkSchedule (Employee_Id, WorkDate, HoursWorked)
VALUES 
    ((SELECT Id FROM Employee WHERE FullName = 'Иванов Иван Иванович'), '2026-06-01', 160),
    ((SELECT Id FROM Employee WHERE FullName = 'Петрова Алина Сергеевна'), '2026-06-01', 160),
    ((SELECT Id FROM Employee WHERE FullName = 'Сидорова Анна Александровна'), '2026-06-01', 150),
    ((SELECT Id FROM Employee WHERE FullName = 'Кузнецов Дмитрий Владимирович'), '2026-06-01', 170),
    ((SELECT Id FROM Employee WHERE FullName = 'Михайлова Елена Николаевна'), '2026-06-01', 160);

-- Стаж сотрудников
INSERT INTO Experience (Employee_Id, Years)
VALUES 
    ((SELECT Id FROM Employee WHERE FullName = 'Иванов Иван Иванович'), 10),
    ((SELECT Id FROM Employee WHERE FullName = 'Петрова Алина Сергеевна'), 5),
    ((SELECT Id FROM Employee WHERE FullName = 'Сидорова Анна Александровна'), 3),
    ((SELECT Id FROM Employee WHERE FullName = 'Кузнецов Дмитрий Владимирович'), 8),
    ((SELECT Id FROM Employee WHERE FullName = 'Михайлова Елена Николаевна'), 12);

-- ============================================
-- Сброс sequence для всех таблиц
-- ============================================

-- ============================================
-- Сброс sequence для всех таблиц
-- ============================================
-- Устанавливаем sequence на MAX(id) + 1, чтобы следующий INSERT получил правильный ID

-- ============================================
-- Сброс sequence для всех таблиц
-- ============================================

SELECT setval(pg_get_serial_sequence('AccrualType', 'id'), COALESCE((SELECT MAX(id) FROM AccrualType), 0));
SELECT setval(pg_get_serial_sequence('DeductionType', 'id'), COALESCE((SELECT MAX(id) FROM DeductionType), 0));
SELECT setval(pg_get_serial_sequence('AbsenceType', 'id'), COALESCE((SELECT MAX(id) FROM AbsenceType), 0));
SELECT setval(pg_get_serial_sequence('Positions', 'id'), COALESCE((SELECT MAX(id) FROM Positions), 0));
SELECT setval(pg_get_serial_sequence('Department', 'id'), COALESCE((SELECT MAX(id) FROM Department), 0));
SELECT setval(pg_get_serial_sequence('Employee', 'id'), COALESCE((SELECT MAX(id) FROM Employee), 0));
SELECT setval(pg_get_serial_sequence('Accrual', 'id'), COALESCE((SELECT MAX(id) FROM Accrual), 0));
SELECT setval(pg_get_serial_sequence('Deduction', 'id'), COALESCE((SELECT MAX(id) FROM Deduction), 0));
SELECT setval(pg_get_serial_sequence('WorkSchedule', 'id'), COALESCE((SELECT MAX(id) FROM WorkSchedule), 0));
SELECT setval(pg_get_serial_sequence('Experience', 'id'), COALESCE((SELECT MAX(id) FROM Experience), 0));