import multiprocessing as mp
import random
import time
import os
from prettytable import PrettyTable

# Классы
class Question:
    def __init__(self, text):
        self.text = text
        self.words = text.split()
        self.success = 0

class Student:
    def __init__(self, name, gender):
        self.name = name
        self.id = 0
        self.gender = gender  # 'М' или 'Ж'
        self.status = "Очередь"  # Изначально в очереди
        self.success_time = 0.0
        self.fail_time = 0.0

class Examiner:
    def __init__(self, name, gender):
        self.name = name
        self.gender = gender
        self.total_students = 0
        self.failed_students = 0
        self.current_student = "-"
        self.work_time = 0.0

# Оценка экзамена
def evaluate(student_correct, student_incorrect):
    BADMOOD = 1 / 8
    GOODMOOD = 1 / 4

    if random.random() < BADMOOD:  # Плохое настроение
        return False
    if random.random() < GOODMOOD:  # Хорошее настроение
        return True
    # Нейтральное настроение — объективная оценка
    return student_correct > student_incorrect

# Эмуляция ответа студента на вопрос    
def answer_question(gender, words):
    return choosing_answer(gender, words)

# Выбор вопросов     
def get_random_answers(gender, words):
    answers = []
    answers.append(choosing_answer(gender, words))
    words.remove(answers[0])

    while True:
        if words:
            if random.random() < 1 / 3:  # Экзаменатор с вероятностью 1/3 добавляет новое слово в ответы
                answers.append(choosing_answer(gender, words))
                words.remove(answers[-1])
        else:
            break            

    return answers

# Выбор ответов
def choosing_answer(gender, words):
    weights = list()
    if gender == "М":
        weights = list(range(len(words), 0, -1))
    else:
        weights = list(range(1, len(words) + 1))
    total_weight = sum(weights)
    probabilities = [w / total_weight for w in weights]
    return random.choices(words, probabilities, k=1)[0]

# Чтение данных
def load_data():
    with open("examiners.txt", "r", encoding="utf-8") as f:
        examiners = list(map(lambda line: Examiner(*line.strip().split(" ")), f))
    with open("students.txt", "r", encoding="utf-8") as f:
        students = list(map(lambda line: Student(*line.strip().split(" ")), f))
    with open("questions.txt", "r", encoding="utf-8") as f:
        questions = list(map(lambda line: Question(line.strip()), f))
    return examiners, students, questions


# Основная логика
def examiner_process(name, student_queue, examiner_stats, student_stats, question_stats, questions):
    start_time = time.time()

    while True:
        if student_queue.empty():
            break
        else:
            exam_time = random.uniform(len(examiner_stats[f"{name}"]) - 1, len([f"{name}"]) + 1)
            st_id = student_queue.get() # берем студента по id из очереди
            examiner_stats[f"{name}_current_student"] = student_stats[f"{st_id}_name"]
            examiner_stats[f"{name}_total_students"] += 1
            examiner_stats[f"{name}_work_time"] = time.time() - start_time
            
            student_stats[f"{st_id}_status"] = "На экзамене"

            end_time = time.time() + exam_time
            # Экзаменатор задает вопросы пока не закончится время экзамена
            while time.time() < end_time:
                examiner_stats[f"{name}_work_time"] = time.time() - start_time
            #time.sleep(exam_time)

            student_correct = 0 # cчетчик верных ответов студента
            student_incorrect = 0 # cчетчик неверных ответов студента
            que = questions[:]

            for _ in range(3):
                question = random.choice(que)
                que.remove(question)
                correct_answers = get_random_answers(examiner_stats[f"{name}_gender"], question.words[:])
                student_answer = answer_question(student_stats[f"{st_id}_gender"], question.words)
                if student_answer in correct_answers:
                    student_correct += 1
                    question_stats[question.text] += 1
                else:
                    student_incorrect += 1

            # Оценка результата
            if evaluate(student_correct, student_incorrect):
                student_stats[f"{st_id}_status"] = "Сдал"
                if student_stats[f"{st_id}_success_time"] == 0:
                    student_stats[f"{st_id}_success_time"] = exam_time
                else: 
                    if exam_time < student_stats[f"{st_id}_success_time"]:
                        student_stats[f"{st_id}_success_time"] = exam_time
            else:
                examiner_stats[f"{name}_failed_students"] += 1
                student_stats[f"{st_id}_status"] = "Провалил"
                if student_stats[f"{st_id}_fail_time"] == 0.0:
                    student_stats[f"{st_id}_fail_time"] = exam_time
                    if exam_time < student_stats[f"{st_id}_fail_time"]:
                        print("Завалили")
                        student_stats[f"{st_id}_fail_time"] = exam_time

            examiner_stats[f"{name}_work_time"] = time.time() - start_time

            # Обед через 30 секунд
            if time.time() - start_time > 30:
                examiner_stats[f"{name}_current_student"] = " - "
                time.sleep(random.uniform(12, 18))  # Перерыв на обед
                start_time = time.time()


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
def display_final(student_stats, students, examiner_stats, examiners, question_stats, questions, start_time, total_students):
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

def main():
    examiners, students, questions = load_data()

    student_queue = mp.Queue()
    it_id = 0 # для индексации студентов 
    for student in students:
        student.id = it_id
        student_queue.put(student.id)
        it_id += 1

    # Используем Manager для сбора и хранения статистики
    with mp.Manager() as manager:
        examiner_stats = manager.dict()
        student_stats = manager.dict()
        question_stats = manager.dict()

        # Работаем с простыми ключамя верхнего уровня, т.к. 
        # невозможна синхронизация данных с вложенностью(словарь словарей или список словарей)
        for examiner in examiners:
            ex_name = examiner.name
            examiner_stats[f"{ex_name}"] = ex_name
            examiner_stats[f"{ex_name}_gender"] = examiner.gender
            examiner_stats[f"{ex_name}_total_students"] = examiner.total_students
            examiner_stats[f"{ex_name}_failed_students"] = examiner.failed_students
            examiner_stats[f"{ex_name}_current_student"] = examiner.current_student
            examiner_stats[f"{ex_name}_work_time"] = examiner.work_time

        for student in students:
            st_id = student.id
            student_stats[f"{st_id}_name"] = student.name
            student_stats[f"{st_id}_gender"] = student.gender
            student_stats[f"{st_id}_status"] = student.status
            student_stats[f"{st_id}_success_time"] = student.success_time
            student_stats[f"{st_id}_fail_time"] = student.fail_time

        for question in questions:
            question_stats[question.text] = question.success

        total_students = len(students)
        start_time = time.time()
        processes = []
        display_status(student_stats, students, examiner_stats, examiners, total_students, start_time)
        for i in range(len(examiners)):
            p = mp.Process(target=examiner_process, args=(examiners[i].name, student_queue, examiner_stats, student_stats, question_stats, questions))
            p.start()
            processes.append(p)

        while any(p.is_alive() for p in processes):
           display_status(student_stats, students, examiner_stats, examiners, total_students, start_time)
        
        for p in processes:
            p.join()

        #Вывод финальной информции после окончания экзаменов
        display_final(student_stats, students, examiner_stats, examiners, question_stats, questions, start_time, total_students)

if __name__ == "__main__":
    main()
