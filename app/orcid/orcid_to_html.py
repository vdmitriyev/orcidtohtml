import argparse
import codecs
import json
import os
import traceback
import uuid
from datetime import datetime, timezone

import requests
from werkzeug.utils import secure_filename

from .bibtex_parser import parse_bibtex


def generate_job_id() -> str:
    """
    Generates a string representing the current datetime in 'YYYYMMDD-HHMM' format
    and appends a UUID to it.

    Returns:
      str: A string in the format 'YYYYMMDD-HHMM-UUID'.
    """

    now_utc = datetime.now(timezone.utc)
    formatted_datetime = now_utc.strftime("%Y%m%d-%H%M")
    unique_id = str(uuid.uuid4())[:8]

    return f"{formatted_datetime}-{unique_id}"


def change_logging_level():
    """Changes logging level of some libraries not to make output too verbose"""
    import logging.config

    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("bibtexparser.bparser").setLevel(logging.WARNING)
    logging.getLogger("bibtexparser.customization").setLevel(logging.WARNING)


def process_orcid(orcid_id=None, name=None, test_mode=False, keep_files=False, job_id=None):
    """Process items of a given orcid_id

    orcid_id    -> ORCID number
    name        -> name to highlight / use as folder
    test_mode   -> only one run + keep some results as files
    keep_files  -> keep some results as files
    """

    change_logging_level()
    if job_id is None:
        job_id = generate_job_id()

    if orcid_id is None:
        print("orcid_id cannot be None")
        return

    if test_mode:
        keep_files = True

    if not os.path.exists("data"):
        os.makedirs("data")

    base_dir = os.path.join("data", secure_filename(name))
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    resp = requests.get(f"http://pub.orcid.org/{orcid_id}/works", headers={"Accept": "application/orcid+json"})

    results = resp.json()

    if keep_files:
        orcid_output_as_json = os.path.join(base_dir, f"{job_id}_orcid-output.json")
        with open(orcid_output_as_json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

    entries, errors = [], []
    for i, item in enumerate(results["group"]):
        try:
            is_error = False
            print(f"Processing: {item['work-summary'][0]['path']}")
            path_url = item["work-summary"][0]["path"]

            # get specific work item / publication
            resp = requests.get(f"http://pub.orcid.org/{path_url}", headers={"Accept": "application/orcid+json"})
            results = resp.json()

            if keep_files:
                output_as_json_file = os.path.join(base_dir, f"{job_id}_{i}_output.json")
                with open(output_as_json_file, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=4, ensure_ascii=False)

            citation = results["citation"]
            if citation is not None:
                if "citation-type" in citation:
                    if citation["citation-type"].lower() == "bibtex":

                        bibtex_original = citation["citation-value"]
                        bibtex_path = os.path.join(base_dir, f"{job_id}_{i}_output.bib")
                        bibtex_as_html_path = os.path.join(base_dir, f"{job_id}_{i}_output.html")

                        with open(bibtex_path, "w", encoding="utf-8") as f:
                            f.write(bibtex_original)

                        bibtex_output = parse_bibtex(bibtex_path, bibtex_original)

                        if bibtex_output is not None:
                            entries.append(bibtex_output)
                            if keep_files:
                                with open(bibtex_as_html_path, "w", encoding="utf-8") as f:
                                    f.write(bibtex_output.to_html(names_highlight=[name], short_name=False))
                        else:
                            is_error = True

            else:
                is_error = True

            if is_error:
                try:
                    pub_title = item["work-summary"][0]["title"]["title"]["value"]
                    message = f'Empty or wrong BibTeX was found: "{pub_title}"'
                    print(f"message: {message};\npath_url: {path_url}")
                    errors.append({"message": message, "path_url": path_url})
                except Exception as ex:
                    print(traceback.format_exc())
                    errors.append({"message": f"Exception: {ex}", "path_url": None})

            if test_mode:
                break

        except Exception as ex:
            print(traceback.format_exc())
            errors.append({"message": f"Exception: {ex}", "path_url": None})

    return entries, errors


def parse_via_cli(fname: str = None, orcid: str = None):
    """Parses ORCID IDs from a file or a single provided ID."""

    fname_orcid_ids = fname if fname else "orcid_ids_list.json"
    orcid_ids = {}

    if orcid:
        print(f"Processing single ORCID provided via CLI: {orcid}")
        process_orcid(orcid_id=orcid, name="single user")
        return

    try:
        with open(fname_orcid_ids, "r", encoding="utf8") as f_json:
            orcid_ids = json.load(f_json)
    except FileNotFoundError:
        print(f"Error: The file '{fname_orcid_ids}' was not found.")
        return

    print(f"List of orcid IDs: {orcid_ids}")

    for key in orcid_ids:
        print(f"Processing orcid of the author: {key}")
        process_orcid(orcid_id=orcid_ids[key], name=key)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process ORCID IDs from a file or direct input.")

    parser.add_argument("--file", type=str, help="Path to the JSON file containing ORCID IDs")
    parser.add_argument("--orcid", type=str, help="A single ORCID ID to process directly")

    args = parser.parse_args()
    parse_via_cli(fname=args.file, orcid=args.orcid)
