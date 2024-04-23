# library functions - may be transferred to amilib later
import csv
from collections import defaultdict
from pathlib import Path
import pandas as pd

import lxml.etree as ET
from amilib.file_lib import FileLib
from amilib.xml_lib import XmlLib
from lxml.html import HTMLParser

from climate.ipcc import HTML_WITH_IDS
from climate.un import IPCC

SEP = ";"


class LibTemp:

    @classmethod
    def parse_html_lxml(cls, inputx):

        try:
            html_tree = ET.parse(inputx, HTMLParser())
        except Exception as e:
            raise e
        return html_tree

    @classmethod
    def get_xml_values(cls, term_file, xpath):
        xml_tree = ET.parse(term_file)
        phrases = xml_tree.xpath(xpath)
        return phrases

    @classmethod
    def get_ipcc_dir(cls):
        ipcc_dir = Path(FileLib.get_home(), "projects", "ipcc")
        return ipcc_dir

    @classmethod
    def get_query_dir(cls):
        ipcc_dir = cls.get_ipcc_dir()
        query_dir = Path(ipcc_dir, "ar6", "test", "ar6", "query")
        return query_dir

    @classmethod
    def search_phrases_into_html_lists(cls, country_file, debug, indir, outfile):
        globstr = f"{str(indir)}/**/{HTML_WITH_IDS}.html"
        infiles = FileLib.posix_glob(globstr, recursive=True)
        with open(country_file, "r") as f:
            phrases = [phrase.strip() for phrase in (f.readlines())]
        html1 = IPCC.search_inputfiles_with_phrases_into_html_tree_and_file(infiles, phrases=phrases, outfile=outfile,
                                                                            debug=debug)
        return html1

    @classmethod
    def _make_country_filenames(cls, query, infile=None, topdir=None):
        # if not infile or not topdir:
        #     raise ValueError("must give infile and topdir")
        if not topdir:
            topdir = LibTemp.get_ipcc_dir()
        indir = topdir
        assert indir.exists(), f"{indir} should exist"
        outfile = Path(indir, "ar6", "query", f"{query}.html")
        outcsv = Path(indir, "ar6", "query", f"{query}.csv")
        return infile, indir, outfile, outcsv

    @classmethod
    def build_list_dict(cls, labels, outcsv, listfile=None, html_list=None, corpus=None):

        if html_list is None:
            html_list = LibTemp.parse_html_lxml(listfile)
        hits = html_list.xpath("/html/body/ul/li")
        para_dict = defaultdict(list)
        for hit in hits:
            cls.get_para_content_from_anchor_id(corpus, hit, para_dict)
        corpus = LibTemp.get_ipcc_dir()
        cls.write_csv_file(labels, outcsv, para_dict, corpus=corpus)
        dataframe = pd.read_csv(outcsv)
        return dataframe

    @classmethod
    def get_para_content_from_anchor_id(cls, corpus, hit, para_dict):


        hit_names = hit.xpath("./p/text()")
        if len(hit_names) > 0:
            for aa in hit.xpath("./ul/li/a"):

                key = aa.text
                para_dict[key].append(hit_names[0])

    @classmethod
    def get_para_file_by_id(cls, key, para_file):
        para_string = "??"
        if para_file.exists():
            try:
                para_html = LibTemp.parse_html_lxml(para_file)
                id = key.split("#")[1]
                paras = para_html.xpath(f"//*[@id='{id}']")
                if len(paras) == 1:
                    para = paras[0]
                    para_string = XmlLib.get_text(para)
                elif len(paras) == 0:
                    para_string = f"NO PARA FOR {id}"

            except Exception as e:
                print(f"****cannot read {para_file}, {e}****")
                para_string = "EXC"
        return para_string

    @classmethod
    def write_csv_file(cls, labels, outcsv, para_dict, corpus=None):
        para_text_dict = dict()

        with open(outcsv, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(labels)
            for para_key in para_dict:
                para_data_list = para_dict.get(para_key)
                if type(para_data_list) is list:
                    para_data_list = SEP.join(para_data_list)
                para_file = cls.get_html_with_id_filename(corpus, para_key)
                if para_file is None or not Path(para_file).exists():
                    print(f"Cannot find file {para_key}")
                    para_text = "??"
                else:
                    # para_text = LibTemp.parse_html_lxml(para_file)
                    para_text = cls.get_para_file_by_id(para_key, para_file)

                csvwriter.writerow([para_key, para_data_list, para_text])
            print(f"wrote CSV {outcsv}")

    @classmethod
    def get_html_with_id_filename(cls, corpus, key):
        keys = key.split("#")
        # print(f"key {key} {corpus}")
        filename = Path(corpus, f"{keys[0]}", "html_with_ids.html")

        return filename

    @classmethod
    def check_output_tree(cls, output, expected=None, xpath=None):
        assert xpath, f"must give xpath"
        assert output, f"output cannot be None"
        html_tree = ET.parse(output)
        assert html_tree is not None, f"html_tree is None"
        if expected:
            pp = len(html_tree.xpath(xpath))
            if type(expected) is list and len(expected) == 2:
                assert expected[0] <= pp <= expected[1], f"found {pp} elements in {output}, expected {expected}"
            else:
                assert pp == expected, f"found {pp} elements in {output}"

    @classmethod
    def read_lines(cls, file):
        """reads indivual lines from file
        convenience
        :param: file
        :return: list of strings (including empty list)  or None if not suitable file
        """

        if not file or not file.exists():
            return None
        p = Path(file)
        lines = p.read_text().splitlines()
        return lines

    @classmethod
    def extract_phrases(self, phrase_file, suffix, xpath):
        phrases = None
        if suffix == ".xml" and xpath:
            phrases = LibTemp.get_xml_values(phrase_file, xpath)
        else:
            phrases = LibTemp.read_lines(phrase_file)
        return phrases




if __name__ == "__main__":
    print("running main")
