import pytest
import glob, os, sys


def test_columun_count():
    for path in glob.glob("*"):
        if path.find(".") == -1 and os.path.isfile(path):
            lines = []
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            sample_args = 0
            for line in lines:
                if not line.startswith("#"):
                    meta_args = len(line.split(","))
                    if sample_args == 0:
                        sample_args = meta_args
                    assert sample_args == meta_args


if __name__ == "__main__":
    test_columun_count()
