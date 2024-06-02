"""
library methods not associated with climate
Includes temporary updates of amilib functions

"""
import logging
from pathlib import Path
import json

# from climate.misclib import MiscUtil


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


import pytest
from collections.abc import Mapping


class MiscUtil:
    """various utilies (or revised amilib) probably move to amilib later
    """
    @classmethod
    def load_json_from_file(cls, file, raise_exception=True):
        """convenience method wrapping json.load()
        :param file: to read from
        :param throw_exception: If true, throw exception on bad Jso, else return None
        :return content or None
        """
        if not file:
            return None
        path = Path(file)
        if not path.exists():
            raise FileNotFoundError(f"cannot find {file}")
        with open(path, "r") as f:
            try:
                content = json.load(f)
            except json.decoder.JSONDecodeError as e:
                if raise_exception:
                    raise e
                return None
            return content

    @classmethod
    def create_logger(cls, namex, formatx=None, outstream=None):
        """
        Creates logger (suggest one per module)
        I THINK I have finally gotm Python logger to work
        see https://stackoverflow.com/questions/7016056/python-logging-not-outputting-anything
        :param namex: logger name (usually __name__)
        :param formatx: format (default: '%(filename)s:%(lineno)s | %(asctime)s | %(levelname)s | %(message)s')
        :param outstream: defaults to sys.stdout (haven't tried files, but should work)
        :return: logger

        """
        import sys
        logger = logging.getLogger(namex)
        if formatx is None:
            formatx = '%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(process)d | %(message)s'
            formatx = '%(filename)s:%(lineno)s | %(asctime)s | %(levelname)s | %(message)s'
        stdout_log_formatter = logging.Formatter(formatx)
        if outstream is None:
            outstream = sys.stdout
        stdout_log_handler = logging.StreamHandler(stream=outstream)
        stdout_log_handler.setLevel(logging.INFO)
        stdout_log_handler.setFormatter(stdout_log_formatter)
        logger.addHandler(stdout_log_handler)
        level = logging.INFO
        logger.setLevel(level)
        return logger


    # ====================approx routines=============

    def my_approx(expected, rel=None, abs=None, nan_ok=False):
        """compare nested dictionaries approx
        https://stackoverflow.com/questions/56046524/check-if-python-dictionaries-are-equal-allowing-small-difference-for-floats
        thanks to @hoefling
        """
        class ApproxNestedMapping(ApproxMapping):
            """
            use as
            def test_nested():
                assert {'foo': {'bar': 0.30000001}} == my_approx({'foo': {'bar': 0.30000002}})
            """
            def _yield_comparisons(self, actual):
                for k in self.expected.keys():
                    if isinstance(actual[k], type(self.expected)):
                        gen = ApproxNestedMapping(
                            self.expected[k], rel=self.rel, abs=self.abs, nan_ok=self.nan_ok
                        )._yield_comparisons(actual[k])
                        for el in gen:
                            yield el
                    else:
                        yield actual[k], self.expected[k]

            def _check_type(self):
                for key, value in self.expected.items():
                    if not isinstance(value, type(self.expected)):
                        super()._check_type()

        if isinstance(expected, Mapping):
            return ApproxNestedMapping(expected, rel, abs, nan_ok)
        return pytest.approx(expected, rel, abs, nan_ok)

import pytest
from _pytest.python_api import ApproxBase, ApproxMapping, ApproxSequenceLike

class ApproxBaseReprMixin(ApproxBase):
    def __repr__(self) -> str:

        def recur_repr_helper(obj):
            if isinstance(obj, dict):
                return dict((k, recur_repr_helper(v)) for k, v in obj.items())
            elif isinstance(obj, tuple):
                return tuple(recur_repr_helper(o) for o in obj)
            elif isinstance(obj, list):
                return list(recur_repr_helper(o) for o in obj)
            else:
                return self._approx_scalar(obj)

        return "approx({!r})".format(recur_repr_helper(self.expected))

# also compares lists in dicts (same URL, from @Iker)
class ApproxNestedSequenceLike(ApproxSequenceLike, ApproxBaseReprMixin):

    def _yield_comparisons(self, actual):
        for k in range(len(self.expected)):
            if isinstance(self.expected[k], dict):
                mapping = ApproxNestedMapping(self.expected[k], rel=self.rel, abs=self.abs, nan_ok=self.nan_ok)
                for el in mapping._yield_comparisons(actual[k]):
                    yield el
            elif isinstance(self.expected[k], (tuple, list)):
                mapping = ApproxNestedSequenceLike(self.expected[k], rel=self.rel, abs=self.abs, nan_ok=self.nan_ok)
                for el in mapping._yield_comparisons(actual[k]):
                    yield el
            else:
                yield actual[k], self.expected[k]

    def _check_type(self):
        pass


class ApproxNestedMapping(ApproxMapping, ApproxBaseReprMixin):

    def _yield_comparisons(self, actual):
        for k in self.expected.keys():
            if isinstance(self.expected[k], dict):
                mapping = ApproxNestedMapping(self.expected[k], rel=self.rel, abs=self.abs, nan_ok=self.nan_ok)
                for el in mapping._yield_comparisons(actual[k]):
                    yield el
            elif isinstance(self.expected[k], (tuple, list)):
                mapping = ApproxNestedSequenceLike(self.expected[k], rel=self.rel, abs=self.abs, nan_ok=self.nan_ok)
                for el in mapping._yield_comparisons(actual[k]):
                    yield el
            else:
                yield actual[k], self.expected[k]

    def _check_type(self):
        pass



    @classmethod
    def nested_approx(cls, expected, rel=None, abs=None, nan_ok=False):
        if isinstance(expected, dict):
            return ApproxNestedMapping(expected, rel, abs, nan_ok)
        if isinstance(expected, (tuple, list)):
            return ApproxNestedSequenceLike(expected, rel, abs, nan_ok)
        return pytest.approx(expected, rel, abs, nan_ok)

