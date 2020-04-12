"""
This program is a data repository of courses, students, and instructors.  
The system will be used to help students track their required courses, 
the courses they have successfully completed, their grades,  GPA, etc.  
The system will also be used by faculty advisors to help students to create study plans

Author : Kavya Jadhav
Version : Python 3.7.6
"""

import unittest
from typing import List
from Student_Repository_kavyaJ import University, Student, Instructor


class TestUniversity(unittest.TestCase):
    def test_student_table(self):
        Columbia = University('/Users/kavyaj/Desktop/810')
        Columbia._get_student()
        Columbia._get_instructor()
        Columbia._get_grades()

        expected_result: List = list()
        for cwid, student in Columbia._student.items():
            expected_result.append((cwid, student._name, list(student.student_course.keys())))

        self.assertEqual(expected_result, [('10115', 'Wyatt, X', ['SSW 567', 'SSW 564', 'SSW 687', 'CS 545']),
                               ('10172', 'Forbes, I', ['SSW 555', 'SSW 567']),
                               ('10175', 'Erickson, D', ['SSW 567', 'SSW 564', 'SSW 687']),
                               ('10183', 'Chapman, O', ['SSW 689']),
                               ('11399', 'Cordova, I', ['SSW 540']),
                               ('11461', 'Wright, U', ['SYS 800', 'SYS 750', 'SYS 611']),
                               ('11658', 'Kelly, P', ['SSW 540']),
                               ('11714', 'Morton, A', ['SYS 611', 'SYS 645']),
                               ('11788', 'Fuller, E', ['SSW 540'])])

    def test_instructor_table(self):
        Yale = University('/Users/kavyaj/Desktop/810')
        Yale._get_student()
        Yale._get_instructor()
        Yale._get_grades()

        expected_result: List = list()
        for cwid, instructor in Yale._instructor.items():
            for course, students in instructor.instructor_courses.items():
                expected_result.append((cwid, instructor._name, instructor._department, course, students))

        self.assertEqual(expected_result, [('98764', '98764', 'SFEN', 'SSW 564', 2),
                               ('98764', '98764', 'SFEN', 'SSW 687', 2),
                               ('98764', '98764', 'SFEN', 'CS 545', 1),
                               ('98763', '98763', 'SFEN', 'SSW 555', 1),
                               ('98763', '98763', 'SFEN', 'SSW 689', 1),
                               ('98760', '98760', 'SYEN', 'SYS 800', 1),
                               ('98760', '98760', 'SYEN', 'SYS 750', 1),
                               ('98760', '98760', 'SYEN', 'SYS 611', 2),
                               ('98760', '98760', 'SYEN', 'SYS 645', 1)])


if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)

if __name__ == '__main__':
    unittest.main()