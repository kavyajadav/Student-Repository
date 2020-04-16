"""
This program is a data repository of courses, students, and instructors.  
The system will be used to help students track their required courses, 
the courses they have successfully completed, their grades,  GPA, etc.  
The system will also be used by faculty advisors to help students to create study plans

Author : Kavya Jadhav
Version : Python 3.7.6
"""

import os
import sqlite3
from collections import defaultdict
from prettytable import PrettyTable
from typing import Dict, Set, List, Iterator, Tuple, DefaultDict
from HW08_kavyaJ import file_reader


class Student:
    # Student class holds the details of students
    header = ["CWID", "Name", "Major", "Completed Courses", "Remaining Required", "Remaining Electives",
              "GPA"]

    def __init__(self, cwid, name, major):
        self._cwid: int = cwid
        self._name: str = name
        self._major: str = major
        self._courses: Dict[str, str] = dict()

    def add_course(self, course, grade):
        self._courses[course] = grade

    def gpa(self):
        grades: Dict[str, float] = {"A": 4.00, "A-": 3.75, "B+": 3.25, "B": 3.00, "B-": 2.75, "C+": 2.25, "C": 2.00, "C-": 0.00,
                                    "D+": 0.00, "D": 0.00, "D-": 0.00, "F": 0.00}
        try:
            total: float = sum([grades[grade] for grade in self._courses.values()]) / len(self._courses.values())
            return round(total, 2)
        except ZeroDivisionError as e:
            print(e)

    def ptable_row(self):
        major, passed_courses, rem_required, rem_electives = self._major.courses_left(self._courses)
        return [self._cwid, self._name, major, sorted(passed_courses), sorted(rem_required), sorted(rem_electives),
                self.gpa()]


class Instructor:
    # Instructor class holds all of the details of an instructor, names of the courses taught 
    # along with the number of students who have taken the course
    header2 = ["CWID", "Name", "Dept", "Course", "Students"]

    def __init__(self, cwid: int, name: str, dept: str):
        """A constructor that Initialize instructor table details """
        self._cwid: int = cwid
        self._name: str = name
        self._dept: str = dept
        self._courses_i: DefaultDict[str, int] = defaultdict(int)

    def add_student(self, course):
        self._courses_i[course] += 1

    def ptable_row(self):
        for course, count in self._courses_i.items():
            yield [self._cwid, self._name, self._dept, course, count]


class Major:
    #Major Class consist the info about the number of majors and electives courses
    names = ['Major', 'Required Courses', 'Electives']
    grades_given = {'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C'}

    def __init__(self, dept):
        self._dept: str = dept
        self._required: Set = set()
        self._electives: Set = set()

    def add_remain_electives(self, course, req):
        if req == 'R':
            self._required.add(course)
        elif req == 'E':
            self._electives.add(course)
        else:
            raise ValueError("Course not found")

    def courses_left(self, completed_courses):
        completed_courses = {course for course, grade in completed_courses.items() if grade in Major.grades_given}
        rem_core_required = self._required - completed_courses
        if self._electives.intersection(completed_courses):
            rem_electives = {}
        else:
            rem_electives = self._electives - completed_courses

        return self._dept, completed_courses, rem_core_required, rem_electives

    def ptable_row(self):
        return [self._dept, sorted(self._required), sorted(self._electives)]


class University:
    # University class has stored details of students and instructors with grades of students
    def __init__(self, dir: str, hd=True):
        self._dir: str = dir
        self._students: Dict[str, Student] = dict()
        self._instructors: Dict[str, Instructor] = dict()
        self._majors: Dict[str, Major] = dict()

        try:
            self._get_majors_details(os.path.join(dir, "majors.txt"))
            self._get_students_details(os.path.join(dir, "students.txt"))
            self._get_instructors_details(os.path.join(dir, "instructors.txt"))
            self._get_grades_details(os.path.join(dir, "grades.txt"))

        except (FileNotFoundError, ValueError) as v:
            print(v)
        else:
            if hd:
                print("Student summary table")
                self.print_student_prettytable()

                print("Instructor summary table")
                self.print_instructor_prettytable()

                print("Majors Table")
                self.print_majors_prettytable()

                print("Student Grade Summary table")
                self.print_grades_prettytable()

    def _get_majors_details(self, path):
        try:
            major_file: Iterator[Tuple[str]] = file_reader(path, 3, sep='\t', header=True)
            for major, flag, course in major_file:
                if major not in self._majors:
                    self._majors[major] = Major(major)
                self._majors[major].add_remain_electives(course, flag)
        except ValueError as v:
            print(v)

    def _get_students_details(self, path):
        try:
            student_file: Iterator[Tuple[str]] = file_reader(path, 3, sep='\t', header=True)
            for cwid, name, major in student_file:
                if major not in self._majors:
                    print(f"Student {cwid} '{name}' has unknown major '{major}'")
                else:
                    self._students[cwid] = Student(cwid, name, self._majors[major])
        except ValueError as e:
            print(e)

    def _get_instructors_details(self, path: str):
        try:
            instructor_file: Iterator[Tuple[str]] = file_reader(path, 3, sep='\t', header=True)
            for cwid, name, dept in instructor_file:
                self._instructors[cwid] = Instructor(cwid, name, dept)
        except ValueError as e:
            print(e)

    def _get_grades_details(self, path: str):
        try:
            grades_file = file_reader(path, 4, sep='\t', header=True)
            for student_cwid, course, grade, instructor_cwid in grades_file:
                if student_cwid in self._students:
                    self._students[student_cwid].add_course(course, grade)
                else:
                    print(f"Grades for student whose CWID not registered {student_cwid}")

                if instructor_cwid in self._instructors:
                    self._instructors[instructor_cwid].add_student(course)
                else:
                    print(f"Grade for unknown instructor {instructor_cwid}")
        except ValueError as e:
            print(e)

    def instructor_summary_database(self):
        db: sqlite3.Connection = sqlite3.connect("/Users/kavyaj/Desktop/810/kavya.sqlite")
        sql_query: str = "SELECT i.CWID, i.Name, i.Dept, g.Courses, COUNT(*) " \
                         "FROM Grades g JOIN Instructor i on InstructorCWID = CWID " \
                         "GROUP BY i.CWID, g.Courses ORDER BY i.CWID DESC, g.Courses DESC"
        for cwid, name, department, course, count in db.execute(sql_query):
            yield [cwid, name, department, course, count]

    def student_summary_database(self):
        db: sqlite3.Connection = sqlite3.connect("/Users/kavyaj/Desktop/810/kavya.sqlite")
        sql_query: str = "SELECT s.Name, s.CWID, g.Courses, g.Grade, i.Name AS 'Instructor' " \
                         "FROM Grades g  JOIN students s  ON g.StudentCWID = s.CWID " \
                         "JOIN Instructor i ON g.InstructorCWID = i.CWID ORDER BY s.Name"
        for name, cwid, course, grade, instructor in db.execute(sql_query):
            yield [name, cwid, course, grade, instructor]

    def print_student_prettytable(self):
        prettytable: PrettyTable = PrettyTable(field_names=Student.header)
        a = list()
        for student in self._students.values():
            prettytable.add_row(student.ptable_row())
            a.append(student.ptable_row())

        print(prettytable)

    def print_instructor_prettytable(self):
        prettytable: PrettyTable = PrettyTable(field_names=Instructor.header2)
        for row in self.instructor_summary_database():
            prettytable.add_row(row)
        print(prettytable)

    def print_majors_prettytable(self):
        prettytable: PrettyTable = PrettyTable(field_names=Major.names)
        for major in self._majors.values():
            prettytable.add_row(major.ptable_row())
        print(prettytable)

    def print_grades_prettytable(self):
        prettytable: PrettyTable = PrettyTable(field_names=["Name", "CWID", "Course", "Grade", "Instructor"])
        for each_row in self.student_summary_database():
            prettytable.add_row(each_row)
        print(prettytable)


# Main fucntion

def main():
    University("/Users/kavyaj/Desktop/810")


if __name__ == '__main__':
    main()
