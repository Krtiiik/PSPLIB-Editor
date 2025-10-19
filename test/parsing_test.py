import os
from pathlib import Path
import unittest
from io import StringIO
import json

import jsonschema.exceptions

from psplib_editor.instances import Job, Precedence, ProblemInstance, RenewableResource
from psplib_editor.parsing import parse_json, parse_psplib


INSTANCE_NAME = "j301_1.sm"
INSTANCE_FILENAME_PSPLIB = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", INSTANCE_NAME)
INSTANCE_FILENAME_JSON = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", INSTANCE_NAME + ".json")
EXPECTED = {
    "horizon": 158,
    "jobs": {
        Job(1, 0, {"R 1": 0 , "R 2": 0, "R 3": 0, "R 4": 0}),
        Job(2, 8, {"R 1": 4 , "R 2": 0, "R 3": 0, "R 4": 0}),
        Job(3, 4, {"R 1": 10, "R 2": 0, "R 3": 0, "R 4": 0}),
        Job(4, 6, {"R 1": 0 , "R 2": 0, "R 3": 0, "R 4": 3}),
        Job(5, 3, {"R 1": 3 , "R 2": 0, "R 3": 0, "R 4": 0}),
        Job(6, 8, {"R 1": 0 , "R 2": 0, "R 3": 0, "R 4": 8}),
        Job(7, 5, {"R 1": 4 , "R 2": 0, "R 3": 0, "R 4": 0}),
        Job(8, 9, {"R 1": 0 , "R 2": 1, "R 3": 0, "R 4": 0}),
        Job(9, 2, {"R 1": 6 , "R 2": 0, "R 3": 0, "R 4": 0}),
        Job(10, 7, {"R 1": 0 , "R 2": 0, "R 3": 0, "R 4": 1}),
        Job(11, 9, {"R 1": 0 , "R 2": 5, "R 3": 0, "R 4": 0}),
        Job(12, 2, {"R 1": 0 , "R 2": 7, "R 3": 0, "R 4": 0}),
        Job(13, 6, {"R 1": 4 , "R 2": 0, "R 3": 0, "R 4": 0}),
        Job(14, 3, {"R 1": 0 , "R 2": 8, "R 3": 0, "R 4": 0}),
        Job(15, 9, {"R 1": 3 , "R 2": 0, "R 3": 0, "R 4": 0}),
        Job(16, 10, {"R 1": 0 , "R 2": 0, "R 3": 0, "R 4": 5}),
        Job(17, 6, {"R 1": 0 , "R 2": 0, "R 3": 0, "R 4": 8}),
        Job(18, 5, {"R 1": 0 , "R 2": 0, "R 3": 0, "R 4": 7}),
        Job(19, 3, {"R 1": 0 , "R 2": 1, "R 3": 0, "R 4": 0}),
        Job(20, 7, {"R 1": 0 , "R 2": 10, "R 3": 0, "R 4": 0}),
        Job(21, 2, {"R 1": 0 , "R 2": 0, "R 3": 0, "R 4": 6}),
        Job(22, 7, {"R 1": 2 , "R 2": 0, "R 3": 0, "R 4": 0}),
        Job(23, 2, {"R 1": 3 , "R 2": 0, "R 3": 0, "R 4": 0}),
        Job(24, 3, {"R 1": 0 , "R 2": 9, "R 3": 0, "R 4": 0}),
        Job(25, 3, {"R 1": 4 , "R 2": 0, "R 3": 0, "R 4": 0}),
        Job(26, 7, {"R 1": 0 , "R 2": 0, "R 3": 4, "R 4": 0}),
        Job(27, 8, {"R 1": 0 , "R 2": 0, "R 3": 0, "R 4": 7}),
        Job(28, 3, {"R 1": 0 , "R 2": 8, "R 3": 0, "R 4": 0}),
        Job(29, 7, {"R 1": 0 , "R 2": 7, "R 3": 0, "R 4": 0}),
        Job(30, 2, {"R 1": 0 , "R 2": 7, "R 3": 0, "R 4": 0}),
        Job(31, 2, {"R 1": 0 , "R 2": 0, "R 3": 2, "R 4": 0}),
        Job(32, 0, {"R 1": 0 , "R 2": 0, "R 3": 0, "R 4": 0}),
    },
    "precedences": {Precedence(predecessor, successor) for predecessor, successors in [
        (1, (2, 3, 4)),
        (2, (6, 11, 15)),
        (3, (7, 8, 13)),
        (4, (5, 9, 10)),
        (5, (20,)),
        (6, (30,)),
        (7, (27,)),
        (8, (12, 19, 27)),
        (9, (14,)),
        (10, (16, 25)),
        (11, (20, 26)),
        (12, (14,)),
        (13, (17, 18)),
        (14, (17,)),
        (15, (25,)),
        (16, (21, 22)),
        (17, (22,)),
        (18, (20, 22)),
        (19, (24, 29)),
        (20, (23, 25)),
        (21, (28,)),
        (22, (23,)),
        (23, (24,)),
        (24, (30,)),
        (25, (30,)),
        (26, (31,)),
        (27, (28,)),
        (28, (31,)),
        (29, (32,)),
        (30, (32,)),
        (31, (32,)),
        (32, tuple()),
    ] for successor in successors},
    "resources": {
        RenewableResource("R 1", 12),
        RenewableResource("R 2", 13),
        RenewableResource("R 3", 4),
        RenewableResource("R 4", 12),
    },
}


class Parsing_Tests(unittest.TestCase):
    def assert_instance_validity(self, instance: ProblemInstance):
        self.assertEqual(INSTANCE_NAME, instance.name)
        self.assertEqual(EXPECTED["horizon"], instance.horizon)

        for job_id, job in instance.jobs_by_id.items():
            self.assertEqual(job_id, job.id)
        for resource_key, resource in instance.resources_by_key.items():
            self.assertEqual(resource_key, resource.key)
        for predecessor, successors in instance.job_successors.items():
            for successor in successors:
                self.assertIn(Precedence(predecessor, successor), EXPECTED["precedences"])
        for successor, predecessors in instance.job_predecessors.items():
            for predecessor in predecessors:
                self.assertIn(Precedence(predecessor, successor), EXPECTED["precedences"])

        self.assertSetEqual(EXPECTED["jobs"], set(instance.jobs))
        for expected_job in EXPECTED["jobs"]:
            actual_job = instance.jobs_by_id[expected_job.id]
            self.assertEqual(expected_job.duration, actual_job.duration)
            self.assertDictEqual(expected_job.consumption, actual_job.consumption)

        self.assertSetEqual(EXPECTED["precedences"], set(instance.precedences))

        self.assertSetEqual(EXPECTED["resources"], set(instance.resources))
        for expected_resource in EXPECTED["resources"]:
            actual_resource = instance.resources_by_key[expected_resource.key]
            self.assertEqual(expected_resource.capacity, actual_resource.capacity)


class Parsing_PSPLIB_Tests(Parsing_Tests):
    def test_parse_psplib_filename(self):
        instance = parse_psplib(INSTANCE_FILENAME_PSPLIB, name=INSTANCE_NAME)
        self.assert_instance_validity(instance)

    def test_parse_psplib_path(self):
        path = Path(INSTANCE_FILENAME_PSPLIB)
        instance = parse_psplib(path, name=INSTANCE_NAME)
        self.assert_instance_validity(instance)

    def test_parse_psplib_file(self):
        with open(INSTANCE_FILENAME_PSPLIB) as f:
            instance = parse_psplib(f, name=INSTANCE_NAME)
        self.assert_instance_validity(instance)


class Parsing_JSON_Tests(Parsing_Tests):
    def test_parse_filename(self):
        instance = parse_json(INSTANCE_FILENAME_JSON)
        self.assert_instance_validity(instance)

    def test_parse_path(self):
        path = Path(INSTANCE_FILENAME_JSON)
        instance = parse_json(path)
        self.assert_instance_validity(instance)

    def test_parse_file(self):
        with open(INSTANCE_FILENAME_JSON) as f:
            instance = parse_json(f)
        self.assert_instance_validity(instance)

    def test_invalid_json(self):
        invalid_encodings = [
            {"UnexpectedField": 42},
            {"Name": "Instance with missing fields"},
            {"Horizon": "Text instead of integer"},
            {"Resources": [{"Key": "R 1", "Type": "Renewable"}]},  # missing Capacity
            {"Jobs": [{"Id": 1, "Duration": 5, "Resource consumption": {"R 1": 2}}]},  # missing Successors
        ]
        for encoding in invalid_encodings:
            encoding_stream = StringIO(json.dumps(encoding))
            encoding_stream.seek(0)
            with self.subTest(encoding=encoding):
                with self.assertRaises(ValueError):
                    parse_json(encoding_stream)
