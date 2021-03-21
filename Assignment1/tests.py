import pytest
import course
import survey
import criterion
import grouper
import pytest
from typing import List, Set, FrozenSet

@pytest.fixture
def students() -> List[course.Student]:
    return [course.Student(1, 'Zoro'),
            course.Student(2, 'Aaron'),
            course.Student(3, 'Gertrude'),
            course.Student(4, 'Yvette'),
            course.Student(5, 'Alisa'),
            course.Student(6, 'Paulina'),
            course.Student(7, 'Emily'),
            course.Student(7, 'Sophia'),
            course.Student(10, 'Jacob'),
            course.Student(11, 'Anna')]

@pytest.fixture
def questions() -> List[survey.Question]:
    return [survey.MultipleChoiceQuestion(1, 'why?', ['a', 'b', 'c', 'd']),
            survey.NumericQuestion(2, 'what?', -2, 4),
            survey.YesNoQuestion(3, 'really?'),
            survey.CheckboxQuestion(4, 'how?', ['a', 'b', 'c', 'd'])]

@pytest.fixture
def answers() -> List[List[survey.Answer]]:
    return [[survey.Answer('a'), survey.Answer('b'),
             survey.Answer('b'), survey.Answer('d'),
             survey.Answer('a'), survey.Answer('b'),
             survey.Answer('e'), survey.Answer('a')],
            [survey.Answer(0), survey.Answer(4),
             survey.Answer(-1), survey.Answer(1),
             survey.Answer(-3), survey.Answer(5),
             survey.Answer(0.5), survey.Answer(2)],
            [survey.Answer(True), survey.Answer(False),
             survey.Answer(True), survey.Answer(True),
             survey.Answer(False), survey.Answer(False),
             survey.Answer(False), survey.Answer(True)],
            [survey.Answer(['a', 'b']), survey.Answer(['a', 'b', 'c']),
             survey.Answer(['e']), survey.Answer(['d']),
             survey.Answer('a'), survey.Answer(['a', 'a', 'b']),
             survey.Answer(['a']), survey.Answer(['b'])]]

@pytest.fixture
def students_with_answers(students, questions, answers) -> List[course.Student]:
    for i, student in enumerate(students[:4]):
        for j, question in enumerate(questions[:4]):
            student.set_answer(question, answers[j][i])
    return students


@pytest.fixture
def course_with_students(empty_course, students) -> course.Course:
    empty_course.enroll_students(students)
    return empty_course


@pytest.fixture
def empty_course() -> course.Course:
    return course.Course('phy354')


@pytest.fixture
def course_with_students_with_answers(empty_course,
                                      students_with_answers) -> course.Course:
    empty_course.enroll_students(students_with_answers)
    return empty_course


class TestStudent:
    def test__str__(self, students) -> None:
        assert str(students[0]) == "Zoro"

    def test_has_answers(self, students_with_answers, questions) -> None:
        student_1 = students_with_answers[0]
        question_1 = questions[3]
        assert student_1.has_answer(question_1)

    def test_set_answers(self, students, students_with_answers, questions,
                         answers) -> None:
        student = students[3]
        answers = answers[0][0]
        student.set_answer(questions[0], answers)
        assert student._questions.values() == answers

    def test_get_answers(self, students_with_answers, questions,
                         students) -> None:
        for i, student in enumerate(students_with_answers[:8]):
            question = student.get_answer(questions[0])[questions[0].id]
            assert isinstance(question, survey.Question)

class TestCourse:
    def test_enroll_students(self, students, empty_course):
        students = students[4:8]
        empty_course.enroll_students(students)
        assert len(empty_course.students) == 3
        students = students[0:6]
        empty_course.enroll_students(students)
        assert len(empty_course.students) == 9

    def test__check_duplicates(self, students, empty_course):
        students = students[4:8]
        assert len(empty_course._check_duplicates(students)) == 3


    #def test_all_answered(self, ):


class TestMultipleChoiceQuestion:
    def test_str_multiples(self):
        question = survey.MultipleChoiceQuestion(1,
                                          "this is a question",
                                          ['option 1', 'option 2', 'option 3',
                                           'option 4'])
        assert "this is a question: possible answers are (1) option 1 " \
               "(2) option 2 (3) option 3 (4) option 4 , " \
               "(pick one)" == str(question)

    def test_validate_answer(self, questions, answers):
        qmc = questions[0]
        ans_valid_1 = answers[0][0]
        ans_valid_2 = answers[0][1]
        ans_invalid = answers[3][1]
        assert qmc.validate_answer(ans_valid_1)
        assert qmc.validate_answer(ans_valid_2)
        assert not qmc.validate_answer(ans_invalid)





if __name__ == '__main__':
    pytest.main(['tests.py'])
