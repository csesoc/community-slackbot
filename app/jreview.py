from app import db
from app.models import Review
from app.handler import review_confirm

class ReviewClass:
    def __init__(self, author, course):
        self.author = author
        self.course = course
        self.lecturer = ""
        self.when = ""
        self.comments = ""
        self.overall = 0
        self.difficulty = 0
        self.time = 0

reviews = {}

def review_init(user_id, course):
    reviews[user_id] = ReviewClass(user_id, course)

def review_overall(user_id, overall):
    reviews[user_id].overall = overall

def review_difficulty(user_id, difficulty):
    reviews[user_id].difficulty = difficulty

def review_time(user_id, time):
    reviews[user_id].time = time

def review_submit(user_id, values):
    reviews[user_id].lecturer = values['course_lecturer']['course_lecturer']['value']
    reviews[user_id].when = values['course_when']['course_when']['value']
    reviews[user_id].comments = values['course_comments']['course_comments']['value']
    # insert into db
    rev = reviews[user_id]
    rev_db = Review(course=rev.course, review=rev.comments, user_id=rev.author, lecturer=rev.lecturer, term=rev.when, 
                    overall=rev.overall, difficulty=rev.difficulty, time=rev.time, is_approved=False)
    db.session.add(rev_db)
    db.session.commit()
    del reviews[user_id]
    # TODO send confirmation of review
    review_confirm(user_id, rev.course)