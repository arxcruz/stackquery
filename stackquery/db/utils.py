from stackquery.db.models import User
from stackquery.db.models import GerritReview


def get_users(filter=None, first=False):
    if not filter:
        return User.query.all()
    if first:
        return User.query.filter_by(**filter).first()
    return User.query.filter_by(**filter).all()


def get_gerrit_reviews(filter=None, first=False):
    if not filter:
        return GerritReview.query.all()
    if first:
        return GerritReview.query.filter_by(**filter).order_by(
            GerritReview.created.desc()).first()
    return GerritReview.query.filter_by(**filter).filter(
        GerritReview.user is not None).order_by(
        GerritReview.created.desc()).all()
