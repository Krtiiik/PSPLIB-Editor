from io import StringIO
import os
import unittest

from psplib_editor.parsing import parse_json, parse_psplib
from psplib_editor.writing import write_json


INSTANCE_NAME = "j301_1.sm"
INSTANCE_FILENAME_PSPLIB = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", INSTANCE_NAME)


class Writing_JSON_Tests(unittest.TestCase):
    def test_write_instance_schema_compliant(self):
        instance = parse_psplib(INSTANCE_FILENAME_PSPLIB, name=INSTANCE_NAME)

        output_stream = StringIO()
        write_json(instance, output_stream, indent=4)

        output_stream.seek(0)
        written_instance = parse_json(output_stream)
        pass  # If parsing succeeded, the written instance is schema-compliant
