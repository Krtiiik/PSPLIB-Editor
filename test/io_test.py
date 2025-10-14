import os
from pathlib import Path
import unittest


from psplib_editor.instances import Job, Precedence, ProblemInstance, RenewableResource
from psplib_editor.io import parse_psplib


class IO_PSPLIBParsing_Tests(unittest.TestCase):
    instance_name = "Test"
    instance_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "j301_1.sm")

    def setUp(self):
        return super().setUp()

    def test_parse_psplib_filename(self):
        instance = parse_psplib(IO_PSPLIBParsing_Tests.instance_filename, name=IO_PSPLIBParsing_Tests.instance_name)
        self.assert_instance_validity(instance)

    def test_parse_psplib_path(self):
        path = Path(IO_PSPLIBParsing_Tests.instance_filename)
        instance = parse_psplib(path, name=IO_PSPLIBParsing_Tests.instance_name)
        self.assert_instance_validity(instance)

    def test_parse_psplib_file(self):
        with open(IO_PSPLIBParsing_Tests.instance_filename) as f:
            instance = parse_psplib(f, name=IO_PSPLIBParsing_Tests.instance_name)
        self.assert_instance_validity(instance)

    def assert_instance_validity(self, instance: ProblemInstance):
        expected_horizon = 158
        expected_jobs = [
            (1, 0, {"R 1": 0 , "R 2": 0, "R 3": 0, "R 4": 0}),
            (2, 8, {"R 1": 4 , "R 2": 0, "R 3": 0, "R 4": 0}),
            (3, 4, {"R 1": 10, "R 2": 0, "R 3": 0, "R 4": 0}),
            (4, 6, {"R 1": 0 , "R 2": 0, "R 3": 0, "R 4": 3}),
            (5, 3, {"R 1": 3 , "R 2": 0, "R 3": 0, "R 4": 0}),
            (6, 8, {"R 1": 0 , "R 2": 0, "R 3": 0, "R 4": 8}),
            (7, 5, {"R 1": 4 , "R 2": 0, "R 3": 0, "R 4": 0}),
            (8, 9, {"R 1": 0 , "R 2": 1, "R 3": 0, "R 4": 0}),
            (9, 2, {"R 1": 6 , "R 2": 0, "R 3": 0, "R 4": 0}),
            (10, 7, {"R 1": 0 , "R 2": 0, "R 3": 0, "R 4": 1}),
            (11, 9, {"R 1": 0 , "R 2": 5, "R 3": 0, "R 4": 0}),
            (12, 2, {"R 1": 0 , "R 2": 7, "R 3": 0, "R 4": 0}),
            (13, 6, {"R 1": 4 , "R 2": 0, "R 3": 0, "R 4": 0}),
            (14, 3, {"R 1": 0 , "R 2": 8, "R 3": 0, "R 4": 0}),
            (15, 9, {"R 1": 3 , "R 2": 0, "R 3": 0, "R 4": 0}),
            (16, 10, {"R 1": 0 , "R 2": 0, "R 3": 0, "R 4": 5}),
            (17, 6, {"R 1": 0 , "R 2": 0, "R 3": 0, "R 4": 8}),
            (18, 5, {"R 1": 0 , "R 2": 0, "R 3": 0, "R 4": 7}),
            (19, 3, {"R 1": 0 , "R 2": 1, "R 3": 0, "R 4": 0}),
            (20, 7, {"R 1": 0 , "R 2": 10, "R 3": 0, "R 4": 0}),
            (21, 2, {"R 1": 0 , "R 2": 0, "R 3": 0, "R 4": 6}),
            (22, 7, {"R 1": 2 , "R 2": 0, "R 3": 0, "R 4": 0}),
            (23, 2, {"R 1": 3 , "R 2": 0, "R 3": 0, "R 4": 0}),
            (24, 3, {"R 1": 0 , "R 2": 9, "R 3": 0, "R 4": 0}),
            (25, 3, {"R 1": 4 , "R 2": 0, "R 3": 0, "R 4": 0}),
            (26, 7, {"R 1": 0 , "R 2": 0, "R 3": 4, "R 4": 0}),
            (27, 8, {"R 1": 0 , "R 2": 0, "R 3": 0, "R 4": 7}),
            (28, 3, {"R 1": 0 , "R 2": 8, "R 3": 0, "R 4": 0}),
            (29, 7, {"R 1": 0 , "R 2": 7, "R 3": 0, "R 4": 0}),
            (30, 2, {"R 1": 0 , "R 2": 7, "R 3": 0, "R 4": 0}),
            (31, 2, {"R 1": 0 , "R 2": 0, "R 3": 2, "R 4": 0}),
            (32, 0, {"R 1": 0 , "R 2": 0, "R 3": 0, "R 4": 0}),
        ]
        expected_jobs = {Job(*job_data) for job_data in expected_jobs}

        expected_successors = [
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
        ]
        expected_precedences = {Precedence(predecessor, successor)
                                for predecessor, successors in expected_successors
                                for successor in successors}

        expected_resources = {RenewableResource(key, capacity) for key, capacity in[
            ("R 1", 12),
            ("R 2", 13),
            ("R 3", 4),
            ("R 4", 12),
        ]}

        self.assertEqual(IO_PSPLIBParsing_Tests.instance_name, instance.name)
        self.assertEqual(expected_horizon, instance.horizon)

        for job_id, job in instance.jobs_by_id.items():
            self.assertEqual(job_id, job.id)
        for resource_key, resource in instance.resources_by_key.items():
            self.assertEqual(resource_key, resource.key)
        for predecessor, successors in instance.job_successors.items():
            for successor in successors:
                self.assertIn(Precedence(predecessor, successor), expected_precedences)
        for successor, predecessors in instance.job_predecessors.items():
            for predecessor in predecessors:
                self.assertIn(Precedence(predecessor, successor), expected_precedences)

        self.assertSetEqual(expected_jobs, set(instance.jobs))
        for expected_job in expected_jobs:
            actual_job = instance.jobs_by_id[expected_job.id]
            self.assertEqual(expected_job.duration, actual_job.duration)
            self.assertDictEqual(expected_job.consumption, actual_job.consumption)

        self.assertSetEqual(expected_precedences, set(instance.precedences))

        self.assertSetEqual(expected_resources, set(instance.resources))
        for expected_resource in expected_resources:
            actual_resource = instance.resources_by_key[expected_resource.key]
            self.assertEqual(expected_resource.capacity, actual_resource.capacity)
