"""
This program is a data repository of courses, students, and instructors.  
The system will be used to help students track their required courses, 
the courses they have successfully completed, their grades,  GPA, etc.  
The system will also be used by faculty advisors to help students to create study plans

Author : Kavya Jadhav
Version : Python 3.7.6
"""

from typing import Dict, Iterator, Tuple, KeysView
from prettytable import PrettyTable
from collections import defaultdict
from HW08_kavyaJ import file_reader
import os

#Student class holds the details of students

class Student(object):
    def __init__(self, cwid: int, name: str, major: str) -> None:
        self._name: str = name
        self._cwid: int = cwid
        self._major: str = major
        self.student_course: Dict[str] = dict()

    def add_course(self, course: str, grade: str) -> None:
        self.student_course[course] = grade

    def reg_course(self) -> KeysView[str]:
        return self.student_course.keys()


#Instructor class holds all of the details of an instructor, names of the courses taught 
# along with the number of students who have taken the course

class Instructor(object):
    def __init__(self, name: str, cwid: int, department: str) -> None:
        self._cwid: int = cwid
        self._name: str = name
        self._department: str = department
        self.instructor_course: Dict[str] = defaultdict(int)

    def add_student(self, course: str) -> None:
        self.instructor_course[course] += 1

    def reg_course(self) -> KeysView[str]:
        return self.instructor_course.keys()

    def get_student_count(self, course: str) -> int:
        return self.instructor_course[course]


#University class has stored details of students and instructors with grades of students

class University(object):
    def __init__(self, directory_name, summ=True):
        self._directory: str = directory_name
        self._student: Dict[str, Student] = dict()
        self._instructor: Dict[str, Instructor] = dict()

        try:
            self._get_student(os.path.join(dir, "student.txt"))
            self._get_instructor(os.path.join(dir, "instructor.txt"))
        except FileNotFoundError:
             print(f"Can't open {directory_name}")
        else:
            if summ:
                print("Student summary table")
                self.student_table()

                print("Instructor summary table")
                self.instructor_table()

    def _get_student(self,path) -> None:
        for cwid, name, major in file_reader(path, 3, sep='\t', header=False):
            self._student[cwid] = Student(cwid, name, major)

    def _get_instructor(self, path) -> None:
        for cwid, name, dept in file_reader(path, 3, sep='\t', header=False):
            self._instructor[cwid] = Instructor(cwid, name, dept)
    
    def _get_grades(self) -> None:
        try:
            grade_file: Iterator[Tuple[str]] = file_reader('grades.txt', 4, sep='\t', header=True)
        
            for student_cwid, course, grade, instructor_cwid in grade_file:
            
                if student_cwid in self._student.keys():
                    self._student[student_cwid].student_course[course] = grade
                
                    if instructor_cwid in self._instructor.keys():
                        self._instructor[instructor_cwid].instructor_course[course] += 1
        except(FileNotFoundError, ValueError) as e:
            print(e)

    def student_table(self) -> PrettyTable:
        print_student_table: PrettyTable = PrettyTable()
        print_student_table.field_names = ["CWID", "Name", "Completed Courses"]
        
        for cwid, student in self._student.items():
            print_student_table.add_row([cwid, student.name, sorted(list(student.student_course.keys()))])
        return print_student_table

    def instructor_table(self) -> PrettyTable:
        print_instructor_table: PrettyTable = PrettyTable()
        print_instructor_table.field_names = ["CWID", "Name", "Dept", "Course", "Students"]
        
        for cwid, instructor in self._instructor.items():
            for course in instructor.instructor_course:
                print_instructor_table.add_row([cwid, instructor.name, instructor.department, course,
                                                instructor.instructor_course[course]])
        return print_instructor_table


#Main fucntion

def main() -> None:
    directory_name: str = '/Users/kavyaj/Desktop/810'
    result = University(directory_name)
    print("Student Summary")
    print(result.student_table())
    print("Instructor Summary")
    print(result.instructor_table())


if __name__ == "__main__":
    main()