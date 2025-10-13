import re
from typing import Any, Callable, Sequence, Type, Union, TextIO, Pattern
from pathlib import Path


def parse_psplib(source: Union[str, Path, TextIO], name: str = None):
    """
    Parses a PSPLIB instance file under the given source.

    Args:
        source: The source from which to parse the instance.
            Can either be a name of the file, file path,
            or an open file-like object to read directly from.
        name: If given, determines the name of the parsed instance.

    Returns:
        The parsed PSPLIB instance.
    """
    parser = FileParser()

    if isinstance(source, (str, Path)):
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"PSPLIB file not found: {path}")
        with path.open("r", encoding="utf8") as f:
            parser.init(f)
            return _parse_psplib(parser, name)
    elif isinstance(source, TextIO):
        parser.init(source)
        return _parse_psplib(parser, name)
    else:
        raise TypeError("source must be a filename, Path, or file-like object")


class FileParser:
    """
    Class for parsing open files line-by-line.
    Allows for parsing lines using regex expressions and parsing matched values.
    """
    class FileParserError(ValueError):
        def __init__(self, filename: str, linenum: int, *args):
            super().__init__(f"[{filename}:{linenum}]", *args)

    class UnsupportedOperationError(FileParserError):
        """Attempted unsupported operation."""

    class ParseError(FileParserError):
        """Invalid parse operation (arguments or conditions)."""

    def __init__(self):
        """
        Initializes this instance.
        """
        self._source: TextIO = None
        self._linenum = None

    def init(self, source: TextIO):
        """
        Prepares for reading from a given open file-like source object.

        Args:
            source: The file-like object to read from.
        """
        self._source = source
        self._linenum = 0

    def read_line(self) -> str:
        """Reads and returns a single line from the underlying source."""
        self._linenum += 1
        return self._source.readline().rstrip()

    def skip_lines(self, count: int):
        """
        Skips the given number of lines.
        Each skipped line is read fully from the underlying source.
        """
        if count < 0:
            self.error("Number of lines to skip cannot be negative", error_type=FileParser.UnsupportedOperationError)
        for _ in range(count):
            self.read_line()

    def parse_line(self,
                   pattern: Union[str, Pattern],
                   types: Union[Any, Sequence[Union[Type, Callable[[Any], Any]]]],
                   fullmatch: bool = True,
                   ) -> Sequence[Any]:
        """
        Parses the next line using a given regex pattern.
        The line is read from the underlying source.
        Given types specify how to extract values from a match in the parsed line.

        Args:
            pattern: The regex pattern to parse the line with.
            types: Either a type or a constructor function of the match to parse,
                or the sequence of types or constructor functions specifying how the desired values should be extracted.
            fullmatch (optional): Determines whether the pattern should match the line fully (True), or partially (False).
                Default is fully (True).

        Returns:
            The parsed value if only a single value was expected,
            or the parsed values in the determined order of appearance.

        Raises:
            FileParser.UnsupportedOperationError: If the operation is not supported
                for the combination of inner state and arguments.
            FileParser.ParseError: If any error during the parsing process is encountered.
        """
        line = self.read_line()
        if isinstance(pattern, str):
            match = (re.fullmatch(pattern, line) if fullmatch else re.match(pattern, line))
        elif isinstance(pattern, Pattern):
            match = (pattern.fullmatch(line) if fullmatch else pattern.match(line))
        else:
            self.error("Unsupported parse pattern type", error_type=FileParser.UnsupportedOperationError)

        if not match:
            self.error("Pattern did not match the current line")

        expected_multiple_values = isinstance(values, Sequence)
        if not expected_multiple_values:
            values = (values, )

        values = match.groups()
        if len(types) != len(values):
            self.error("Number of matched values does not correspond to number of expected values")

        values = []
        for value, type in zip(values, types):
            value_parsed = type(value)
            values.append(value_parsed)

        return values if expected_multiple_values else values[0]

    def error(self, *args, error_type: ValueError = ParseError):
        """Raises an error detailed with the current parsing state."""
        raise error_type(self._source.name, self._linenum, *args)


def _parse_psplib(parser: FileParser, name: str = None):
    def divider():
        parser.skip_lines(1)

    def pattern_keyvalue(key: str) -> str:
        return "{}\s*:\*(\d+)".format(key)

    def pattern_resource_definition(resource: str, type: str) -> str:
        return "\s*-\s+{}\s*:\s*(\d+)\s+{}".format(resource, type)

    # Header with metadata (not parsed)
    divider()
    parser.skip_lines(2)  # "file with basedata" / "initial value random generator"

    # Information
    divider()
    project_count = parser.parse_line(pattern_keyvalue("projects"), int)
    job_count = parser.parse_line(pattern_keyvalue("jobs (incl. supersource/sink )"), int)
    horizon = parser.parse_line(pattern_keyvalue("horizon"), int)
    parser.skip_lines(1)  # RESOURCES list header
    renewable_resource_count = parser.parse_line(pattern_resource_definition("renewable", "R"), int)
    nonrenewable_resource_count = parser.parse_line(pattern_resource_definition("nonrenewable", "N"), int)
    _doubly_constrained_resource_count = parser.parse_line(pattern_resource_definition("doubly constrained", "D"), int)

    if project_count != 1:
        parser.error("Only single-project instances are currently supported", error_type=FileParser.UnsupportedOperationError)
    if _doubly_constrained_resource_count > 0:
        parser.error("Doubly-constrained resources are not currently supported", error_type=FileParser.UnsupportedOperationError)

    num_resources = renewable_resource_count + nonrenewable_resource_count + _doubly_constrained_resource_count

    # Projects
    divider()
    parser.skip_lines(2)  # "PROJECT INFORMATION" / projects header ("pronr. #jobs rel.date duedate tardcost  MPM-Time")
    projects = []
    for _ in range(project_count):
        project_id, project_duedate, project_tardiness_cost = \
            parser.parse_line(r"\s*(\d+)\s+(?:\d+)\s+(?:\d+)\s+(\d+)\s+(\d+)\s+(?:\d+)\s*",
                              (int, int, int))
        projects.append((project_id, project_duedate, project_tardiness_cost))

    # Precedences
    divider()
    parser.skip_lines(2)  # "PRECEDENCE RELATIONS" / precedences header ("jobnr. #modes #successors successors")
    precedences = []
    for _ in range(job_count):
        job_id, _job_modes, job_successor_count, job_successors = \
            parser.parse_line(r"\s*(\d+)\s+(\d+)\s+(\d+)\s*(\s+\d+(?:\s+\d+)*)?\s*",
                              (int, int, int, lambda successors_str: map(int, successors_str.split()) if successors_str else tuple()))
        if job_successor_count != len(job_successors):
            parser.error("Number of parsed job successors does not match the expected number of job successors")
        precedences.append((job_id, job_successor_count, job_successors))

    # Job Resource consumptions
    divider()
    parser.skip_lines(1)  # "REQUESTS/DURATIONS"
    resource_keys = parser.parse_line(r"\s*jobnr.\s+mode\s+duration\s*(\s+[RND]\s\d+(?:\s+[RND]\s\d+)*)?\s*",
                                      lambda keys_str: re.findall(r"[RND]\s\d+", keys_str) if keys_str else [])
    if len(resource_keys) != num_resources:
        parser.error("Number of parsed resource keys does not match the expected number of resources")
    divider()
    jobs = []
    for _ in range(job_count):  # assumes single-mode jobs. Should be sum(job.num_modes for job in jobs) entries
        job_id, _job_mode, job_duration, consumptions = \
            parser.parse_line(r"\s*(\d+)\s+(\d+)\s+(\d+)\s*(\s+\d+(?:\s+\d+)*)?\s*",
                              (int, int, int, lambda consumptions_str: map(int, consumptions_str.split()) if consumptions_str else tuple()))
        if len(consumptions) != num_resources:
            parser.error("Number of parsed job resource-consumptions does not match the expected number of resources")
        jobs.append((job_id, job_duration, consumptions))

    # Resource availabilities
    divider()
    parser.skip_lines(2)  # "RESOURCE AVAILABILITIES" / Resource name headers (assuming same order of resources as above)
    capacities = parser.parse_line(r"\s*(\d+(?:\s+\d+)*)?\s*",
                                   lambda capacities_str: map(int, capacities_str.split()) if capacities_str else tuple())

    # TODO build instance
    instance = ...
    return instance
