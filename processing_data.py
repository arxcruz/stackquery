import stackquery.libs.gerrit as gerrit
import stackquery.libs.utils as utils


def main():
    projects = utils.get_projects_being_used()
    for project in projects:
        gerrit.process_reviews(project)

if __name__ == '__main__':
    main()
