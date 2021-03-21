"""CSC148 Assignment 1

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Misha Schwartz, Mario Badr, Christine Murad, Diane Horton, Sophia Huynh
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) 2020 Misha Schwartz, Mario Badr, Christine Murad, Diane Horton,
Sophia Huynh and Jaisie Sin

=== Module Description ===

This file contains classes that define different algorithms for grouping
students according to chosen criteria and the group members' answers to survey
questions. This file also contain a classe that describes a group of students as
well as a grouping (a group of groups).
"""
from __future__ import annotations
import random
from typing import TYPE_CHECKING, List, Any
from course import sort_students, Course, Student
if TYPE_CHECKING:
    from survey import Survey



def slice_list(lst: List[Any], n: int) -> List[List[Any]]:
    """
    Return a list containing slices of <lst> in order. Each slice is a
    list of size <n> containing the next <n> elements in <lst>.

    The last slice may contain fewer than <n> elements in order to make sure
    that the returned list contains all elements in <lst>.

    === Precondition ===
    n <= len(lst)

    >>> slice_list([3, 4, 6, 2, 3], 2) == [[3, 4], [6, 2], [3]]
    True
    >>> slice_list(['a', 1, 6.0, False], 3) == [['a', 1, 6.0], [False]]
    True
    """
    new_lst = []
    sublist = []
    for counter, item in enumerate(lst, 1):
        if counter == len(lst):
            sublist.append(item)
            new_lst.append(sublist)
            break
        if not counter % n == 0:
            sublist.append(item)
        else:
            sublist.append(item)
            new_lst.append(sublist)
            sublist = []
    return new_lst



def windows(lst: List[Any], n: int) -> List[List[Any]]:
    """
    Return a list containing windows of <lst> in order. Each window is a list
    of size <n> containing the elements with index i through index i+<n> in the
    original list where i is the index of window in the returned list.

    === Precondition ===
    n <= len(lst)

    >>> windows([3, 4, 6, 2, 3], 2) == [[3, 4], [4, 6], [6, 2], [2, 3]]
    True
    >>> windows(['a', 1, 6.0, False], 3) == [['a', 1, 6.0], [1, 6.0, False]]
    True
    """
    sublist = []
    new_lst = []
    if len(lst) <= n:
        return [lst]
    for index in range(len(lst)):
        for i in range(n):
            sublist.append(lst[index + i])
        new_lst.append(sublist)
        sublist = []
        if index + n == len(lst):
            break
    return new_lst






class Grouper:
    """
    An abstract class representing a grouper used to create a grouping of
    students according to their answers to a survey.

    === Public Attributes ===
    group_size: the ideal number of students that should be in each group

    === Representation Invariants ===
    group_size > 1
    """

    group_size: int

    def __init__(self, group_size: int) -> None:
        """
        Initialize a grouper that creates groups of size <group_size>

        === Precondition ===
        group_size > 1
        """
        self.group_size = group_size

    def make_grouping(self, course: Course, survey: Survey) -> Grouping:
        """ Return a grouping for all students in <course> using the questions
        in <survey> to create the grouping.
        """
        raise NotImplementedError


class AlphaGrouper(Grouper):
    """
    A grouper that groups students in a given course according to the
    alphabetical order of their names.

    === Public Attributes ===
    group_size: the ideal number of students that should be in each group

    === Representation Invariants ===
    group_size > 1
    """

    group_size: int

    def make_grouping(self, course: Course, survey: Survey) -> Grouping:
        """
        Return a grouping for all students in <course>.

        The first group should contain the students in <course> whose names come
        first when sorted alphabetically, the second group should contain the
        next students in that order, etc.

        All groups in this grouping should have exactly self.group_size members
        except for the last group which may have fewer than self.group_size
        members if that is required to make sure all students in <course> are
        members of a group.

        Hint: the sort_students function might be useful
        """

        lst_students = course.get_students()
        new_lst = sort_students(list(lst_students), 'name')
        grouping = Grouping()
        if self.group_size < len(new_lst):
            new_lst = slice_list(new_lst, self.group_size)
            for sublist in new_lst:
                group = Group(sublist)
                grouping.add_group(group)
        else:
            group = Group(new_lst)
            grouping.add_group(group)
        return grouping


class RandomGrouper(Grouper):
    """
    A grouper used to create a grouping of students by randomly assigning them
    to groups.

    === Public Attributes ===
    group_size: the ideal number of students that should be in each group

    === Representation Invariants ===
    group_size > 1
    """

    group_size: int

    def make_grouping(self, course: Course, survey: Survey) -> Grouping:
        """
        Return a grouping for all students in <course>.

        Students should be assigned to groups randomly.

        All groups in this grouping should have exactly self.group_size members
        except for one group which may have fewer than self.group_size
        members if that is required to make sure all students in <course> are
        members of a group.
        """
        lst_students = list(course.get_students())
        new_list = random.sample(lst_students, len(lst_students))
        lst_students = new_list
        grouping = Grouping()
        if self.group_size < len(lst_students):
            lst_students = slice_list(lst_students, self.group_size)
            for sublist in lst_students:
                group = Group(sublist)
                grouping.add_group(group)
        else:
            group = Group(lst_students)
            grouping.add_group(group)
        return grouping


class GreedyGrouper(Grouper):
    """
    A grouper used to create a grouping of students according to their
    answers to a survey. This grouper uses a greedy algorithm to create
    groups.

    === Public Attributes ===
    group_size: the ideal number of students that should be in each group

    === Representation Invariants ===
    group_size > 1
    """

    group_size: int

    def make_grouping(self, course: Course, survey: Survey) -> Grouping:
        """
        Return a grouping for all students in <course>.

        Starting with a tuple of all students in <course> obtained by calling
        the <course>.get_students() method, create groups of students using the
        following algorithm:

        1. select the first student in the tuple that hasn't already been put
           into a group and put this student in a new group.
        2. select the student in the tuple that hasn't already been put into a
           group that, if added to the new group, would increase the group's
           score the most (or reduce it the least), add that student to the new
           group.
        3. repeat step 2 until there are N students in the new group where N is
           equal to self.group_size.
        4. repeat steps 1-3 until all students have been placed in a group.

        In step 2 above, use the <survey>.score_students method to determine
        the score of each group of students.

        The final group created may have fewer than N members if that is
        required to make sure all students in <course> are members of a group.
        """
        tup_students = course.get_students()
        free_students = list(tup_students)
        grouping = Grouping()
        while len(free_students) > self.group_size:
            first_student = free_students.pop(0)
            group = [first_student]
            while not len(group) == self.group_size:
                group_scores = {}
                for student in free_students:
                    try_group = group + [student]
                    score = survey.score_students(try_group)
                    group_scores[score] = student
                max_score = max(group_scores.keys())
                next_student = group_scores[max_score]
                group.append(next_student)
                free_students.remove(next_student)
            group = Group(group)
            grouping.add_group(group)
        last_group = Group(free_students)
        grouping.add_group(last_group)
        return grouping


class WindowGrouper(Grouper):
    """
    A grouper used to create a grouping of students according to their
    answers to a survey. This grouper uses a window search algorithm to create
    groups.

    === Public Attributes ===
    group_size: the ideal number of students that should be in each group

    === Representation Invariants ===
    group_size > 1
    """

    group_size: int

    def make_grouping(self, course: Course, survey: Survey) -> Grouping:
        """
        Return a grouping for all students in <course>.

        Starting with a tuple of all students in <course> obtained by calling
        the <course>.get_students() method, create groups of students using the
        following algorithm:

        1. Get the windows of the list of students who have not already been
           put in a group.
        2. For each window in order, calculate the current window's score as
           well as the score of the next window in the list. If the current
           window's score is greater than or equal to the next window's score,
           make a group out of the students in current window and start again at
           step 1. If the current window is the last window, compare it to the
           first window instead.

        In step 2 above, use the <survey>.score_students to determine the score
        of each window (list of students).

        In step 1 and 2 above, use the windows function to get the windows of
        the list of students.

        If there are any remaining students who have not been put in a group
        after repeating steps 1 and 2 above, put the remaining students into a
        new group.
        """
        tup_students = course.get_students()
        lst_students = list(tup_students)
        grouping = Grouping()
        lst_winds = windows(lst_students, self.group_size)
        while len(lst_winds) != 1:
            result = self._find_best_window(survey, lst_winds, lst_students)
            wind = result[0]
            group = Group(wind)
            grouping.add_group(group)
            lst_winds = result[1]
        last_winds = []
        for student in lst_winds[0]:
            last_winds.append(student)
        grouping.add_group(Group(last_winds))
        return grouping

    def _find_best_window(self, survey: Survey,
                          windows_: List[List[Any]],
                          lst_students: List[Student]) -> List:
        """"
        Return a list, first element is the new group to be added to window,
        second element is the new windows list
        """

        for index, window in enumerate(windows_):
            if index + 1 == len(windows_):
                wind_curr_score = survey.score_students(window)
                wind_first = survey.score_students(windows_[0])
                if wind_curr_score >= wind_first:
                    new_lst = self._new_windows(window, lst_students)
                    return [window, new_lst]
                else:
                    window = windows_[0]
                    new_lst = self._new_windows(window, lst_students)
                    return [window, new_lst]
            else:
                wind_curr_score = survey.score_students(window)
                wind_next_score = survey.score_students(windows_[index + 1])
                if wind_curr_score >= wind_next_score:
                    new_lst = self._new_windows(window, lst_students)
                    return [window, new_lst]
        return None

    def _new_windows(self, window: List, free_students: List) -> List:
        """
        Returns a new_window list

        Helper method
        Removes the students in the window (who were put in the group) from the
        free_student list. Calls the windows function to generate new window lst
        """
        for student in window:
            free_students.remove(student)
        new_windows = windows(free_students, self.group_size)
        return new_windows


class Group:
    """
    A group of one or more students

    === Private Attributes ===
    _members: a list of unique students in this group

    === Representation Invariants ===
    No two students in _members have the same id
    """

    _members: List[Student]

    def __init__(self, members: List[Student]) -> None:
        """ Initialize a group with members <members> """
        for student in members:
            for others in members:
                if student.id == others.id and student != others:
                    raise AttributeError
        self._members = members

    def __len__(self) -> int:
        """ Return the number of members in this group """
        return len(self._members)

    def __contains__(self, member: Student) -> bool:
        """
        Return True iff this group contains a member with the same id
        as <member>.
        """
        for student in self._members:
            if student.id == member.id:
                return True
        return False

    def __str__(self) -> str:
        """
        Return a string containing the names of all members in this group
        on a single line.

        You can choose the precise format of this string.
        """
        student_string = ""
        for student in self._members:
            student_string += f"{student.name}, "
        return f"The names of students in this group are {student_string}"

    def get_members(self) -> List[Student]:
        """ Return a list of members in this group. This list should be a
        shallow copy of the self._members attribute.
        """
        lst = self._members[:]
        return lst


class Grouping:
    """
    A collection of groups

    === Private Attributes ===
    _groups: a list of Groups

    === Representation Invariants ===
    No group in _groups contains zero members
    No student appears in more than one group in _groups
    """

    _groups: List[Group]

    def __init__(self) -> None:
        """ Initialize a Grouping that contains zero groups """
        self._groups = []

    def __len__(self) -> int:
        """ Return the number of groups in this grouping """
        return len(self._groups)

    def __str__(self) -> str:
        """
        Return a multi-line string that includes the names of all of the members
        of all of the groups in <self>. Each line should contain the names
        of members for a single group.

        You can choose the precise format of this string.
        """
        group_string = ""
        for num, i in enumerate(self._groups):
            group_string += f"(Group {num+1}): {str(i)} \n"
        return group_string

    def add_group(self, group: Group) -> bool:
        """
        Add <group> to this grouping and return True.

        Iff adding <group> to this grouping would violate a representation
        invariant don't add it and return False instead.
        """
        if not self._groups:
            self._groups = [group]
            return True
        elif not group:
            return False
        else:
            if not self._check_duplicates(group):
                return False
            self._groups.append(group)
            return True

    def _check_duplicates(self, group: Group) -> bool:
        """
        Return True if the group does not contain any duplicate students and if
        no other groups in <self._groups> contain any overlapping students
        """
        for student in group.get_members():
            for sub_groups in self._groups:
                if sub_groups.__contains__(student):
                    return False
        return True

    def get_groups(self) -> List[Group]:
        """ Return a list of all groups in this grouping.
        This list should be a shallow copy of the self._groups
        attribute.
        """
        return self._groups[:]


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={'extra-imports': ['typing',
                                                  'random',
                                                  'survey',
                                                  'course']})
