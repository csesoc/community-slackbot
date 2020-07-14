from app.models import *


def run_user_seeder():
    pass


def run_courses_seeder():
    Courses.query.delete()
    db.session.commit()
    courses = [
        ["1511", "1511"],
        ["1521", "1521"],
        ["2521", "2521"]
    ]
    for c in courses:
        course = Courses(course=c[0], msg=c[1])
        db.session.add(course)
        db.session.commit()


def run_seeders():
    run_user_seeder()
    run_courses_seeder()
