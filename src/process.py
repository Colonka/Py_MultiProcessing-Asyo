import random
import time
from src import utils

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

            student_correct = 0 # cчетчик верных ответов студента
            student_incorrect = 0 # cчетчик неверных ответов студента
            que = questions[:]

            for _ in range(3):
                question = random.choice(que)
                que.remove(question)
                correct_answers = utils.get_random_answers(examiner_stats[f"{name}_gender"], question.words[:])
                student_answer = utils.choosing_answer(student_stats[f"{st_id}_gender"], question.words)
                if student_answer in correct_answers:
                    student_correct += 1
                    question_stats[question.text] += 1
                else:
                    student_incorrect += 1

            # Оценка результата
            if utils.evaluate(student_correct, student_incorrect):
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
                examiner_stats[f"{name}_current_student"] = "Что-то типо обЭда"
                time.sleep(random.uniform(12, 18))  # Перерыв на обед
                start_time = time.time()
