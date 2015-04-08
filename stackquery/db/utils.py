from stackquery.db.models import User
from stackquery.db.models import GerritReview
from stackquery.db.models import Project
from stackquery.db.models import Team


def get_users(filter=None, first=False):
    if not filter:
        return User.query.all()
    if first:
        return User.query.filter_by(**filter).first()
    return User.query.filter_by(**filter).all()

def get_users_by_team(team_id):
    team = Team.query.get(int(team_id))
    if team:
        return team.users
    return []


def get_gerrit_reviews(filter=None, first=False):
    if not filter:
        return GerritReview.query.all()
    if first:
        return GerritReview.query.filter_by(**filter).order_by(
            GerritReview.created.desc()).first()
    return GerritReview.query.filter_by(**filter).filter(
        GerritReview.user is not None).order_by(
        GerritReview.created.desc()).all()


def get_projects(filter=None):
    if not filter:
        return Project.query.order_by(Project.name).all()
    return Project.query.filter_by(**filter).order_by(
        Project.name).all()
