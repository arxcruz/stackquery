from flask import Blueprint
from flask import render_template
from flask import request

from stackquery.common import gerrit

import datetime

gerrit_report = Blueprint('gerrit_report', __name__,
                          url_prefix='/gerrit',
                          template_folder='templates')


@gerrit_report.route('/', methods=['GET', 'POST'])
def gerrit_report_index():
    if request.method == 'POST':
        filters = request.form.get('filter')
        filters += ' status:MERGED'
        search_filter = gerrit.get_filters(filters)
        error = None
        before = datetime.datetime.now()
        try:
            releases = gerrit.get_all_reviews_from_database(
                filters=search_filter)
        except Exception as e:
            error = 'Invalid query: %s' % e.message
            releases = None
        after = datetime.datetime.now()
        seconds = abs(after - before).seconds
        return render_template('gerrit/index.html',
                               releases=releases, seconds=seconds,
                               error=error)

    return render_template('gerrit/index.html')
