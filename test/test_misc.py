import logging
import sys
from pathlib import Path
import pytest
from amilib.file_lib import FileLib

from amilib.html_generator import HtmlGenerator
from amilib.ami_pdf_libs import AmiPDFPlumber

from test.resources import Resources
from test.test_all import AmiAnyTest

from climate.misclib import MiscUtil

logging.basicConfig()
# logger = logging.getLogger(__file__)
logger = logging.getLogger(__name__)
logger.level = logging.DEBUG
class UNMiscTest(AmiAnyTest):
    """
    May really belong in PDFPlumber tests
    """

    def test_pdfplumber_singlecol_create_spans_with_CSSStyles(self):
        """
        creates AmiPDFPlumber and reads single-column pdf and debugs
        """
        input_pdf = Path(Resources.TEST_IPCC_LONGER_REPORT, "fulltext.pdf")
        output_page_dir = Path(AmiAnyTest.TEMP_DIR, "html", "ipcc", "LongerReport", "pages")
        # page_json_dir = output_page_dir
        page_json_dir = None
        output_page_dir.mkdir(exist_ok=True, parents=True)
        ami_pdfplumber = AmiPDFPlumber()
        HtmlGenerator.create_html_pages(
            ami_pdfplumber, input_pdf=input_pdf, outdir=output_page_dir, page_json_dir=page_json_dir,
            pages=[1, 2, 3, 4, 5, 6, 7])

from climate.misclib import ApproxNestedMapping
class MiscTest(AmiAnyTest):

    def test_logger(self):
        import logging
        logger = logging.getLogger(__name__)
        log = Path(FileLib.get_home(), "misc", 'example.log')
        print(f"log {log}")
        logging.basicConfig(filename=str(log), level=logging.DEBUG)
        logger.debug('This message should go to the log file')
        logger.info('So should this')
        logger.warning('And this, too')
        logger.error('And non-ASCII stuff, too, like Øresund and Malmö')

    def test_more_logger(self):

        namex = __name__
        formatx = None
        logger = MiscUtil.create_logger(namex)

        logger.info("PLEASE WORK!")


    def test_approx_dictionaries(self):
        """tests near equality of nested dictioaries"""
        dict1 = {"foo":
                    {"bar": 0.30000001, "plugh": 10.3}
                 }
        dict2 = {"foo":
                     {"plugh": 10.30000001, "bar": 0.30000002},
                 }

        assert dict1 == ApproxNestedMapping.nested_approx(dict2)

    def test_approx_dictionaries_with_sequences(self):
        """test near equality of nested dicts with lists"""
        dict1 = {"foo":
                    {"bar": 0.30000001, "plugh": [10.3, 10.4]}
                 }
        dict2 = {"foo":
                     {"plugh": [10.30000001, 10.4000001], "bar": 0.30000002},
                 }

        assert dict1 == ApproxNestedMapping.nested_approx(dict2)

    # @pytest.mark.xfail(reason="compares quantities outside range")
    def test_approx_unequal_dictionaries_with_sequences(self):
        """test near inequality of nested dicts with lists"""
        dict1 = {"foo":
                    {"bar": 0.30000001, "plugh": [10.9, 10.4]}
                 }
        dict2 = {"foo":
                     {"plugh": [10.30000001, 10.4000001], "bar": 0.30000002},
                 }

        try:
            assert dict1 == ApproxNestedMapping.nested_approx(dict2)
            raise AssertionError(f"should raise AsserrtionError")
        except AssertionError as e:
            """ expected"""
            logger.info("raised AssertionError")
            print(f"raised AssertionError {logger.level} {logging.INFO}")


    def test_approx_unequal_dictionaries_with_sequences(self):
        """test near inequality of nested dicts with lists"""
        dict1 = {"foo":
                    {"bar": 0.30000001, "plugh": [10.9, 10.4]}
                 }
        dict2 = {"foo":
                     {"plugh": [10.30000001, 10.4000001], "bar": 0.30000002},
                 }

        try:
            assert dict1 == ApproxNestedMapping.nested_approx(dict2)
            raise AssertionError(f"should raise AsserrtionError")
        except AssertionError as e:
            """ expected"""
            logger.info("raised AssertionError")
            print(f"raised AssertionError {logger.level} {logging.INFO}")


    @pytest.mark.xfail(reason="lists of different lengths")
    def test_approx_dictionaries_with_bad_sequences(self):
        """dict with bad lists"""
        dict1 = {"foo":
                    {"bar": 0.30000001, "plugh": [10.3, 10.4]}
                 }
        dict2 = {"foo":
                     {"plugh": [10.30000001, 10.4000001, 99], "bar": 0.30000002},
                 }

        assert dict1 == ApproxNestedMapping.nested_approx(dict2)

    def test_arrays_of_dicts(self):

        dict11 =  {
                "foo1a": "bar1a",
                "foo1b": 1.1,
                }
        dict12 =  {
                "foo2a": "bar2a",
                "foo2b": 1.2,
                }
        dict12y =  {
                "foo2a": "bar2ay",
                "foo2b": "bar2b",
                }

        dict21 = {
            "foo1a": "bar1a",
            "foo1b": 1.1001,
        }
        dict22 = {
            "foo2a": "bar2a",
            "foo2b": 1.2001,
        }

        dict1x = {
            "fooa": [
                dict11,
                dict12,
                ]
            }

        dict1y = {
            "fooa": [
                dict11,
                dict12y,
                ]
            }

        dict2x = {
            "fooa": [
                dict21,
                dict22,
            ]
        }
        assert dict1x == ApproxNestedMapping.nested_approx(dict2x, abs=0.001)

        # change a value
        # assert dict1x == ApproxNestedMapping.nested_approx(dict1y)


    def test_large_nested_dicts(self):
        indir = Path(Resources.TEST_IPCC_DIR, "wg3", "Chapter08", "html")
        infile1 = Path(indir, "page_1.json")
        dict1 = MiscUtil.load_json_from_file(str(infile1))
        dict1_copy = MiscUtil.load_json_from_file(str(infile1))
        assert dict1 == ApproxNestedMapping.nested_approx(dict1_copy)

        infile1_approx = Path(indir, "page_1approx.json")
        dict1_approx = MiscUtil.load_json_from_file(str(infile1_approx))
        assert dict1_approx == ApproxNestedMapping.nested_approx(dict1)
