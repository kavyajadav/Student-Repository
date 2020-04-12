"""
This program is a data repository of courses, students, and instructors.  
The system will be used to help students track their required courses, 
the courses they have successfully completed, their grades,  GPA, etc.  
The system will also be used by faculty advisors to help students to create study plans

Author : Kavya Jadhav
Version : Python 3.7.6
"""

from typing import Dict, Set, List, Iterator, Tuple, DefaultDict
from prettytable import PrettyTable
from collections import defaultdict
from HW08_kavyaJ import file_reader
import os

#Student class holds the details of students

class Student(object):
    header1 = ["CWID", "Name", "Major", "Completed Courses", "Remaining Required", "Remaining Electives", "GPA"]

    def __init__(self, cwid: int, name: str, major: str) -> None:
        self._name: str = name
        self._cwid: int = cwid
        self._major: str = major
        self.student_course: Dict[str] = dict()

    def add_course(self, course: str, grade: str) -> None:
        self.student_course[course] = grade

    def calcgpa(self) -> None:
        grades: Dict[str, float] = {"A": 4.00, "A-": 3.75, "B+": 3.25, "B": 3.00, "B-": 2.75, "C+": 2.25, "C": 2.00,
                                    "C-": 0.00, "D+": 0.00, "D": 0.00, "D-": 0.00, "F": 0.00}
        try:
            total: float = sum([grades[grade] for grade in self.student_course.values()]) / len(self.student_course.values())
            return round(total, 2)
        except ZeroDivisionError as e:
            print(e)

    def ptable(self) -> None:
        """ Returning a student prettytable to prettytable method"""
        major, passed_courses, remain_required, remain_electives = self._major.courses_left(self.student_course)
        return [self._cwid, self._name, major, sorted(passed_courses), sorted(remain_required), sorted(remain_electives), self.calcgpa()]
        

#Instructor class holds all of the details of an instructor, names of the courses taught 
# along with the number of students who have taken the course

class Instructor(object):
    header2 = ["CWID", "Name", "Department", "Course", "Students"]

    def __init__(self, name: str, cwid: int, department: str) -> None:
        self._cwid: int = cwid
        self._name: str = name
        self._department: str = department
        self.instructor_course: Dict[str] = defaultdict(int)

    def add_student(self, course: str) -> None:
        self.instructor_course[course] += 1

    def ptable(self) -> None:
        """ Generates each row for the instructor table """
        for course, count in self.instructor_course.items():
            yield [self._cwid, self._name, self._department, course, count]


class Major:
    header3 = ['Major', 'Required Courses', 'Electives']
    grades_given = {'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C'}

    def __init__(self, department : str):
        self._department: str = department
        self._required: Set = set()
        self._electives: Set = set()

    def add_remain_electives(self, course : str, requiredc : str):
        if requiredc == 'Req':
            self._required.add(course)
        elif requiredc == 'Elec':
            self._electives.add(course)
        else:
            raise ValueError("Course not found")

    def courses_left(self, compl_courses : str):
        compl_courses = {course for course, grade in compl_courses.items() if grade in Major.grades_given}
        remain_core_required = self._required - compl_courses
        if self._electives.intersection(compl_courses):
            remain_electives = {}
        else:
            remain_electives = self._electives - compl_courses

        return self._department, compl_courses, remain_core_required, remain_electives

    def ptable(self):
        return [self._department, sorted(self._required), sorted(self._electives)]


#University class has stored details of students and instructors with grades of students

class University(object):
    def __init__(self, directory_name, summ=True):
        self._directory: str = directory_name
        self._student: Dict[str, Student] = dict()
        self._instructor: Dict[str, Instructor] = dict()
        self._majors: Dict[str, Major] = dict()

        try:
            self._get_student(os.path.join(dir, "student.txt"))
            self._get_instructor(os.path.join(dir, "instructor.txt"))
            self._get_majors(os.path.join(dir, "majors.txt"))
            self._get_grades(os.path.join(dir, "grades.txt"))

        except FileNotFoundError:
             print(f"Can't open {directory_name}")
        else:
            if summ:
                print("Student summary table")
                self.student_table()

                print("Instructor summary table")
                self.instructor_table()

                print("Major Summary table")
                self.majors_table()


    def _get_student(self, path : str):
        try:
            student_file: Iterator[Tuple[str]] = file_reader(path, 3, sep='\t', header=True)
            for cwid, name, major in student_file:
                if major not in self._majors:
                    print(f"Student {cwid} '{name}' has unknown major '{major}'")
                else:
                    self._student[cwid] = Student(cwid, name, self._majors[major])
        except ValueError as v:
            print(v)


    def _get_instructor(self, path: str):
        try:
            instructor_file: Iterator[Tuple[str]] = file_reader(path, 3, sep='|', header=True)
            for cwid, name, department in instructor_file:
                self._instructor[cwid] = Instructor(cwid, name, department)
        except ValueError as v:
            print(v)


    def _get_grades(self, path: str):
        try:
            grades_file = file_reader(path, 4, sep='|', header=True)
            for student_cwid, course, grade, instructor_cwid in grades_file:
                if student_cwid in self._student:
                    self._student[student_cwid].add_course(course, grade)
                else:
                    print(f"Grades for student whose CWID not registered {student_cwid}")

                if instructor_cwid in self._instructor:
                    self._instructor[instructor_cwid].add_student(course)
                else:
                    print(f"Grade for unknown instructor {instructor_cwid}")
        except ValueError as v:
            print(v)


    def _get_majors(self, path : str):
        try:
            major_file: Iterator[Tuple[str]] = file_reader(path, 3, sep='\t', header=True)
            for major, flag, course in major_file:
                if major not in self._majors:
                    self._majors[major] = Major(major)
                self._majors[major].add_remain_electives(course, flag)
        except ValueError as v:
            print(v)


    def student_table(self) -> PrettyTable:
        ptable: PrettyTable = PrettyTable(field_names=Student.header1)
        a = list()
        for student in self._student.values():
            ptable.add_row(student.ptable())
            a.append(student.ptable())

        print(ptable)


    def instructor_table(self) -> PrettyTable:
        ptable: PrettyTable = PrettyTable(field_names=Instructor.header2)

        for instructor in self._instructor.values():
            for row in instructor.ptable():
                ptable.add_row(row)
        print(ptable)
    

    def majors_table(self) -> PrettyTable:
        ptable: PrettyTable = PrettyTable(field_names=Major.header3)

        for major in self._majors.values():
            ptable.add_row(major.ptable())
        print(ptable)



#Main fucntion

def main():
    University("/Users/kavyaj/Desktop/810")


if __name__ == '__main__':
    main()
