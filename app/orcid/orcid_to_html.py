import os
import json
import codecs
import requests
import traceback
from .bibtex_parser import BibtexEntry, parse_bibtex

from werkzeug.utils import secure_filename

def change_logging_level():
    ''' Changes logging level of some libraries not to make output too verbose'''
    import logging.config
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("bibtexparser.bparser").setLevel(logging.WARNING)
    logging.getLogger("bibtexparser.customization").setLevel(logging.WARNING)

def process_orcid(orcid_id = None, name = None, test_mode = False, keep_files = False):
    ''' Process items of a given orcid_id

        orcid_id    -> ORCID number
        name        -> name to highlight / use as folder
        test_mode   -> only one run + keep some results as files
        keep_files  -> keep some results as files
    '''

    change_logging_level()

    if orcid_id is None:
        print ('orcid_id cannot be None')
        return

    if test_mode:
        keep_files = True

    if not os.path.exists('data'):
        os.makedirs('data')

    base_dir = os.path.join('data', secure_filename(name))
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    resp = requests.get(f"http://pub.orcid.org/{orcid_id}/works", headers={'Accept':'application/orcid+json'})

    results = resp.json()

    if keep_files:
        with codecs.open(os.path.join(base_dir, 'orcid-output.json'), 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

    entries, errors = [], []
    for i, item in enumerate(results['group']):
        try:
            is_error = False
            print(f"Processing: {item['work-summary'][0]['path']}")
            path_url = item['work-summary'][0]['path']

            # get specific work item / publication
            resp = requests.get(f"http://pub.orcid.org/{path_url}", headers={'Accept':'application/orcid+json'})
            results = resp.json()

            if keep_files:
                with codecs.open(os.path.join(base_dir, f'{i}_output.json'), 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=4, ensure_ascii=False)

            citation = results['citation']
            if citation is not None:
                if 'citation-type' in citation:
                    if citation['citation-type'].lower() == 'bibtex':
                        with codecs.open(os.path.join(base_dir, f'{i}_output.bib'), 'w', encoding='utf-8') as f:
                           f.write(citation['citation-value'])

                        bibtex_output = parse_bibtex(os.path.join(base_dir, f'{i}_output.bib'))
                        if bibtex_output is not None:
                            entries.append(bibtex_output)
                            if keep_files:
                                with codecs.open(os.path.join(base_dir, f'{i}_output.html'), 'w', encoding='utf-8') as f:
                                    f.write(bibtex_output.to_html(names_highlight = [name], short_name = False))
                        else:
                            is_error = True

            else:
                is_error = True

            if is_error:
                try:
                    pub_title = item['work-summary'][0]['title']['title']['value']
                    message = f'Empty or wrong BibTeX was found: "{pub_title}"'
                    print(message)
                    print(f'path_url: {path_url}')
                    errors.append({'message' : message, 'path_url' : path_url})
                except Exception as ex:
                    print (traceback.format_exc())
                    errors.append({'message' : f'Exception: {ex}', 'path_url' : None})

            if test_mode:
                break
        except Exception as ex:
            print (traceback.format_exc())
            errors.append({'message' : f'Exception: {ex}', 'path_url' : None})
    return entries, errors

def main():
    ''' '''

    fname_orcid_ids = 'orcid_ids_list.json'
    orcid_ids = {}
    with codecs.open(fname_orcid_ids, 'r', encoding='utf8') as f_json:
        orcid_ids = json.load(f_json)

    print(orcid_ids)

    for key in orcid_ids:
        print(f'Processing orcid of the author: {key}')
        process_orcid(orcid_id = orcid_ids[key], name = key)

if __name__ == '__main__':
    main()
