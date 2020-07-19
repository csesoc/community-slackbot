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
        ["1511", "1511"],
        ["1521", "1521"],
        ["2521", "2521"]
    ]
    for c in courses:
        course = Courses(course=c[0], msg=c[1])
        db.session.add(course)
        db.session.commit()


def run_seeders():
    run_role_seeder()
    run_user_seeder()
    run_courses_seeder()
