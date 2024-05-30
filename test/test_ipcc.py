import logging

import lxml.etree as ET
from climate.amix import AMIClimate, REPO_DIR
from climate.ipcc import IPCCWordpress, IPCCGatsby, IPCCChapter, IP_WG1, IPCCArgs, IP_WG2, IP_WG3
import csv
import os
from pathlib import Path
import unittest
import requests

from amilib.ami_pdf_libs import AmiPDFPlumber, AmiPlumberJson
from amilib.ami_html import HtmlUtil
from amilib.file_lib import FileLib
from amilib.html_generator import HtmlGenerator
from amilib.xml_lib import HtmlLib
from lxml.html import HTMLParser

from climate.un import DECISION_SESS_RE, MARKUP_DICT, INLINE_DICT, UNFCCC, UNFCCCArgs, IPCC, HTML_WITH_IDS_HTML, \
    AR6_URL, TS, GATSBY_RAW, LR, SPM, ANN_IDX, \
    GATSBY, DE_GATSBY, HTML_WITH_IDS, ID_LIST, WORDPRESS, DE_WORDPRESS, MANUAL, PARA_LIST
# from pyamihtmlx.util import Util
# from pyamihtmlx.xml_lib import HtmlLib
#
from test.resources import Resources
from test.test_all import AmiAnyTest


# from test.test_all import AmiAnyTest

# from test.test_headless import SC_TEST_DIR
#
UNFCCC_DIR = Path(Resources.TEST_RESOURCES_DIR, "unfccc")
UNFCCC_TEMP_DIR = Path(Resources.TEMP_DIR, "unfccc")
UNFCCC_TEMP_DOC_DIR = Path(UNFCCC_TEMP_DIR, "unfcccdocuments1")
#
MAXPDF = 3
#
# OMIT_LONG = True  # omit long tests
#
# #
TEST_DIR = Path(REPO_DIR, "test")
TEMP_DIR = Path(REPO_DIR, "temp")
#
IPCC_TOP = Path(TEST_DIR, "resources", "ipcc", "cleaned_content")
# assert IPCC_TOP.exists(), f"{IPCC_TOP} should exist"
#
QUERIES_DIR = Path(TEMP_DIR, "queries")
# assert QUERIES_DIR.exists(), f"{QUERIES_DIR} should exist"
#
IPCC_DICT = {
    "_IPCC_REPORTS": IPCC_TOP,
    "_IPCC_QUERIES": QUERIES_DIR,
}
#
CLEANED_CONTENT = 'cleaned_content'
SYR = 'syr'
SYR_LR = 'longer-report'
IPCC_DIR = 'ipcc'
#

OUT_DIR_TOP = Path(FileLib.get_home(), "workspace")

# input
IPCC_URL = "https://www.ipcc.ch/"
AR6_URL = IPCC_URL + "report/ar6/"
SYR_URL = AR6_URL + "syr/"
WG1_URL = AR6_URL + "wg1/"
WG2_URL = AR6_URL + "wg2/"
WG3_URL = AR6_URL + "wg3/"

# SC_TEST_DIR = Path(OUT_DIR_TOP, "ipcc", "ar6", "test")

logger = FileLib.get_logger(__file__)
logger.setLevel(logging.INFO)

class TestIPCC(AmiAnyTest):

    @unittest.skipUnless(True or AmiAnyTest.run_long(), "run occasionally, 1 min")
    def test_pdfplumber_doublecol_create_pages_for_WGs_HACKATHON(self):
        """
        creates AmiPDFPlumber and reads double-column pdf and debugs
        This is also an integration/project test
        """

        report_names = [
            # "SYR_LR",
            # "SYR_SPM",
            # "SR15_SPM",
            # "SR15_TS",
            # "SRCCL_SPM",
            # "SRCCL_TS",
            # "SROCC_SPM",
            # "SROCC_TS",
            # "WG1_SPM",
            # "WG1_TS",
            # "WG2_SPM",
            # "WG2_TS",
            # "WG3_SPM",
            # "WG3_TS",
            "WG3_CHAP08",
        ]
        # this needs mending
        for report_name in report_names:
            report_dict = self.get_report_dict_from_resources(report_name)
            HtmlGenerator.get_pdf_and_parse_to_html(report_dict, report_name)

    def get_report_dict_from_resources(self, report_name):
        return Resources.WG_REPORTS[report_name]

    def test_html_commands(self):
        """NYI"""
        print(f"directories NYI")
        return

        in_dir, session_dir, top_out_dir = self._make_query()
        outdir =  TEMP_DIR
        AMIClimate().run_command(
            ['IPCC', '--input', "WG3_CHAP08", '--outdir', str(top_out_dir),
             '--operation', UNFCCCArgs.PIPELINE])

    @unittest.skipUnless(AmiAnyTest.run_long(), "run occasionally, 1 min")
    def test_html_commands_shadow(self):
        """shadows above test - mainly development"""
        report_name = "WG3_CHAP08"
        report_dict = self.get_report_dict_from_resources(report_name)
        print(f"report_dict {report_dict}")
        outdir = report_dict.get("outdir")
        print(f"outdir {outdir}")
        HtmlGenerator.get_pdf_and_parse_to_html(report_dict, report_name)

    @unittest.skip("NYI")
    def test_clean_pdf_html_SYR_LR(self):
        """fails as there are no tables! (they are all bitmaps)"""
        inpdfs = [
            Path(Resources.TEST_IPCC_SROCC, "ts", "fulltext.pdf"),
            Path(Resources.TEST_IPCC_LONGER_REPORT, "fulltext.pdf"),
        ]
        for inpdf in inpdfs:
            pass

    def test_extract_target_section_ids_from_page(self):
        """The IPCC report and many others have hierarchical IDs for sections
        These are output in divs and spans
        test/resources/ipcc/wg2/spm/page_9.html
        e.g. <div>
        """
        input_html_path = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "wg2", "spm", "page_9.html")
        assert input_html_path.exists()
        id_regex = r"^([A-F](?:.[1-9])*)\s+.*"

        spanlist = HtmlLib.extract_ids_from_html_page(input_html_path, regex_str=id_regex, debug=False)
        assert len(spanlist) == 4

    def test_extract_target_sections_from_pages(self):
        """The IPCC report and many others have hierarchical IDs for sections
        These are output in divs and spans
        test/resources/ipcc/wg2/spm/page_9.html
        e.g. <div>
        """
        id_regex = r"^([A-F](?:.[1-9])*)\s+.*"
        html_dir = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "wg2", "spm", "pages")
        os.chdir(html_dir)
        total_spanlist = []
        files = FileLib.posix_glob("*.html")
        for i in range(len(files)):
            file = f"page_{i + 1}.html"
            try:
                spanlist = HtmlLib.extract_ids_from_html_page(file, regex_str=id_regex, debug=False)
            except Exception as e:
                print(f"cannot read {file} because {e}")
                continue
            total_spanlist.append((file, spanlist))
        output_dir = Path(Resources.TEMP_DIR, "html", "ipcc", "wg2", "spm", "pages")
        output_dir.mkdir(exist_ok=True, parents=True)
        section_file = Path(output_dir, 'sections.csv')
        with open(section_file, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, quotechar='|')
            csvwriter.writerow(["qid", "Len", "P1"])
            for file, spanlist in total_spanlist:
                if spanlist:
                    print(f"========= {file} ==========")
                    for span in spanlist:
                        text_ = span.text[:50].strip()
                        qid = '\"' + text_.split()[0] + '\"'
                        # print(f" [{qid}]")
                        text = text_.split()[1] if len(text_) > 8 else span.xpath("following::span")[0].text
                        print(f"{qid}, {text}")
                        csvwriter.writerow(["", qid, "Q18"])
                        # csvlist.append(["", qid, "P18"])
        print(f" wrote {section_file}")
        assert section_file.exists()

    @unittest.skipUnless(AmiAnyTest.run_long(), "run occasionally")
    def test_pdfplumber_json_longer_report_debug(self):
        """creates AmiPDFPlumber and reads pdf and debugs"""
        path = Path(Resources.TEST_IPCC_LONGER_REPORT, "fulltext.pdf")
        ami_pdfplumber = AmiPDFPlumber()
        # pdf_json = ami_pdfplumber.create_parsed_json(path)
        plumber_json = ami_pdfplumber.create_ami_plumber_json(path)
        assert type(plumber_json) is AmiPlumberJson
        metadata_ = plumber_json.pdf_json_dict['metadata']
        print(f"k {plumber_json.keys, metadata_.keys} \n====Pages====\n"
              # f"{len(plumber_json['pages'])} "
              # f"\n\n page_keys {c['pages'][0].items()}"
              )
        pages = plumber_json.get_ami_json_pages()
        assert len(pages) == 85
        for page in pages:
            ami_pdfplumber.debug_page(page)
        # pprint.pprint(f"c {c}[:20]")

    def test_strip_decorations_from_raw_expand_wg3_ch09_old(self):
        """
        From manually downloaded HTML strip image paragraphs

        <p class="Figures--tables-etc_•-Figure-title---spans-columns" lang="en-US">
          <span class="•-Figure-table-number---title">
            <span class="•-Bold-condensed" lang="en-GB">
              <img alt="" class="_idGenObjectAttribute-2" id="figure-9-1" src="https://ipcc.ch/report/ar6/wg3/downloads/figures/IPCC_AR6_WGIII_Figure_9_1.png">
              </span>
              </span>
              </p>
        This is mainly to see if stripping the img@href improvdes the readability of the raw HTML

        and
        <div class="_idGenObjectLayout-1">
          <div class="_idGenObjectStyleOverride-1" id="_idContainer006">
            <img alt="" class="_idGenObjectAttribute-1" src="https://ipcc.ch/report/ar6/wg3/downloads/figures/IPCC_AR6_WGIII_Equation_9_1-2.png">
          </div>
        </div>
        """
        encoding = "utf-8"
        expand_file = Path(Resources.TEST_IPCC_WG3, "Chapter09", "online", "raw.expand.html")
        assert expand_file.exists()

        expand_html = ET.parse(str(expand_file), parser=HTMLParser(encoding=encoding))
        assert expand_html is not None

        # Note remove_elems() edits the expand_html
        # remove styles
        HtmlUtil.remove_elems(expand_html, xpath="/html/head/style")
        # remove links
        HtmlUtil.remove_elems(expand_html, xpath="/html/head/link")
        # remove share_blocks
        """<span class="share-block">
              <img class="share-icon" src="../../share.png">
            </span>
        """
        HtmlUtil.remove_elems(expand_html, xpath=".//span[@class='share-block']")
        """
        <div class="ch-figure-button-cont">
          <a href="/report/ar6/wg3/figures/chapter-9/box-9-1-figure" target="_blank">
            <button class="btn-ipcc btn btn-primary ch-figure-button">Open figure</button>
          </a> 
        </div>        
        """
        HtmlUtil.remove_elems(expand_html, xpath=".//div[@class='ch-figure-button-cont']")

        """
        <div class="dropdown">
          <button id="dropdown-basic" aria-expanded="false" type="button" class="btn-ipcc btn btn-primary dl-dropdown dropdown-toggle btn btn-success">Downloads</button>
        </div>
        """
        HtmlUtil.remove_elems(expand_html, xpath="/html/body//div[@class='dropdown']")
        HtmlUtil.remove_elems(expand_html, xpath="/html/body//button")
        HtmlUtil.remove_elems(expand_html, xpath="/html//script")

        no_decorations = expand_html
        no_decorations_file = Path(expand_file.parent, "no_decorations.html")
        HtmlLib.write_html_file(no_decorations, no_decorations_file, debug=True)

    def test_strip_non_content_from_raw_expand_wg3_ch06(self):
        """
        From manually downloaded HTML strip non-content (style, link, button, etc

        """
        from climate.ipcc import IPCCChapter

        expand_file = Path(Resources.TEST_IPCC_WG3, "Chapter06", "online", "expanded.html")
        IPCCChapter.make_pure_ipcc_content(expand_file)

    def test_strip_decorations_from_raw_expand_syr_longer(self):
        """
        From manually downloaded HTML strip decorations

        The xpaths may need editing - they started as the same for WG3
        """
        encoding = "utf-8"
        expand_file = Path(Resources.TEST_IPCC_SYR, "lr", "online", "expanded.html")
        assert expand_file.exists()

        expand_html = ET.parse(str(expand_file), parser=HTMLParser(encoding=encoding))
        assert expand_html is not None

        # Note remove_elems() edits the expand_html
        # remove styles
        HtmlUtil.remove_elems(expand_html, xpath="/html/head/style")
        # remove links
        HtmlUtil.remove_elems(expand_html, xpath="/html/head/link")
        # remove share_blocks
        """<span class="share-block">
              <img class="share-icon" src="../../share.png">
            </span>
        """
        HtmlUtil.remove_elems(expand_html, xpath=".//span[@class='share-block']")
        """
        <div class="ch-figure-button-cont">
          <a href="/report/ar6/wg3/figures/chapter-9/box-9-1-figure" target="_blank">
            <button class="btn-ipcc btn btn-primary ch-figure-button">Open figure</button>
          </a> 
        </div>        
        """
        HtmlUtil.remove_elems(expand_html, xpath=".//div[@class='ch-figure-button-cont']")

        """
        <div class="dropdown">
          <button id="dropdown-basic" aria-expanded="false" type="button" class="btn-ipcc btn btn-primary dl-dropdown dropdown-toggle btn btn-success">Downloads</button>
        </div>
        """
        HtmlUtil.remove_elems(expand_html, xpath="/html/body//div[@class='dropdown']")
        HtmlUtil.remove_elems(expand_html, xpath="/html/body//button")
        HtmlUtil.remove_elems(expand_html, xpath="/html/body//script")

        no_decorations = expand_html
        no_decorations_file = Path(expand_file.parent, "no_decorations.html")
        HtmlLib.write_html_file(no_decorations, no_decorations_file, debug=True)

    def test_download_sr15_chapter1_and_strip_non_content(self):
        """read single chapter from "view" button and convert to raw semantic HTML
        Tests the encoding
        """
        debug = False
        rep = "sr15"
        chapter_no = 1
        chapter_no_out = "01"
        url = f"https://www.ipcc.ch/{rep}/chapter/chapter-{chapter_no}/"
        html_tree = HtmlLib.retrieve_with_useragent_parse_html(url, debug=debug)
        title = html_tree.xpath('/html/head/title')[0].text
        assert title == "Chapter 1 — Global Warming of 1.5 ºC"
        p0text = html_tree.xpath('//p')[0].text
        assert p0text[:41] == "Understanding the impacts of 1.5°C global"
        IPCCChapter.atrip_wordpress(html_tree)
        HtmlLib.write_html_file(html_tree,
                                Path(Resources.TEMP_DIR, "ipcc", rep, f"Chapter{chapter_no_out}", f"{WORDPRESS}.html"),
                                debug=True)
        IPCC.add_styles_to_head(HtmlLib.get_head(html_tree))
        HtmlLib.write_html_file(html_tree,
                                Path(Resources.TEMP_DIR, "ipcc", rep, f"Chapter{chapter_no_out}",
                                     f"{WORDPRESS}_styles.html"),
                                debug=True)

    @unittest.skipUnless(AmiAnyTest.run_long(), "run occasionally")
    def test_download_special_reports_and_strip_non_content(self):
        """read single chapter from "view" button and convert to raw semantic HTML
        Tests the encoding
        """
        chapters = [
            ("sr15", "chapter-1", "Chapter01"),
            ("sr15", "chapter-2", "Chapter02"),
            ("sr15", "chapter-3", "Chapter03"),
            ("sr15", "chapter-4", "Chapter04"),
            ("sr15", "chapter-5", "Chapter05"),
            ("sr15", "spm", "spm"),
            ("sr15", "ts", "ts"),
            ("sr15", "glossary", "glossary"),

            ("srccl", "chapter-1", "Chapter01"),
            ("srccl", "chapter-2", "Chapter02"),
            ("srccl", "chapter-3", "Chapter03"),
            ("srccl", "chapter-4", "Chapter04"),
            ("srccl", "chapter-5", "Chapter05"),
            ("srccl", "chapter-6", "Chapter06"),
            ("srccl", "chapter-7", "Chapter07"),
            ("srccl", "spm", "spm"),
            ("srccl", "ts", "ts"),
            # ("srccl", "glossary", "glossary"),  # points to PDF

            ("srocc", "chapter-1", "Chapter01"),
            ("srocc", "chapter-2", "Chapter02"),
            ("srocc", "chapter-3", "Chapter03"),
            ("srocc", "chapter-4", "Chapter04"),
            ("srocc", "chapter-5", "Chapter05"),
            ("srocc", "chapter-6", "Chapter06"),
            ("srocc", "spm", "spm"),
            ("srocc", "ts", "ts"),
            ("srocc", "glossary", "glossary"),

        ]
        debug = False
        for chapter in chapters:
            rep = chapter[0]
            chapter_no = chapter[1]
            chapter_no_out = chapter[2]
            url = f"https://www.ipcc.ch/{rep}/chapter/{chapter_no}/"
            print(f"reading: {url}")
            html = HtmlLib.retrieve_with_useragent_parse_html(url, debug=debug)
            HtmlLib.write_html_file(html,
                                    Path(Resources.TEMP_DIR, "ipcc", rep, chapter_no_out, f"{WORDPRESS}.html"),
                                    debug=True)
            IPCCChapter.atrip_wordpress(html)
            HtmlLib.write_html_file(html,
                                    Path(Resources.TEMP_DIR, "ipcc", rep, chapter_no_out, f"{DE_WORDPRESS}.html"),
                                    debug=True)
            IPCC.add_styles_to_head(HtmlLib.get_head(html))
            HtmlLib.write_html_file(html,
                                    Path(Resources.TEMP_DIR, "ipcc", rep, chapter_no_out,
                                         f"{DE_WORDPRESS}_styles.html"),
                                    debug=True)

    @unittest.skip("probably redundant")
    def test_download_sr15_as_utf8(self):
        """
        maybe obsolete
        """
        url = "https://www.ipcc.ch/sr15/chapter/chapter-1/"
        response = requests.get(url, headers={"user-agent": "myApp/1.0.0"})
        content = response.content
        content_string = content.decode("UTF-8")
        chapter_no_out = "01"
        rep = "sr15"
        outfile = Path(Resources.TEMP_DIR, "ipcc", rep, f"Chapter{chapter_no_out}", f"{WORDPRESS}_1.html")
        with open(outfile, "w", encoding="UTF-8") as f:
            f.write(content_string)

        content_html = ET.fromstring(content_string, HTMLParser())

        paras = content_html.xpath("//p")
        # check degree character is encoded
        assert paras[0].text[:41] == "Understanding the impacts of 1.5°C global"
        for p in paras[:10]:
            print(f"p> {p.text}")
        head_elems = content_html.xpath("/html/head/*")
        for head_elem in head_elems:
            print(f"h> {ET.tostring(head_elem)}")

    def test_download_wg_chapter_and_strip_non_content(self):
        """read single chapter from "EXPLORE" button and convert to raw semantic HTML
        """
        wg = "wg3"
        # correct chapter url
        chapter_no = 10
        url = f"https://www.ipcc.ch/report/ar6/{wg}/chapter/chapter-{chapter_no}/"
        outfile = Path(Resources.TEMP_DIR, "ipcc", wg, f"Chapter{chapter_no}", f"{GATSBY}.html")
        (html, error) = IPCCChapter.make_pure_ipcc_content(html_url=url, outfile=outfile)
        assert error is None
        assert outfile.exists()
        assert len(html.xpath("//div")) > 20

        # test non-existent chapter
        chapter_no = 100
        url = f"https://www.ipcc.ch/report/ar6/{wg}/chapter/chapter-{chapter_no}/"
        logger.warning(f"input {url}")
        outfile = None
        (html, error) = IPCCChapter.make_pure_ipcc_content(html_url=url, outfile=outfile)
        assert error.status_code == 404
        assert html is None

        # non-existent file
        file = "foo.bar"
        outfile = None
        logger.warning(f"output {outfile}")
        (html, error) = IPCCChapter.make_pure_ipcc_content(html_file=file, outfile=outfile)

    @unittest.skipUnless(AmiAnyTest.run_long(), "run occasionally")
    def test_download_all_wg_chapters_and_strip_non_content(self):
        """
        download over all chapters in reports and convert to raw semantic form
        """

        for section in [
            LR,
            SPM,
            ANN_IDX,
        ]:
            url = f"https://www.ipcc.ch/report/ar6/syr/{section}/"
            outfile = Path(Resources.TEMP_DIR, "ipcc", "syr", f"{section}", "content.html")
            (html_elem, error) = IPCCChapter.make_pure_ipcc_content(html_url=url, outfile=outfile)
            if error is not None and error.status_code == 404:
                print(f"no online chapter or {url}, assume end of chapters")

        for report in [
            "report/ar6/wg1",
            "report/ar6/wg2",
            "report/ar6/wg3",
            # "sr15",
            # "srocc",
            # "srccl",
        ]:
            for section in [
                SPM,
                "technical-summary",
            ]:
                url = f"https://www.ipcc.ch/{report}/chapter/{section}/"
                outfile = Path(Resources.TEMP_DIR, "ipcc", report, f"{section}", f"{GATSBY}.html")
                (html_elem, error) = IPCCChapter.make_pure_ipcc_content(html_url=url, outfile=outfile)
                if error is not None and error.status_code == 404:
                    print(f"no online chapter or {url}, assume end of chapters")

            for chapter_no in range(1, 99):
                outchap_no = chapter_no if chapter_no >= 10 else f"0{chapter_no}"
                url = f"https://www.ipcc.ch/{report}/chapter/chapter-{chapter_no}/"
                outfile = Path(Resources.TEMP_DIR, "ipcc", report, f"Chapter{outchap_no}", f"{GATSBY}.html")
                (html_elem, error) = IPCCChapter.make_pure_ipcc_content(html_url=url, outfile=outfile)
                if error is not None and error.status_code == 404:
                    print(f"no online chapter or {url}, assume end of chapters")
                    break

    def test_download_wg_chapter_spm_ts_IMPORTANT(self):
        """downlaods all parts of WG reports
        writes:
        gatsby_raw.html
        gatsby_raw.html
        de_gatsby.html
        para_list

        """
        reports = [
            IP_WG1,
        ]
        chapters = [
            SPM,
            TS,
            "chapter-1",
        ]
        web_publisher = IPCCGatsby()
        for report in reports:
            wg_url = f"{AR6_URL}{report}/"
            logger.info(f"report: {report}")
            for chap in chapters:
                logger.info(f"chapter: {chap}")
                outdir = Path(TEMP_DIR, report, chap)
                logger.info(f"outdir {outdir}")
                IPCC.download_save_chapter(report, chap, wg_url, outdir=TEMP_DIR, sleep=1)
                raw_gatsby_file = Path(outdir, f"{GATSBY_RAW}.html")
                logger.info(f"checking raw Gatsby file {raw_gatsby_file}")
                FileLib.assert_exist_size(raw_gatsby_file, minsize=20000, abort=False)
                html_elem = web_publisher.remove_unnecessary_markup(raw_gatsby_file)
                assert html_elem is not None, f"{raw_gatsby_file} gave None html_elem"
                body = HtmlLib.get_body(html_elem)
                if body is None:
                    logger.error(f"None body for {html_elem} in {raw_gatsby_file}")
                    continue
                elems = body.xpath(".//*")
                if len(elems) < 2:
                    # no significant content
                    continue
                de_gatsby_file = Path(outdir, f"{DE_GATSBY}.html")
                HtmlLib.write_html_file(html_elem, outfile=de_gatsby_file, debug=True)

                html_ids_file, idfile, parafile = web_publisher.add_ids(de_gatsby_file, outdir, assert_exist=True,
                                                                        min_id_sizs=10, min_para_size=10)
                logger.info(f"idfile {idfile}")
                logger.info(f"parafile {parafile}")

    def test_download_wg_chapter_spm_ts_using_dict_IMPORTANT(self):
        """downlaods all parts of WG reports
        writes:
        gatsby_raw.html
        gatsby_raw.html
        de_gatsby.html
        para_list

        """
        reports = [
            IP_WG1,
            # IP_WG2,
            # IP_WG3,
        ]
        chapters = [
            # SPM,
            # TS,
            "chapter-1",
        ]
        # ipcc_dict = IPCC_DICT.get_ipcc_dict()
        # ar6_url = ipcc_dict.get()
        web_publisher = IPCCGatsby()
        outdir = TEMP_DIR
        minsize = 500000
        for report in reports:
            wg_url = f"{AR6_URL}{report}/"
            print(f"report: {report}")
            for chap in chapters:
                print(f"chapter: {chap}")
                web_publisher.download_clean_chapter(chap, minsize, outdir, report, wg_url)

    def test_cmdline_download_wg_reports(self):
        """download WG reports
        output in petermr/semanticClimate
        FAILS TO DOWNLOAD
        """

        inurl = f"{AR6_URL}/"
        outdir = Path(f"{TEMP_DIR}/debug/")
        wg = "wg1"
        chapters = ["chapter-1", SPM, TS]
        # assert indir.exists()
        FileLib.force_mkdir(outdir)
        assert outdir.exists()
        args = [
            "IPCC",
            "--indir", inurl,
            "--outdir", str(outdir),
            "--informat", GATSBY,
            "--chapter", chapters,
            "--report", wg,
            "--operation", IPCCArgs.DOWNLOAD,
            "--kwords", "chapter:chapter",  # for test
            "--debug",
        ]

        wgdir = Path(outdir, wg)
        FileLib.delete_directory_contents(wgdir, delete_directory=True)
        assert not wgdir.exists(), f"{wgdir} should have been deleted"

        AMIClimate().run_command(args)
        assert wgdir.exists(), f"{wgdir} should have been created"

        chap1_dir = Path(wgdir, chapters[0])
        assert chap1_dir.exists()
        raw_gatsby_file = Path(chap1_dir, f"{GATSBY_RAW}.html")
        assert raw_gatsby_file.exists()
        htmlx = HtmlUtil.parse_html_lxml(raw_gatsby_file)
        title = htmlx.xpath("/html/head/title")
        assert title
        txt = title[0].text
        print(f"title {txt}")
        FileLib.assert_exist_size(raw_gatsby_file, minsize=300000, abort=True)

    def test_cmdline_help(self):
        """
        """
        AMIClimate().run_command(["IPCC", "--help"])

    def test_cmdline_download_sr_reports(self):
        """download WG reports
        output in petermr/semanticClimate
        """

        args = [
            "IPCC",
            "--indir", f"{AR6_URL}/",
            "--outdir", f"{TEMP_DIR}",
            "--informat", WORDPRESS,
            "--chapter", "SPM", "TS",
            "--report", "srocc",
            "--operation", IPCCArgs.DOWNLOAD,
            "--kwords", "chapter:chapter",  # for test
            "--debug",
        ]

        AMIClimate().run_command(args)

    def test_cmdline_search(self):
        """
        search reports with keywords
        """
        args = [
            "IPCC",
            "--indir", f"{TEMP_DIR}",
            "--outdir", f"{TEMP_DIR}/{IP_WG1}",
            "--chapter", "Chapter*",
            "--report", "wg1", "srocc",
            "--query", "birds", "methane",
            "--operation", IPCCArgs.SEARCH,
            "--debug",
        ]

        AMIClimate().run_command(args)

    def test_remove_gatsby_markup_for_report_types(self):
        """take output after downloading anc converting and strip all gatsby stuff, etc.
        """
        for rep_chap in [
            # ("sr15", "Chapter02"),
            # ("srccl", "Chapter02"),
            # ("srocc", "Chapter02"),
            ("wg1", "Chapter02"),
            ("wg2", "Chapter02"),
            ("wg3", "Chapter03"),
            ("syr", "longer-report")

        ]:
            publisher = IPCCGatsby()
            infile = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", rep_chap[0], rep_chap[1],
                          f"{publisher.raw_filename}.html")
            outfile = Path(Resources.TEMP_DIR, "ipcc", rep_chap[0], rep_chap[1], f"{publisher.cleaned_filename}.html")
            html = publisher.remove_unnecessary_markup(infile)
            HtmlLib.write_html_file(html, outfile, encoding="UTF-8", debug=True)

    def test_remove_wordpress_markup_for_report_types(self):
        """take output after downloading anc converting and strip all wordpress stuff, etc.
        """
        for rep_chap in [
            ("sr15", "Chapter02"),
            ("srccl", "Chapter02"),
            ("srocc", "Chapter02"),

        ]:
            publisher = IPCCWordpress()
            infile = Path(Resources.TEST_RESOURCES_DIR, "ipcc", rep_chap[0], rep_chap[1],
                          f"{publisher.raw_filename}.html")
            outfile = Path(Resources.TEMP_DIR, "ipcc", rep_chap[0], rep_chap[1], f"{publisher.cleaned_filename}.html")
            html = publisher.remove_unnecessary_markup(infile)

            HtmlLib.write_html_file(html, outfile, encoding="UTF-8", debug=True)

    def test_remove_wordpress_markup_from_all_srs_and_add_ids(self):
        """take output after downloading anc converting and strip all wordpress stuff, etc.
        """
        publisher = IPCCWordpress()
        globx = f"{Path(Resources.TEMP_DIR, 'ipcc')}/sr*/**/{publisher.cleaned_filename}.html"
        infiles = FileLib.posix_glob(globx)
        assert len(infiles) > 10
        print(f"de_publisher files {len(infiles)}")
        cleaned_path = Path(TEMP_DIR, "ipcc", "cleaned_content")
        for infile in infiles:
            chap = Path(infile).parent.stem
            sr = Path(infile).parent.parent.stem
            print(f"sr {sr} chap {chap}")
            outfile = Path(cleaned_path, sr, chap, f"{publisher.cleaned_filename}.html")
            htmlx = publisher.remove_unnecessary_markup(infile)
            HtmlLib.write_html_file(htmlx, outfile, encoding="UTF-8", debug=True)
            infile = Path(cleaned_path, sr, chap, f"{publisher.cleaned_filename}.html")
            outfile = Path(cleaned_path, sr, chap, f"{HTML_WITH_IDS}.html")
            idfile = Path(cleaned_path, sr, chap, f"{ID_LIST}.html")
            parafile = Path(cleaned_path, sr, chap, f"{PARA_LIST}.html")
            publisher.add_para_ids_and_make_id_list(infile, idfile=idfile, outfile=outfile, parafile=parafile)
            assert outfile.exists(), f"{outfile} should exist"
            assert idfile.exists(), f"{idfile} should exist"

    def test_remove_gatsby_markup_from_all_chapters(self):

        """
        input raw_html
        output_de-gatsby

        take output after downloading anc converting and strip all gatsby stuff, etc.
        """
        web_publisher = IPCCGatsby()
        indir = Resources.TEST_RESOURCES_DIR
        globx = f"{Path(indir, 'ipcc')}/**/{web_publisher.raw_filename}.html"

        infiles = FileLib.posix_glob(globx, recursive=True)
        outdir = TEMP_DIR
        for infile in infiles:
            html_elem = web_publisher.remove_unnecessary_markup(infile)
            # TODO - this is a mess, use Path components
            inpath = Path(infile).parent
            rest =  str(inpath)[len(str(indir)) + 1:]
            print(f"inpath {inpath} || {rest}")
            outpath = Path(outdir, rest)
            outfile = Path(outpath, f"{DE_GATSBY}.html")
            HtmlLib.write_html_file(html_elem, outfile, debug=True)

    def test_gatsby_add_ids_to_divs_and_paras(self):
        """
        outputs:
            html_with_ids
            id_filr
            paras_ids - paragraphs with ids

        """

        publisher = IPCCGatsby()

        indir = Resources.TEST_RESOURCES_DIR
        outdir = TEMP_DIR
        globx = f"{Path(indir, 'ipcc')}/**/{publisher.raw_filename}.html"
        infile = Path(indir, "ipcc", "wg3", "Chapter03", f"{DE_GATSBY}.html")
        outfile = Path(outdir, "ipcc", "wg3", "Chapter03", f"{HTML_WITH_IDS}.html")
        idfile = Path(outdir, "ipcc", "wg3", "Chapter03", f"{ID_LIST}.html")
        parafile = Path(outdir, "ipcc", "wg3", "Chapter03", f"{PARA_LIST}.html")

        publisher.add_para_ids_and_make_id_list(infile, idfile=idfile, outfile=outfile, parafile=parafile)
        assert outfile.exists(), f"{outfile} should exist"
        assert idfile.exists(), f"{idfile} should exist"

    def test_add_ids_to_divs_and_paras_wordpress(self):
        """
        runs Chapter02 and Chapter03 in SR15, SROCC and SRCCL
        takes D_WORDPRESS output (stripped) and adds p(aragraph) ids in HTML_WITH_IDS
        also outputs simple list of links into paras ID_LIST
        """
        publisher = IPCCWordpress()

        for rep in ["sr15", "srocc", "srccl"]:
            for chap in ["Chapter02", "Chapter03"]:
                indir = Resources.TEST_RESOURCES_DIR
                infile = Path(indir, "ipcc", rep, chap, f"{DE_WORDPRESS}.html")
                outdir = TEMP_DIR
                outfile = Path(outdir, "ipcc", rep, chap, f"{HTML_WITH_IDS}.html")
                idfile = Path(outdir, "ipcc", rep, chap, f"{ID_LIST}.html")
                parafile = Path(outdir, "ipcc", rep, chap, f"{PARA_LIST}.html")
                if not infile.exists():
                    print(f"cannot find: {infile}")
                    continue

                publisher.add_para_ids_and_make_id_list(infile, idfile=idfile, outfile=outfile)
                assert outfile.exists(), f"{outfile} should exist"
                assert idfile.exists(), f"{idfile} should exist"

    def test_add_ids_to_divs_and_paras_for_all_reports(self):
        publisher = IPCCGatsby()
        top_dir = str(Path(Resources.TEST_RESOURCES_DIR, "ipcc"))
        outdir = Path(TEMP_DIR, "ipcc")
        globx = f"{top_dir}/**/{DE_GATSBY}.html"
        gatsby_files = FileLib.posix_glob(globx, recursive=True)
        assert len(gatsby_files) >= 1, f"found {len(gatsby_files)} in {globx}"
        for infile in gatsby_files:
            outdir1 = Path(outdir, Path(infile).parent.stem)
            outfile = str(Path(outdir1, f"{HTML_WITH_IDS}.html"))
            idfile = str(Path(outdir1, f"{ID_LIST}.html"))
            parafile = str(Path(outdir1, f"{PARA_LIST}.html"))
            publisher.add_para_ids_and_make_id_list(infile, idfile=idfile, outfile=outfile, parafile=parafile)

    def test_gatsby_mini_pipeline(self):
        publisher = IPCCGatsby()
        topdir = Path(Resources.TEST_RESOURCES_DIR, 'ipcc')
        publisher.raw_to_paras_and_ids(topdir, )

    def test_search_wg3_and_index_chapters_with_ids(self):
        """
        read chapter, search for words and return list of paragraphs/ids in which they occur
        simple, but requires no server
        """
        infile = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "wg3", "Chapter03", f"{HTML_WITH_IDS}.html")
        assert infile.exists(), f"{infile} does not exist"
        html = ET.parse(str(infile), HTMLParser())
        paras = HtmlLib.find_paras_with_ids(html)
        assert len(paras) == 1163

        phrases = [
            "greenhouse gas",
            "pathway",
            "emissions",
            "global warming",
        ]
        para_phrase_dict = HtmlLib.create_para_ohrase_dict(paras, phrases)

        print(f"{para_phrase_dict.get('executive-summary_p1')}")
        keys = para_phrase_dict.keys()
        assert len(keys) == 334
        multi_item_paras = [item for item in para_phrase_dict.items() if len(item[1]) > 1]
        assert len(multi_item_paras) == 60

    def test_search_all_chapters_with_query_words(self, outfile=None):
        """
        read chapter, search for words and return list of paragraphs/ids in which they occur
        simple, but requires no server
        """
        query = "south_asia"
        indir = Path(Resources.TEST_RESOURCES_DIR, 'ipcc')
        outfile = Path(TEMP_DIR, f"{query}.html")
        debug = False
        globstr = f"{str(indir)}/**/{HTML_WITH_IDS}.html"
        infiles = FileLib.posix_glob(globstr, recursive=True)
        print(f"{len(infiles)} {infiles[:2]}")
        phrases = [
            "bananas",
            "South Asia",
        ]
        html1 = IPCC.create_hit_html(infiles, phrases=phrases, outfile=outfile, debug=debug)
        assert html1 is not None
        assert len(html1.xpath("//p")) > 0

    def test_search_all_chapters_with_query_words_commandline(self, outfile=None):
        """
        read chapter, search for words and return list of paragraphs/ids in which they occur
        simple, but requires no server
        """
        query = "south_asia"
        indir = Path(Resources.TEST_RESOURCES_DIR, 'ipcc')
        outdir = Path(TEMP_DIR, 'ipcc')
        outfile = Path(outdir, f"{query}.html")
        debug = False
        infiles = FileLib.posix_glob(f"{str(indir)}/**/{HTML_WITH_IDS}.html", recursive=True)
        phrases = [
            "bananas",
            "South Asia"
        ]
        html1 = IPCC.create_hit_html(infiles, phrases=phrases, outfile=outfile, debug=debug)

    def test_arguments_no_action(self):

        # run args help
        args = AMIClimate().run_command(
            ['IPCC', '--help'])

        # run args
        query_name = "south_asia1"
        ss = str(Path(Resources.TEST_RESOURCES_DIR, 'ipcc'))
        infiles = FileLib.posix_glob(f"{ss}/**/{HTML_WITH_IDS}.html", recursive=True)
        infiles = [str(infile) for infile in infiles]
        logger.warning(f"infiles {infiles}")
        infiles2 = infiles[:100]
        queries = ["South Asia", "methane"]
        outdir = f"{Path(Resources.TEMP_DIR, 'queries')}"
        output = f"{Path(outdir, query_name)}.html"
        AMIClimate().run_command(
            ['IPCC', '--input', str(infiles2[0]), '--output', str(output)])
        # assert Path(output).exists(), f"{output} should exist"

    def test_commandline_search(self):

        # run args
        query_name = "methane"
        indir_path = Path(Resources.TEST_RESOURCES_DIR, 'ipcc', 'cleaned_content')
        infiles = [
            str(Path(indir_path, "wg2/Chapter12/html_with_ids.html")),
            str(Path(indir_path, "wg3/Chapter08/html_with_ids.html")),
        ]
        exists = [
            Path(f).exists() for f in infiles
        ]
        assert (l := len(exists)) > 0, f"input files {l}"
        queries = ["South Asia", "methane"]
        outdir = f"{Path(Resources.TEMP_DIR, 'queries')}"
        output = f"{Path(outdir, query_name)}.html"
        logger.warning(f"writing to {output}")
        print((f"writing to {output}"))

        AMIClimate().run_command(
            ['IPCC', '--input', infiles, '--query', queries,
             '--output', output])
        assert Path(output).exists()

    def test_commandline_search_with_indir(self):

        # run args
        query_name = "methane"
        indir_path = Path(Resources.TEST_RESOURCES_DIR, 'ipcc', 'cleaned_content')
        infile = "wg2/Chapter12/html_with_ids.html"
        queries = ["South Asia", "methane"]
        outdir = f"{Path(Resources.TEMP_DIR, 'queries')}"
        output = f"{Path(outdir, query_name)}.html"
        AMIClimate().run_command(
            ['IPCC', '--indir', str(indir_path), '--input', infile, '--query', queries,
             '--output', output])
        assert Path(output).exists()

    def test_commandline_search_with_wildcards(self):
        """generate inpout files """

        # run args
        query_name = "methane"
        indir_path = Path(Resources.TEST_RESOURCES_DIR, 'ipcc', 'cleaned_content')
        glob_str = f"{indir_path}/**/html_with_ids.html"
        infiles = FileLib.posix_glob(glob_str)
        assert len(infiles) >= 1
        queries = ["South Asia", "methane"]
        queries = "methane"
        outdir = f"{Path(Resources.TEMP_DIR, 'queries')}"
        output = f"{Path(outdir, query_name)}.html"
        AMIClimate().run_command(
            ['IPCC', '--input', infiles, '--query', queries, '--output', output])

        assert Path(output).exists()
        assert len(ET.parse(output).xpath("//ul")) > 0

    def test_not_reference_ids_xpaths(self):
        """include/omit paras by xpath """

        # run args
        infile = Path(Resources.TEST_RESOURCES_DIR, 'ipcc', 'cleaned_content', 'wg1', 'Chapter02', 'html_with_ids.html')

        html_tree = ET.parse(str(infile), HTMLParser())

        p_id = "//p[@id]"
        p_ids = html_tree.xpath(p_id)
        assert len(p_ids) >= 1000, f"p_ids {len(p_ids)}"

        xpath_ref = "//p[@id and ancestor::*[@id='references']]"
        p_refs = html_tree.xpath(xpath_ref)
        assert len(p_refs) >= 500, f"p_refs {len(p_refs)}"

        xpath_not_ref = "//p[@id and not(ancestor::*[@id='references'])]"
        p_not_refs = html_tree.xpath(xpath_not_ref)
        assert len(p_not_refs) >= 100, f"p_not_refs {len(p_not_refs)}"

    def test_search_with_xpaths(self):
        """include/omit paras by xpath """

        query = ["methane"]
        infile = str(
            Path(Resources.TEST_RESOURCES_DIR, 'ipcc', 'cleaned_content', 'wg1', 'Chapter02', 'html_with_ids.html'))
        outdir = f"{Path(Resources.TEMP_DIR, 'queries')}"

        output = f"{Path(outdir, 'methane_all')}.html"
        AMIClimate().run_command(
            ['IPCC', '--input', infile, '--query', query, '--output', output])
        html_tree = ET.parse(output)
        assert (pp := len(html_tree.xpath(".//a[@href]"))) >= 11, f"found {pp} paras in {output}"

        output = f"{Path(outdir, 'methane_ref')}.html"
        xpath_ref = "//p[@id and ancestor::*[@id='references']]"
        AMIClimate().run_command(
            ['IPCC', '--input', infile, '--query', query, '--output', output, '--xpath', xpath_ref])
        html_tree = ET.parse(output)
        assert (pp := len(html_tree.xpath(".//a[@href]"))) >= 5, f"found {pp} paras in {output}"

        query = "methane"
        output = f"{Path(outdir, 'methane_noref')}.html"
        xpath_ref = "//p[@id and not(ancestor::*[@id='references'])]"
        AMIClimate().run_command(
            ['IPCC', '--input', infile, '--query', query, '--output', output, '--xpath', xpath_ref])
        self.check_output_tree(output, xpath=".//a[@href]")

    def test_symbolic_xpaths(self):

        infile = str(
            Path(Resources.TEST_RESOURCES_DIR, 'ipcc', 'cleaned_content', 'wg1', 'Chapter02', 'html_with_ids.html'))
        outdir = f"{Path(Resources.TEMP_DIR, 'queries')}"
        query = "methane"

        output = f"{Path(outdir, 'methane_refs1')}.html"
        AMIClimate().run_command(
            ['IPCC', '--input', infile, '--query', query, '--output', output, '--xpath', "_REFS"])
        self.check_output_tree(output, expected=7, xpath=".//a[@href]")

        output = f"{Path(outdir, 'methane_norefs1')}.html"
        AMIClimate().run_command(
            ['IPCC', '--input', infile, '--query', query, '--output', output, '--xpath', "_NOREFS"])
        # self.check_output_tree(output, expected=[2,8], xpath=".//a[@href]")
        self.check_output_tree(output, xpath=".//a[@href]")

    def test_symbol_indir(self):

        infile = "**/html_with_ids.html"
        outdir = f"{Path(Resources.TEMP_DIR, 'queries')}"
        output = f"{Path(outdir, 'methane_norefs2')}.html"
        query = "methane"

        AMIClimate().run_command(
            ['IPCC', '--indir', "_IPCC_REPORTS", '--input', "_HTML_IDS", '--query', "methane", '--outdir', "_QUERY_OUT",
             "--output", output, '--xpath',
             "_NOREFS"])
        self.check_output_tree(output, expected=[60,300], xpath=".//a[@href]")

    def test_commandline_search_with_wildcards_and_join_indir(self):
        """generate inpout files """

        # run args
        query_name = "methane"
        indir_path = Path(Resources.TEST_RESOURCES_DIR, 'ipcc', 'cleaned_content')
        input = f"{indir_path}/**/html_with_ids.html"

        queries = ["South Asia", "methane"]
        outdir = f"{Path(Resources.TEMP_DIR, 'queries')}"
        output = f"{Path(outdir, query_name)}.html"
        AMIClimate().run_command(
            ['IPCC', '--indir', str(indir_path), '--input', input, '--query', queries,
             '--output', output])
        assert Path(output).exists()
        assert len(ET.parse(output).xpath("//ul")) > 0

    def test_parse_kwords(self):
        AMIClimate().run_command(
            ['IPCC', '--kwords'])
        AMIClimate().run_command(
            ['IPCC', '--kwords', 'foo:bar'])
        AMIClimate().run_command(
            ['IPCC', '--kwords', 'foo:bar', 'plugh: xyzzy'])

    def test_output_bug(self):
        """PMR only, fails if output does not exist"""
        """IPCC --input /Users/pm286/workspace/pyamihtml/test/resources/ipcc/cleaned_content/**/html_with_ids.html --query "south asia"
          --output /Users/pm286/workspace/pyamihtml/temp/queries/south_asiax.html --outdir /Users/pm286/ --xpath "//p[@id and ancestor::*[@id='frequently-asked-questions']]
        """
        AMIClimate().run_command(
            ['IPCC',
             "--input", f"{CLEANED_CONTENT}/**/html_with_ids.html",
             "--query", "south asia",
             "--output", f"{QUERIES_DIR}/south_asia.html",
             "--xpath", "//p[@id and ancestor::*[@id='frequently-asked-questions']]",
             ]
        )
        print("=======================================================")

        AMIClimate().run_command(
            ['IPCC', "--input",
             f"{CLEANED_CONTENT}/**/html_with_ids.html",
             "--query", "south asia",
             "--output", f"{QUERIES_DIR}/south_asia_not_exist.html",
             "--xpath", "//p[@id and ancestor::*[@id='frequently-asked-questions']]",
             ]
        )

    def test_faq_xpath(self):
        """"""
        AMIClimate().run_command(
            ['IPCC', "--input",
             f"{CLEANED_CONTENT}/**/html_with_ids.html",
             "--query", "asia",
             "--output", f"{QUERIES_DIR}/asia_faq.html",
             "--xpath", "_FAQ",
             ]
        )

    def test_version(self):
        AMIClimate().run_command(["--help"])
        AMIClimate().run_command(["IPCC", "--help"])

    def test_ipcc_reports(self):
        """tests components of IPCC
        Not yet fully implemented
        """
        indir_path = Path(Resources.TEST_RESOURCES_DIR, 'ipcc', 'cleaned_content')
        reports = [f for f in list(indir_path.glob("*/")) if f.is_dir()]
        report_stems = [Path(f).stem for f in reports]
        assert len(report_stems) >= 1
        reports_set = set(["sr15", "srocc", "srccl", "syr", "wg1", "wg2", "wg3"])
        assert reports_set.issubset(set(report_stems))

    def test_ipcc_syr_contents(self):
        """analyses contents for IPCC syr
        """
        syr_path = Path(Resources.TEST_RESOURCES_DIR, 'ipcc', 'cleaned_content', 'syr')
        assert syr_path.exists()
        child_dirs = [f for f in list(syr_path.glob("*")) if f.is_dir()]
        child_stems = set([Path(f).stem for f in child_dirs])
        child_set = set(["annexes-and-index", "longer-report", "summary-for-policymakers"])
        assert child_set == child_stems

    def test_ipcc_syr_child_dirs(self):
        """analyses contents for IPCC syr child dirs
        """
        syr_path = Path(Resources.TEST_RESOURCES_DIR, 'ipcc', 'cleaned_content', 'syr')
        child_list = ["annexes-and-index", "longer-report", "summary-for-policymakers"]
        annexe_dir = Path(syr_path, "annexes-and-index")
        annexe_content = Path(annexe_dir, "content.html")
        assert annexe_content.exists()
        lr_dir = Path(syr_path, "longer-report")
        lr_content = Path(lr_dir, "html_with_ids.html")
        assert lr_content.exists()
        spm_dir = Path(syr_path, "summary-for-policymakers")
        spm_content = Path(spm_dir, "content.html")
        assert spm_content.exists()

    def test_ipcc_syr_annexes(self):
        """analyses contents for IPCC syr annexes
        """
        syr_annexe_content = Path(Resources.TEST_RESOURCES_DIR, 'ipcc', 'cleaned_content', 'syr', 'annexes-and-index',
                                  "content.html")
        assert syr_annexe_content.exists()
        annexe_html = ET.parse(str(syr_annexe_content), HTMLParser())
        assert annexe_html is not None
        body = HtmlLib.get_body(annexe_html)
        header1 = body.xpath("./div/div/div/div/header")[0]
        assert len(header1) == 1
        header_h1 = header1.xpath("div/div/div/div/h1")[0]
        assert header_h1 is not None
        header_h1_text = header_h1.text
        assert header_h1_text == "Annexes and Index"

        section = body.xpath("./div/div/div/div/div/section")[0]
        assert section is not None
        annexe_divs = section.xpath("div/div/div[@class='h1-container']")
        assert len(annexe_divs) == 6

        annexe_titles = []
        for annexe_div in annexe_divs:
            text = annexe_div.xpath("h1")[0].text
            text = text.replace('\r', '').replace('\n', '').strip()
            annexe_titles.append(text)
            print(f" text {text}")
        assert annexe_titles == [
            'Annex I: Glossary',
            'Annex II: Acronyms, Chemical Symbols and Scientific Units',
            'Annex III: Contributors',
            'Annex IV: Expert Reviewers AR6 SYR',
            'Annex V: List of Publications of the Intergovernmental Panel on Climate Change',
            'Index'
        ]

    def test_ipcc_syr_lr_toc(self):
        """analyses contents for IPCC syr longer report
        """
        """
            <!-- TOC (from UNFCCC)-->
            <div class="toc">

                <div>
                    <span>Decision</span><span>Page</span></a>
                </div>

                <nav role="doc-toc">
                    <ul>
                        <li>
                            <a href="../Decision_1_CMA_3/split.html"><span class="descres-code">1/CMA.3</span><span
                                    class="descres-title">Glasgow Climate Pact</span></a>
                        </li>
                       ...
                    </ul>
                </nav> 
            </div>
        """
        report = 'longer-report'
        syr_lr_content = Path(Resources.TEST_RESOURCES_DIR, IPCC_DIR, CLEANED_CONTENT, SYR,
                              SYR_LR, HTML_WITH_IDS_HTML)
        logger.warning(f"SYR file is: {syr_lr_content}")
        print(f"SYR file is: {syr_lr_content}")
        assert syr_lr_content.exists()
        lr_html = ET.parse(str(syr_lr_content), HTMLParser())
        assert lr_html is not None
        body = HtmlLib.get_body(lr_html)
        header_h1 = body.xpath("div//h1")[0]
        assert header_h1 is not None
        header_h1_text = header_h1.text
        toc_title = "SYR Longer Report"
        assert header_h1_text == toc_title
        publisher = IPCCGatsby()
        toc_html, ul = publisher.make_nav_ul(toc_title)

        h1_containers = body.xpath("./div//div[@class='h1-container']")
        assert len(h1_containers) == 4
        texts = []
        for h1_container in h1_containers:
            print(f"id: {h1_container.attrib['id']}")
            text = ''.join(h1_container.xpath("./h1")[0].itertext()).strip()
            texts.append(text)
            li = ET.SubElement(ul, "li")
            a = ET.SubElement(li, "a")
            target_id = h1_container.attrib["id"]
            a.attrib["href"] = f"./html_with_ids.html#{target_id}"
            span = ET.SubElement(a, "span")
            span.text = text

        assert texts == [
            '1. Introduction',
            'Section 2: Current Status and Trends',
            'Section 3: Long-Term Climate and Development Futures',
            'Section 4: Near-Term Responses in a Changing Climate',
        ]
        toc_title = Path(syr_lr_content.parent, "toc.html")
        HtmlLib.write_html_file(toc_html, toc_title, debug=True)

    def test_ipcc_syr_lr_toc_full(self):
        """creates toc recursively for IPCC syr longer report
        """
        filename = HTML_WITH_IDS_HTML
        syr_lr_content = Path(Resources.TEST_RESOURCES_DIR, IPCC_DIR, CLEANED_CONTENT, SYR,
                              SYR_LR, filename)
        lr_html = ET.parse(str(syr_lr_content), HTMLParser())
        body = HtmlLib.get_body(lr_html)
        publisher = IPCCGatsby()
        toc_html, ul = publisher.make_header_and_nav_ul(body)
        level = 0
        publisher.analyse_containers(body, level, ul, filename=filename)

        toc_title = Path(syr_lr_content.parent, "toc.html")
        HtmlLib.write_html_file(toc_html, toc_title, debug=True)

    def test_find_ipcc_curly_links(self):
        """
        IPCC links are dumb text usually either in text nodes or spans
        Not finished
        """
        syr_lr_content = Path(Resources.TEST_RESOURCES_DIR, 'ipcc', 'cleaned_content', 'syr',
                              'longer-report', HTML_WITH_IDS_HTML)
        lr_html = ET.parse(str(syr_lr_content), HTMLParser())
        span_texts = lr_html.xpath(".//span[text()[normalize-space(.)!='' "
                                   # "and startswith(normalize-space(.),'{') "
                                   # "and endswith(normalize-space(.),'}') "
                                   "]]")
        for span_text in span_texts:
            texts = span_text.xpath(".//text()")
            if len(texts) > 1:
                # ends = [t for t in texts]
                # print(f"==={len(texts)}")
                # c = '\u25a0'
                # c = '\u00b6'
                # c = '\u33af'
                print(f"texts [{''.join(tx for tx in texts)}]")

    def test_add_ipcc_hyperlinks(self):
        """resolves dumb links (e.g.
        {WGII SPM D.5.3; WGIII SPM D.1.1}) into hyperllinks
        target relies on SYR being sibling of WGIII, etc)
        The actual markup of the links is horrible. Sometime in spans, sometimes in naked text()
        nodes. Somes the nodes are labelled "refs", sometimes not. The safest way is to try to
        locate the actual text and find the relevant node.
        """

        syr_lr_content = Path(Resources.TEST_RESOURCES_DIR, IPCC_DIR, CLEANED_CONTENT, SYR,
                              SYR_LR, HTML_WITH_IDS_HTML)
        lr_html = ET.parse(str(syr_lr_content), HTMLParser())
        para_with_ids = lr_html.xpath("//p[@id]")
        assert len(para_with_ids) == 206
        IPCC.find_analyse_curly_refs(para_with_ids)
        outpath = Path(TEMP_DIR, IPCC_DIR, CLEANED_CONTENT, SYR,
                       SYR_LR, "links.html")
        HtmlLib.write_html_file(lr_html, outpath, debug=True)

    # ========= helpers ============
    def check_output_tree(self, output, expected=None, xpath=None):
        assert xpath, f"must give xpath"
        assert output, f"output cannot be None"
        html_tree = ET.parse(output)
        assert html_tree is not None, f"html_tree is None"
        if expected:
            pp = len(html_tree.xpath(xpath))
            if type(expected) is list and len(expected) ==  2:
                assert expected[0] <= pp <= expected[1], f"found {pp} elements in {output}, expected {expected}"
            else:
                assert pp == expected, f"found {pp} elements in {output}"



