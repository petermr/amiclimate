"""
library methods not associated with climate
Includes temporary updates of amilib functions

"""
from pathlib import Path


class NewFileLib:
    """amilib.file_lib.FileLib routines being updated and tested here
    """

    @classmethod
    def assert_exist_size(cls, file, minsize, abort=True, debug=True):
        """asserts a file exists and is of sufficient size
        :param file: file or path
        :param minsize: minimum size
        :param abort: throw exception if fails (is this needed?)
        :param debug: output filename
        """
        path = Path(file)
        if debug:
            print(f"checking {file}")
        try:
            assert path.exists(), f"file {path} must exist"
            assert (s := path.stat().st_size) > minsize, \
                f"file {file} size = {s} must be above {minsize}"
        except AssertionError as e:
            if abort:
                raise e

