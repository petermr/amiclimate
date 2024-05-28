from pathlib import Path

from amilib.html_generator import HtmlGenerator
from amilib.ami_pdf_libs import AmiPDFPlumber

from test.resources import Resources
from test.test_all import AmiAnyTest
class UNMiscTest(AmiAnyTest):
    """
    May really belone in PDFPlumber tests
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
