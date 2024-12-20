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


class Student:
    def __init__(self, name, gender):
        self.name = name
        self.gender = gender  # 'М' или 'Ж'
        self.status = "Очередь"  # Изначально в очереди
        self.success_time = 0
        self.fail_time = 0

    def answer_question(self, words):
        """Эмуляция ответа студента на вопрос."""
        return choosing_answer(self.gender, words)


class Examiner:
    BADMOOD = 1 / 8
    GOODMOOD = 1 / 4
    question_num = 3

    def __init__(self, name, gender):
        self.name = name
        self.total_students = 0
        self.failed_students = 0
        self.current_student = "-"
        self.work_time = 0
        self.gender = gender

    def get_random_answers(self, words):
        """Эмуляция выбора экзаменатором верных ответов."""
        answers = []
        answers.append(choosing_answer(self.gender, words))
        words.remove(answers[0])

        while True:
            if words:
                if random.random() < 1 / 3:  # Экзаменатор с вероятностью 1/3 добавляет новое слово в ответы
                    answers.append(choosing_answer(self.gender, words))
                    words.remove(answers[-1])
            else:
                break            

        return answers

# Оценка экзамена
    def evaluate(self, student_correct, student_incorrect):
        if random.random() < self.BADMOOD:  # Плохое настроение
            return False
        if random.random() < self.GOODMOOD:  # Хорошее настроение
            return True
        # Нейтральное настроение — объективная оценка
        return student_correct > student_incorrect

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
def examiner_process(examiner: Examiner, student_queue, result_queue, questions, examiner_stats):
    total_time = time.time()

    while True:
        if student_queue.empty():
            break
        else:
            student = student_queue.get()
            examiner.current_student = student.name
            examiner.total_students += 1

            student_correct = 0 # cчетчик верных ответов студента
            student_incorrect = 0 # cчетчик неверных ответов студента

            ex_len_name = len(examiner.name)
            exam_time = random.uniform(ex_len_name - 1, ex_len_name + 1)

            # Экзаменатор задает вопросы пока не закончится время экзамена
            time.sleep(exam_time)

            for _ in range(examiner.question_num):
                question = random.choice(questions)
                correct_answers = examiner.get_random_answers(question.words[:])
                student_answer = student.answer_question(question.words)
                if student_answer in correct_answers:
                    student_correct += 1
                else:
                    student_incorrect += 1

            # Оценка результата
            if examiner.evaluate(student_correct, student_incorrect):
                result_queue.put((student.name, "Сдал"))
                if exam_time < student.success_time:
                    student.success_time = exam_time
            else:
                examiner.failed_students += 1
                result_queue.put((student.name, "Провалил"))
                if exam_time < student.fail_time:
                    student.fail_time = exam_time

            # Обновление статистики экзаменатора в shared memory
            examiner_stats[examiner.name] = {
                "current_student": examiner.current_student,
                "total_students": examiner.total_students,
                "failed_students": examiner.failed_students,
                "work_time": time.time() - total_time
            }

            # Обед через 30 секунд
            if time.time() - total_time > 30:
                examiner.current_student = "-"
                time.sleep(random.uniform(12, 18))  # Перерыв на обед
                total_time = time.time()

# Отображает таблицу студентов
def display_student_table(student_status):
    student_table = PrettyTable()
    student_table.field_names = ["Студент", "Статус"]
    for status in ["Очередь", "Сдал", "Провалил"]:
        for student in student_status[status]:
            student_table.add_row([student, status])
    print("Таблица студентов:")
    print(student_table)

# Отображает таблицу экзаменаторов
def display_examiner_table(examiner_stats, examiner_objects, show_current_student=False):
    examiner_table = PrettyTable()
    if show_current_student:
        examiner_table.field_names = ["Экзаменатор", "Текущий студент", "Всего студентов", "Завалил", "Время работы"]
    else:
        examiner_table.field_names = ["Экзаменатор", "Всего студентов", "Завалил", "Время работы"]

    for examiner in examiner_objects:
        stats = examiner_stats.get(examiner.name, {})
        if show_current_student:
            examiner_table.add_row([
                examiner.name,
                stats.get("current_student", "-"),
                stats.get("total_students", 0),
                stats.get("failed_students", 0),
                f"{stats.get('work_time', 0):.2f}"
            ])
        else:
            examiner_table.add_row([
                examiner.name,
                stats.get("total_students", 0),
                stats.get("failed_students", 0),
                f"{stats.get('work_time', 0):.2f}"
            ])
    print("\nТаблица экзаменаторов:")
    print(examiner_table)

# Общий статус с учётом текущих данных
def display_status(student_status, examiner_stats, examiner_objects, total_students, start_time):
    #os.system('cls' if os.name == 'nt' else 'clear')
    display_student_table(student_status)
    display_examiner_table(examiner_stats, examiner_objects, show_current_student=True)
    print(f"\nОставшихся в очереди студентов: {len(student_status['Очередь'])}/{total_students}")
    print(f"Время с начала экзамена: {time.time() - start_time:.2f} сек")

# Итоговый статус по завершении экзамена
def display_final(student_status, examiner_stats, examiner_objects, start_time, students):
    # display_student_table(student_status)
    # display_examiner_table(examiner_stats, examiner_objects, show_current_student=False)
    print(f"\nВремя с момента начала экзамена и до момента и его завершения: {time.time() - start_time:.2f} сек")

    tmp = {}
    for s in students:
        tmp[s.success_time] = s.name
    k_min = min(tmp.keys())
    best = [v for k, v in tmp.items() if k == k_min]
    print(f"Имена лучших студентов: {', '.join(best)}")

    proc = {}

    for s in examiner_objects:
        #proc[(s.failed_students/s.total_students)*100] = s.name
        print(s.total_students)
    proc_min = min(proc.keys())
    best_ex = [v for k,v in proc.items() if k == proc_min]
    print(f"Имена лучших экзаменаторов: {', '.join(best_ex)}")

    print(f"Имена студентов, которых после экзамена отчислят: ")
    print(f"Лучшие вопросы: ")
    print(f"Вывод: ")


def main():
    examiners, students, questions = load_data()

    student_queue = mp.Queue()
    result_queue = mp.Queue()

    # Используем Manager для хранения статистики экзаменаторов
    with mp.Manager() as manager:
        examiner_stats = manager.dict()

        for student in students:
            student_queue.put((student))

        processes = []
        examiner_objects = []
        for examiner in examiners:
            examiner_objects.append(examiner)
            p = mp.Process(target=examiner_process, args=(examiner, student_queue, result_queue, questions, examiner_stats))
            p.start()
            processes.append(p)

        # Сбор результатов
        total_students = len(students)
        student_status = {"Очередь": [s.name for s in students], "Сдал": [], "Провалил": []}
        start_time = time.time()

        while any(p.is_alive() for p in processes):
            try:
                result = result_queue.get(timeout=0.1)
                if result[0] == "EXAMINER_STATS":
                    pass
                else:
                    student_name, status = result
                    student_status["Очередь"].remove(student_name)
                    student_status[status].append(student_name)
            except:
                continue
            

            #Обновление информационных таблиц во время работы
            display_status(student_status, examiner_stats, examiner_objects, total_students, start_time)

        for p in processes:
            p.join()

        #Вывод финальной информции после окончания экзаменов
        display_final(student_status, examiner_stats, examiner_objects, start_time, students)

if __name__ == "__main__":
    main()
