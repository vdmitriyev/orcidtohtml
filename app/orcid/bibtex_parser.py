import codecs
import copy
import traceback
from dataclasses import dataclass

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.customization import *
from fuzzywuzzy import fuzz
from jinja2 import Template
from pylatexenc.latex2text import LatexNodes2Text


@dataclass
class BibtexEntry:
    authors: [str]
    title: str
    publishedIn: str
    year: int
    doi: str
    url: str
    bibtex: str

    def random_string(self, size=30):
        import random
        import string

        return "".join(random.choice(string.ascii_letters + string.digits) for i in range(size))

    def bibtex(self):
        pass

    def to_html(self, names_highlight=[], short_name=True, include_js=True):
        """Converts dataclass to HTML"""
        js_code_template = """
            <script type="text/javascript">
                function toggle_visibility(id) {
                   var e = document.getElementById(id);
                   if(e.style.display == 'block')
                      e.style.display = 'none';
                   else
                      e.style.display = 'block';
                }
            </script>"""

        js_code = None
        if include_js:
            js_code = js_code_template

        html_template = """
        {% if jsCode is not none %}
            {{jsCode}}
        {% endif %}
        <!------ begin ------->
            <p>
            {{authors}} <b><i>{{title}}</i></b>, {{year}}, {{journal}}, {{booktitle}}
            &nbsp;
            <a href="{{doi}}">DOI</a>&nbsp;
            <a href="{{url}}">URL</a>&nbsp;
            <a href="#" onclick="toggle_visibility('{{publicationID}}');return false;">BibTeX</a>
            <div id="{{publicationID}}" style="display:none;">
              <pre>
                {{bibtex}}
              </pre>
            </div>
            </p>
        <!------ end ------->
        """

        jinja_tpl = Template(html_template)

        author = ", ".join(self.authors)

        def is_highlightable(item, names_highlight):
            for name in names_highlight:
                if fuzz.ratio(item, name) > 80:
                    return True
            return False

        def shorten_name(name):
            tokens = name.split(" ")
            _short_name = ""
            for i, token in enumerate(tokens):
                if i == 0:
                    _short_name += token[0] + ". "
                else:
                    _short_name += token + " "
            return _short_name[:-1]

        # handles short names
        if short_name:
            author = ""
            for index in range(len(names_highlight)):
                names_highlight[index] = shorten_name(names_highlight[index])
            for item in self.authors:
                _tmp = shorten_name(item)
                if is_highlightable(_tmp, names_highlight):
                    author += f"<b><i>{_tmp}</i></b>, "
                else:
                    author += f"{_tmp}, "
        else:
            author = ""
            for item in self.authors:
                if is_highlightable(item, names_highlight):
                    author += f"<b><i>{item}</i></b>, "
                else:
                    author += f"{item}, "

        return jinja_tpl.render(
            authors=author,
            title=self.title,
            journal=self.publishedIn,
            publicationID=self.random_string(size=15),
            year=self.year,
            doi=self.doi,
            url=self.url,
            bibtex=self.bibtex,
            jsCode=js_code,
        )


def customizations(record):
    """Define a function to customize our entries.
       It takes a record and return this record.
       Use some functions delivered by the library

    :param record: a record
    :returns: -- customized record
    """

    record = homogenize_latex_encoding(record)
    record = type(record)
    record = author(record)
    record = editor(record)
    record = journal(record)
    record = keyword(record)
    record = link(record)
    record = page_double_hyphen(record)
    record = doi(record)
    return record


def clean_text(text):

    LATEX_TO_UMLAUT = {
        '\\"{O}': "Ö",
        '\\"{o}': "ö",
        '\\"{a}': "ä",
        '\\"{A}': "Ä",
        '\\"{U}': "Ü",
        '\\"{u}': "ü",
        "{\\ss}": "ß",
        "{\\'o}": "ó",
        "{\\'e}": "é",
    }

    for _ in LATEX_TO_UMLAUT:
        text = text.replace(_, LATEX_TO_UMLAUT[_])
    return text


def bibtex_to_fullname(name):
    """From bibtex format (LNAME,FNAME) to proper format LNAME FNAME"""

    tokens = name.split(",")
    full_name = name
    if len(tokens) == 2:
        full_name = tokens[1].strip() + " " + tokens[0].strip()
    return full_name


def bibtex_to_obj(bibtex_entry):
    """Convers bibtex obj of the parser into own bibtex object (BibtexEntry)"""

    authors = list()
    # authors.append(bibtex_to_fullname(clean_text(LatexNodes2Text().latex_to_text(bibtex_entry['author']))))
    for author in bibtex_entry["author"]:
        # authors.append(bibtex_to_fullname(clean_text(author)))
        authors.append(bibtex_to_fullname(clean_text(LatexNodes2Text().latex_to_text(author))))

    title = bibtex_entry["title"]
    title = LatexNodes2Text().latex_to_text(title)

    year = "-9999"
    if "year" in bibtex_entry:
        year = bibtex_entry["year"]

    publishedIn = ""
    if "journal" in bibtex_entry:
        publishedIn = bibtex_entry["journal"]["name"]
        # publishedIn = bibtex_entry['journal']

    if "booktitle" in bibtex_entry:
        publishedIn = bibtex_entry["booktitle"]

    doi = ""
    if "doi" in bibtex_entry:
        doi = bibtex_entry["doi"]
        # make doi a link, in case its not yet
        if "http" not in doi:
            doi = f"https://dx.doi.org/{doi}"

    url = ""
    if link in bibtex_entry:
        if len(bibtex_entry["link"] > 0):
            url = bibtex_entry["link"][0]["url"]

    new_entry = copy.deepcopy(bibtex_entry)
    bibtex_raw = bibtex_from_entry(new_entry)

    bibtex_entry = BibtexEntry(
        authors=authors, title=title, year=year, publishedIn=publishedIn, doi=doi, url=url, bibtex=bibtex_raw
    )

    return bibtex_entry


def bibtex_from_entry(entry):
    """A hack that lets to avoid exceptoin that happends when exporting back parsed entry into bibtex
    The problems happends because of the new formats of entry, because bwriter understand only "flatt" (old) one
    """

    writer = BibTexWriter()

    if "author" in entry:
        entry["author"] = " and ".join(entry["author"])

    if "editor" in entry:
        editor_fmt = " and ".join([item["name"] for item in entry["editor"]])
        entry["editor"] = editor_fmt

    if "journal" in entry:
        entry["journal"] = entry["journal"]["name"]

    if "link" in entry:
        if len(entry["link"]) != 0:
            entry["link"] = entry["link"][0]["url"]
        else:
            entry["link"] = ""

    bibtex_raw = writer._entry_to_bibtex(entry)
    return bibtex_raw


def parse_bibtex(bibtex_fname):
    """Parses given bibtex file"""

    try:

        with codecs.open(bibtex_fname, "r", encoding="utf8") as bibtex_file:
            parser = BibTexParser()
            parser.customization = customizations
            bib_database = bibtexparser.load(bibtex_file, parser=parser)
            bibtex_entry = None
            if len(bib_database.entries) > 0:
                bibtex_entry = bibtex_to_obj(bib_database.entries[0])
            return bibtex_entry
    except Exception:
        print(traceback.format_exc())

    return None


if __name__ == "__main__":
    pass
