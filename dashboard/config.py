from oslo.config import cfg

OPTS = [
    cfg.BoolOpt('debug', default=True,
                help='Run in debug mode?'),
    cfg.StrOpt('sources-root', default='/home/acruz/local',
               help='The folder that holds all project sources to analyze'),
    cfg.StrOpt('listen-host', default='127.0.0.1',
               help='The address stackquery-dashboard listens on'),
    cfg.IntOpt('listen-port', default=8080,
               help='The port stackquery-dashboard listens on'),
    cfg.StrOpt('review-uri', default='https://review.openstack.org',
               help='URI of review system'),
    cfg.StrOpt('git-base-uri', default='git://git.openstack.org',
               help='git base location'),
    cfg.StrOpt('ssh-key-filename', default='/home/dashboard/.ssh/id_rsa',
               help='SSH key for gerrit review system access'),
    cfg.StrOpt('ssh-username', default='dashboard',
               help='SSH username for gerrit review system access'),
    cfg.StrOpt('data-json', default='/home/acruz/Projetos/pessoais/stackquery-dashboard/etc/default_data.json',
               help='Default file containing json data'),
]
