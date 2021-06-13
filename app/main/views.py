from flask import render_template, redirect, url_for, abort, flash, request,\
                  current_app, make_response, escape, Markup, jsonify, send_from_directory, send_file

from . import main
from .forms import OrcidForm

@main.route('/')
@main.route('/index')
def index():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/orcid2html', methods=['GET', 'POST'])
def orcid2html():
    ''' Processes given OrcidID into HTML'''

    name = request.cookies.get('name', None)
    orcid_id = request.cookies.get('orcidID', None)
    message = None
    bibtex_as_html = None
    form = OrcidForm()
    if form.validate_on_submit():

        from ..orcid.orcid_to_html import process_orcid
        current_app.logger.info(f'Process orcid id: {form.orcidID.data}')
        try:
            import logging.config
            logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
            logging.getLogger("bibtexparser.customization").setLevel(logging.WARNING)

            entires, errors = process_orcid(orcid_id = form.orcidID.data, 
                                            name = form.name.data,
                                            test_mode = False)
            from operator import attrgetter
            entires.sort(key = attrgetter('year'), reverse = True)
            bibtex_as_html = ''
            for index, entry in enumerate(entires):
                if index == 0:
                    bibtex_as_html += entry.to_html(names_highlight=[name], short_name = False, include_js = True)
                else:
                    bibtex_as_html += entry.to_html(names_highlight=[name], short_name = False, include_js = False)

            if len(errors) > 0:
                message = ''
                for error in errors:
                    message += Markup(f'<i>{error["message"]}</i></br>')

        except Exception as ex:
            current_app.logger.error(ex, exc_info=True)
            if message is None: message = ''
            message += Markup(f'[e] {ex}')

    if form.name.data is None and name is not None:
        form.name.data = name

    if form.orcidID.data is None and orcid_id is not None:
        form.orcidID.data = orcid_id

    resp = make_response(render_template('orcid2html.html', form=form, 
                                                            message = message, 
                                                            bibtexAsHTML = bibtex_as_html,
                                                            bibtexAsHTMLPreview = Markup(bibtex_as_html)
                                        ))
    if form.name.data is not None:
        resp.set_cookie('name', form.name.data)

    if form.orcidID.data is not None:
        resp.set_cookie('orcidID', form.orcidID.data)

    return resp

@main.route('/bibtex2html')
def bibtex2html():
    return render_template('bibtex2html.html')
