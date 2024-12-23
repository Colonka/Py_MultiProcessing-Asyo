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
