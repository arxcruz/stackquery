from stackquery.common import gerrit


def main():
    projects = ['openstack/nova', 'stackforge/rally', 'openstack/tempest']
    for project in projects:
        gerrit.process_reviews(project)

if __name__ == '__main__':
    main()
