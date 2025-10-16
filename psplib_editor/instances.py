from abc import abstractmethod
from dataclasses import dataclass
from typing import Collection, Mapping, TypeAlias

from .utils import hidden_field


T_JobId: TypeAlias = int
T_ResourceKey: TypeAlias = str


@dataclass
class Precedence:
    predecessor: T_JobId
    successor: T_JobId

    def __hash__(self):
        return hash((self.predecessor, self.successor))


@dataclass
class Job:
    id: T_JobId
    duration: int
    consumption: Mapping[T_ResourceKey, int]

    def __eq__(self, other):
        """Compares this instance to other for equality."""
        if isinstance(other, Job):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"{Job.__name__}({self.id.__name__}={self.id})"


@dataclass
class Resource:
    key: T_ResourceKey

    @abstractmethod
    @property
    def type(self) -> str:
        ...

    def __eq__(self, other):
        if isinstance(other, Resource):
            return self.type == other.type \
                and self.key == other.key
        return False

    def __hash__(self):
        return hash(self.key)


@dataclass
class RenewableResource(Resource):
    capacity: int

    @property
    def type(self) -> str:
        return "Renewable"

    def __eq__(self, value):
        return super().__eq__(value)

    def __hash__(self):
        return super().__hash__()


@dataclass
class NonRenewableResource(Resource):
    initial_capacity: int

    @property
    def type(self) -> str:
        return "NonRenewable"

    def __eq__(self, value):
        return super().__eq__(value)

    def __hash__(self):
        return super().__hash__()


@dataclass
class ProblemInstance:
    name: str
    horizon: int

    jobs: Collection[Job]
    precedences: Collection[Precedence]
    resources: Collection[Resource]

    _data_built: bool = hidden_field(default=False)
    _jobs_by_id: Mapping[T_JobId, Job] = hidden_field()
    _job_predecessors: Mapping[T_JobId, Collection[T_JobId]] = hidden_field()
    _job_successors: Mapping[T_JobId, Collection[T_JobId]] = hidden_field()
    _resources_by_key: Mapping[T_ResourceKey, Resource] = hidden_field()

    def __init__(self, name: str, horizon: int,
                 jobs: Collection[Job],
                 precedences: Collection[Precedence],
                 resources: Collection[Resource],
                 build_data: bool = False):
        self.name = name
        self.horizon = horizon
        self.jobs = jobs
        self.precedences = precedences
        self.resources = resources

        if build_data:
            self._build_data_if_needed()

    @property
    def jobs_by_id(self) -> Mapping[T_JobId, Job]:
        self._build_data_if_needed()
        return self._jobs_by_id

    @property
    def job_predecessors(self) -> Mapping[T_JobId, Collection[T_JobId]]:
        self._build_data_if_needed()
        return self._job_predecessors

    @property
    def job_successors(self) -> Mapping[T_JobId, Collection[T_JobId]]:
        self._build_data_if_needed()
        return self._job_successors

    @property
    def resources_by_key(self) -> Mapping[T_ResourceKey, Resource]:
        self._build_data_if_needed()
        return self._resources_by_key

    def _build_data_if_needed(self):
        if self._data_built:
            return

        self._jobs_by_id = {}
        for job in self.jobs:
            self._jobs_by_id[job.id] = job

        job_predecessors: dict[T_JobId, list[T_JobId]] = {}
        job_successors: dict[T_JobId, list[T_JobId]] = {}
        for precedence in self.precedences:
            if precedence.predecessor not in job_successors:
                job_successors[precedence.predecessor] = []
            if precedence.successor not in job_predecessors:
                job_predecessors[precedence.successor] = []
            job_successors[precedence.predecessor].append(precedence.successor)
            job_predecessors[precedence.successor].append(precedence.predecessor)
        self._job_predecessors = job_predecessors
        self._job_successors = job_successors

        self._resources_by_key = {}
        for resource in self.resources:
            self._resources_by_key[resource.key] = resource

        self._data_built = True
