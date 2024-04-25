# library functions - may be transferred to amilib later
import csv
from collections import defaultdict
from pathlib import Path
import pandas as pd

import lxml.etree as ET
from amilib.file_lib import FileLib
from amilib.xml_lib import XmlLib, HtmlLib
from lxml.html import HTMLParser



SEP = ";"
HTML_WITH_IDS = "html_with_ids"


class LibTemp:

    @classmethod
    def parse_html_lxml(cls, inputx):
        LibTemp.assert_well_formed(inputx)
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
    def search_phrases_into_html_lists(cls, phrase_file, debug, indir, outfile, html_stem="html_with_ids"):
        assert phrase_file is not None, f"phrase_file must not be None"
        assert Path(phrase_file).exists(), f"phrase_file {phrase_file} must exist"
        globstr = f"{str(indir)}/**/{html_stem}.html"
        infiles = FileLib.posix_glob(globstr, recursive=True)
        with open(phrase_file, "r") as f:
            phrases = [phrase.strip() for phrase in (f.readlines())]
        html1 = cls.search_inputfiles_with_phrases_into_html_tree_and_file(infiles, phrases=phrases, outfile=outfile,
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

        print(f"analysing {listfile}")
        if html_list is None:
            LibTemp.assert_well_formed(listfile)
            html_list = LibTemp.parse_html_lxml(listfile)
        hits = html_list.xpath("/html/body/ul/li")
        para_dict = defaultdict(list)
        for hit in hits:
            cls.get_para_content_from_anchor_id(corpus, hit, para_dict)
        if corpus is None:
            raise ValueError("no corpus given")
        cls.write_csv_file(labels, outcsv, para_dict, corpus=corpus, debug=True)
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
    def write_csv_file(cls, labels, outcsv, para_dict, corpus=None, debug=True):
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
            if debug:
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

    @classmethod
    def assert_lxml_element_tree(cls, html_tree):
        assert html_tree is not None, f"html tree must not be None"
        assert (t := type(html_tree)) is ET._ElementTree, f"html_tree must be of type {ET._ElementTree}, found {t}"

    @classmethod
    def assert_has_paras(cls, html_tree, file=None):
        if file:
            html_tree = LibTemp.parse_html_lxml(file)
        body = cls.assert_has_body(html_tree)
        paras = body.xpath(".//p")
        assert len(paras) > 0, f"body must heve descendant paras"
        return paras

    @classmethod
    def assert_has_body(cls, html_tree, children=True):
        """convenience
        asserts html_tree has body and optionally children
        :param html_tree: tree to exist
        :param children:children must exists (Default False)
        :return body:
        """

        body = HtmlLib.get_body(html_tree)
        assert body is not None, f"html_tree must have body"
        if children:
            assert len(body.xpath("./*")) > 0, f"body must have3 children"
        return body

    @classmethod
    def add_hit_with_filename_and_para_id(cls, all_dict, hit_dict, infile, para_phrase_dict):
        """adds non-empty hits in hit_dict and all to all_dict
        :param all_dict
        """
        item_paras = [item for item in para_phrase_dict.items() if len(item[1]) > 0]
        if len(item_paras) > 0:
            all_dict[infile] = para_phrase_dict
            for para_id, hits in para_phrase_dict.items():
                for hit in hits:
                    # TODO should write file with slashes (on Windows we get %5C)
                    infile_s = f"{infile}"
                    infile_s = infile_s.replace("\\", "/")
                    infile_s = infile_s.replace("%5C", "/")
                    url = f"{infile_s}#{para_id}"
                    hit_dict[hit].append(url)

    @classmethod
    def search_inputfiles_with_phrases_into_html_tree_and_file(cls, infiles, phrases=None, outfile=None, xpath=None, omit=None, debug=False):
        all_paras = []
        all_dict = dict()
        hit_dict = defaultdict(list)
        if not omit:
            omit = ".*#references_.*"
        if type(phrases) is not list:
            phrases = [phrases]
        for infile in infiles:
            assert Path(infile).exists(), f"{infile} does not exist"
            html_tree = ET.parse(str(infile), HTMLParser())
            LibTemp.assert_has_paras(html_tree)
            paras = HtmlLib.find_paras_with_ids(html_tree, xpath=xpath)
            all_paras.extend(paras)

            # this does the search
            para_phrase_dict = HtmlLib.create_para_ohrase_dict(paras, phrases)
            print(f"{para_phrase_dict}")
            if len(para_phrase_dict) > 0:
                if debug:
                    print(f"para_phrase_dict {para_phrase_dict}")
                cls.add_hit_with_filename_and_para_id(all_dict, hit_dict, infile, para_phrase_dict)
        if debug:
            print(f"para count~: {len(all_paras)}")
        outfile = Path(outfile)
        outfile.parent.mkdir(exist_ok=True, parents=True)
        print(f"keys: {hit_dict.keys()}")
        html1 = cls.create_html_from_hit_dict(hit_dict, omit=omit)
        if outfile:
            with open(outfile, "w") as f:
                if debug:
                    print(f" hitdict {hit_dict}")
                HtmlLib.write_html_file(html1, outfile, debug=True)
        return html1

    @classmethod
    def create_html_from_hit_dict(cls, hit_dict, omit=None):
        html = HtmlLib.create_html_with_empty_head_body()
        body = HtmlLib.get_body(html)
        ul = ET.SubElement(body, "ul")
        for term, hits in hit_dict.items():
            li = ET.SubElement(ul, "li")
            p = ET.SubElement(li, "p")
            p.text = term
            ul1 = ET.SubElement(li, "ul")
            for hit in hits:
                if omit:
                    match = re.match(omit, hit)
                    if match:
                        continue # skip
                # TODO manage hits with Paths
                # on windows some hits have "%5C' instead of "/"
                hit = str(hit).replace("%5C", "/")
                li1 = ET.SubElement(ul1, "li")
                a = ET.SubElement(li1, "a")
                a.text = hit.replace("/html_with_ids.html", "")
                ss = "ipcc/"
                try:
                    idx = a.text.index(ss)
                except Exception as e:
                    print(f"cannot find substring {ss} in {a}")
                    continue
                a.text = a.text[idx + len(ss):]
                a.attrib["href"] = hit
        return html

    @classmethod
    def assert_well_formed(cls, inputx, parser=HTMLParser):

        assert inputx is not None, "input must not be null"
        assert Path(inputx).exists()
        xtree = None
        if parser is not None:
            xtree = ET.parse(inputx, parser=parser())
        else:
            xtree = ET.parse()
        return xtree

    @classmethod
    def get_test_dir(cls):
        ipcc_dir = cls.get_ipcc_dir()
        return Path(ipcc_dir, "ar6", "test")


if __name__ == "__main__":
    print("running main")
