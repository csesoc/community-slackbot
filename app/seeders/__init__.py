from app.models import *
from app.slack_utils import get_role_id_by_perm_level


def run_role_seeder():
    Roles.query.delete()
    db.session.commit()
    for role in UserRoles.ROLES:
        r = Roles(perm_level=role, title=UserRoles.TITLES[role])
        db.session.add(r)
        db.session.commit()


def run_user_seeder():
    User.query.delete()
    db.session.commit()
    users = [
        {
            "user_id": "U010VHP7BEV",
            "role": UserRoles.NORMAL
        }
    ]
    for user_obj in users:
        user = User(id=user_obj["user_id"], karma=0)
        user_role = UserRole(user_id=user.id,
                             role_id=get_role_id_by_perm_level(user_obj["role"]))
        db.session.add(user)
        db.session.commit()
        db.session.add(user_role)
        db.session.commit()


def run_courses_seeder():
    Courses.query.delete()
    db.session.commit()
    courses = [
        ["1511", "Programming Fundamentals - An introduction to problem-solving via programming, which aims to have students develop proficiency in using a high level programming language. Topics: algorithms, program structures (statements, sequence, selection, iteration, functions), data types (numeric, character), data structures (arrays, tuples, pointers, lists), storage structures (memory, addresses), introduction to analysis of algorithms, testing, code quality, teamwork, and reflective practice. The course includes extensive practical work in labs and programming projects."],
        ["1521", "Computer System Fundamentals - This course provides a programmer's view on how a computer system executes programs, manipulates data and communicates. It enables students to become effective programmers in dealing with issues of performance, portability, and robustness. It is typically taken in the semester after completing COMP1511, but could be delayed and taken later. It serves as a foundation for later courses on networks, operating systems, computer architecture and compilers, where a deeper understanding of systems-level issues is required."],
        ["2521", "Data Structures and Algorithms - The goal of this course is to deepen students' understanding of data structures and algorithms and how these can be employed effectively in the design of software systems. We anticipate that it will generally be taken in the second year of a program, but since its only pre-requisite is COMP1511, is it possible to take it in first year. It is an important course in covering a range of core data structures and algorithms that will be used in context in later courses."]
    ]
    for c in courses:
        course = Courses(course=c[0], msg=c[1])
        db.session.add(course)
        db.session.commit()


def run_seeders():
    run_role_seeder()
    run_user_seeder()
    run_courses_seeder()
