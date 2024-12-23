import random

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

# Эмуляция выбора ответа
def choosing_answer(gender, words):
    weights = list()
    if gender == "М":
        weights = list(range(len(words), 0, -1))
    else:
        weights = list(range(1, len(words) + 1))
    total_weight = sum(weights)
    probabilities = [w / total_weight for w in weights]
    return random.choices(words, probabilities, k=1)[0]

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
