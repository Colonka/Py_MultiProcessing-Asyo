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

    def get_random_answers(self):
        """Эмуляция выбора экзаменатором верных ответов."""
        answers = []
        answers.append(self.words[0]) # добавить логику зависящую от гендера
        for word in self.words:
            if random.random() < 1 / 3:  # Экзаменатор с вероятностью 1/3 добавляет слово в ответы
                answers.append(word)
        return answers


class Student:
    def __init__(self, name, gender):
        self.name = name
        self.gender = gender  # 'М' или 'Ж'
        self.status = "Очередь"  # Изначально в очереди
        self.success_time = 0

    def answer_question(self, question: Question):
        """Эмуляция ответа студента на вопрос."""
        weights = list(range(len(question.words), 0, -1)) if self.gender == "М" else list(range(1, len(question.words) + 1))
        total_weight = sum(weights)
        probabilities = [w / total_weight for w in weights]
        return random.choices(question.words, probabilities, k=1)[0]


class Examiner:
    BADMOOD = 1 / 8
    GOODMOOD = 1 / 4

    def __init__(self, name, gender):
        self.name = name
        self.total_students = 0
        self.failed_students = 0
        self.current_student = "-"
        self.work_time = 0
        self.gender = gender

    def evaluate(self, student_correct, student_incorrect):
        """Оценка экзамена."""
        if random.random() < self.BADMOOD:  # Плохое настроение
            return False
        if random.random() < self.GOODMOOD:  # Хорошее настроение
            return True
        # Нейтральное настроение — объективная оценка
        return student_correct > student_incorrect
    

# Чтение данных

def load_data():
    """Чтение данных из файлов и создание объектов"""
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
        start_time = time.time()
        if student_queue.empty():
            break
        else:
            student = student_queue.get()
            examiner.current_student = student.name
            examiner.total_students += 1

            student_correct = 0 # cчетчик верных ответов студента
            student_incorrect = 0 # cчетчик неверных ответов студента

            exam_time = random.uniform(len(examiner.name) - 1, len(examiner.name) + 1)

            # Экзаменатор задает вопросы пока не закончится время экзамена
            time.sleep(exam_time)

            for _ in range(3):
                question = random.choice(questions) # 
                correct_answers = question.get_random_answers()
                student_answer = student.answer_question(question)
                if student_answer in correct_answers:
                    student_correct += 1
                else:
                    student_incorrect += 1

            # Оценка результата
            if examiner.evaluate(student_correct, student_incorrect):
                result_queue.put((student.name, "Сдал"))
            else:
                examiner.failed_students += 1
                result_queue.put((student.name, "Провалил"))

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

def display_student_table(student_status):
    """Отображает таблицу студентов."""
    student_table = PrettyTable()
    student_table.field_names = ["Студент", "Статус"]
    for status in ["Очередь", "Сдал", "Провалил"]:
        for student in student_status[status]:
            student_table.add_row([student, status])
    print("Таблица студентов:")
    print(student_table)

def display_examiner_table(examiner_stats, examiner_objects, show_current_student=False):
    """Отображает таблицу экзаменаторов."""
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

def display_status(student_status, examiner_stats, examiner_objects, total_students, start_time):
    """Общий статус с учётом текущих данных."""
    os.system('cls' if os.name == 'nt' else 'clear')
    display_student_table(student_status)
    display_examiner_table(examiner_stats, examiner_objects, show_current_student=True)
    print(f"\nОставшихся в очереди студентов: {len(student_status['Очередь'])}/{total_students}")
    print(f"Время с начала экзамена: {time.time() - start_time:.2f} сек")

def display_final(student_status, examiner_stats, examiner_objects, start_time):
    """Итоговый статус по завершении экзамена."""
    display_student_table(student_status)
    display_examiner_table(examiner_stats, examiner_objects, show_current_student=False)
    print(f"\nВремя с момента начала экзамена и до момента и его завершения: {time.time() - start_time:.2f} сек")
    print(f"Имена лучших студентов: ")
    print(f"Имена лучших экзаменаторов: ")
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
            

            #Обновление таблиц
            display_status(student_status, examiner_stats, examiner_objects, total_students, start_time)

        for p in processes:
            p.join()

        display_final(student_status, examiner_stats, examiner_objects, start_time)

if __name__ == "__main__":
    main()
