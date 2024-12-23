import multiprocessing as mp
import time
from src import io_utils as io
from src import process

def main():
    examiners, students, questions = io.load_data()

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
        io.display_status(student_stats, students, examiner_stats, examiners, total_students, start_time)
        for i in range(len(examiners)):
            p = mp.Process(target=process.examiner_process, args=(examiners[i].name, student_queue, examiner_stats, student_stats, question_stats, questions))
            p.start()
            processes.append(p)

        while any(p.is_alive() for p in processes):
           io.display_status(student_stats, students, examiner_stats, examiners, total_students, start_time)
        
        for p in processes:
            p.join()

        #Вывод финальной информции после окончания экзаменов
        io.display_final(student_stats, students, examiner_stats, examiners, question_stats, start_time, total_students)

if __name__ == "__main__":
    main()
