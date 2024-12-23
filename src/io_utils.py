from src import models
from src import config
import time
import os
from prettytable import PrettyTable

# Чтение данных
def load_data():
    with open(config.DATA_DIR / "examiners.txt", "r", encoding="utf-8") as f:
        examiners = list(map(lambda line: models.Examiner(*line.strip().split(" ")), f))
    with open(config.DATA_DIR / "students.txt", "r", encoding="utf-8") as f:
        students = list(map(lambda line: models.Student(*line.strip().split(" ")), f))
    with open(config.DATA_DIR / "questions.txt", "r", encoding="utf-8") as f:
        questions = list(map(lambda line: models.Question(line.strip()), f))
    return examiners, students, questions

# Отображает таблицу студентов
def display_student_table(student_stats, students):
    student_table = PrettyTable()
    student_table.field_names = ["Студент", "Статус"]
    for student in students:
        student_table.add_row([student_stats[f"{student.id}_name"], student_stats[f"{student.id}_status"]])
    print("Таблица студентов:")
    print(student_table)

# Отображает таблицу экзаменаторов
def display_examiner_table(examiner_stats, examiners, show_current_student=False):
    examiner_table = PrettyTable()
    if show_current_student:
        examiner_table.field_names = ["Экзаменатор", "Текущий студент", "Всего студентов", "Завалил", "Время работы"]
    else:
        examiner_table.field_names = ["Экзаменатор", "Всего студентов", "Завалил", "Время работы"]

    for examiner in examiners:
        if show_current_student:
            examiner_table.add_row([
                examiner_stats[f"{examiner.name}"],
                examiner_stats[f"{examiner.name}_current_student"],
                examiner_stats[f"{examiner.name}_total_students"],
                examiner_stats[f"{examiner.name}_failed_students"],
                f"{examiner_stats[f"{examiner.name}_work_time"]:.2f}"
            ])
        else:
            examiner_table.add_row([
                examiner_stats[f"{examiner.name}"],
                examiner_stats[f"{examiner.name}_total_students"],
                examiner_stats[f"{examiner.name}_failed_students"],
                f"{examiner_stats[f"{examiner.name}_work_time"]:.2f}"
            ])
    print("\nТаблица экзаменаторов:")
    print(examiner_table)

# Общий статус с учётом текущих данных
def display_status(student_stats, students, examiner_stats, examiners, total_students, start_time):
        os.system('cls' if os.name == 'nt' else 'clear')
        display_student_table(student_stats, students)
        display_examiner_table(examiner_stats, examiners, show_current_student=True)

        q = 0
        for s in students:
            if student_stats[f"{s.id}_status"] == "Очередь":
                q += 1

        print(f"\nОставшихся в очереди студентов: {q}/{total_students}")
        print(f"Время с начала экзамена: {time.time() - start_time:.2f} сек")

# Итоговый статус по завершении экзамена
def display_final(student_stats, students, examiner_stats, examiners, question_stats, start_time, total_students):
    os.system('cls' if os.name == 'nt' else 'clear')

    display_student_table(student_stats, students)
    display_examiner_table(examiner_stats, examiners, show_current_student=False)
    print(f"\nВремя с момента начала экзамена и до момента и его завершения: {time.time() - start_time:.2f} сек")

    tmp = {}
    for s in students:
        if student_stats[f"{s.id}_success_time"] > 0:
            tmp[student_stats[f"{s.id}_success_time"]] = s.name
    k_min = min(tmp.keys())
    best = [v for k, v in tmp.items() if k == k_min]
    print(f"Имена лучших студентов: {', '.join(best)}")

    proc = {}
    bad = 0 #для подсчета заваливших экз
    for ex in examiners:
        bad += examiner_stats[f"{ex.name}_failed_students"] 
        proc[(examiner_stats[f"{ex.name}_failed_students"] / examiner_stats[f"{ex.name}_total_students"]) * 100] = ex.name
    proc_min = min(proc.keys())
    best_ex = [v for k,v in proc.items() if k == proc_min]
    print(f"Имена лучших экзаменаторов: {', '.join(best_ex)}")

    tmp.clear()
    for s in students:
        if student_stats[f"{s.id}_fail_time"] > 0:
            tmp[student_stats[f"{s.id}_fail_time"]] = s.name
    if tmp:
        k_min = min(tmp.keys())
        worst = [v for k, v in tmp.items() if k == k_min]
        print(f"Имена студентов, которых после экзамена отчислят: {', '.join(worst)}")
    else:
        print("Имена студентов, которых после экзамена отчислят: - ")

    max_q = max(question_stats.values())
    best_q = [key for key, value in question_stats.items() if value == max_q]
    print(f"Лучшие вопросы: {', '.join(best_q)}")

    result = ""
    perc = 100 - ((bad/total_students) * 100)
    if perc >= 85.0:
        result = "Экзамен прошел успешно"
    else:
        result = "Экзамен прошел НЕ успешно"
    print(f"Вывод: {result}. Сдали экзамен {perc} студентов.")
