import io
import json
from pathlib import Path
from typing import Any, Union

from .instances import ProblemInstance, Job, Resource, RenewableResource, NonRenewableResource
from .utils import use_write_file


class ProblemInstanceJSONEncoder(json.JSONEncoder):
    """
    JSON encoder for ProblemInstance objects.
    """
    def default(self, obj: Any) -> Any:
        if not isinstance(obj, ProblemInstance):
            return super().default(obj)

        instance = obj
        resources = [self._encode_resource(resource) for resource in instance.resources]
        resources.sort(key=lambda r: r["Key"])
        jobs = [self._encode_job(job, instance) for job in instance.jobs]
        jobs.sort(key=lambda j: j["Id"])

        instance_object = {
            "Name": instance.name,
            "Horizon": instance.horizon,
            "Resources": resources,
            "Jobs": jobs,
        }
        return instance_object

    def _encode_resource(self, resource: Resource) -> dict[str, Any]:
        if isinstance(resource, RenewableResource):
            capacity = resource.capacity
        elif isinstance(resource, NonRenewableResource):
            capacity = resource.initial_capacity
        else:
            raise ValueError(f"Unknown resource type: {type(resource)}")

        resource_object = {
            "Key": resource.key,
            "Type": resource.type,
            "Capacity": capacity,
        }
        return resource_object

    def _encode_job(self, job: Job, instance: ProblemInstance) -> dict[str, Any]:
        job_object = {
            "Id": job.id,
            "Duration": job.duration,
            "Resource consumption": dict(job.consumption),
            "Successors": sorted(instance.job_successors[job.id]),
        }
        return job_object


def write_psplib(instance: ProblemInstance, target: Union[str, Path, io.TextIOBase]):
    """Writes the given problem instance to the given target in PSPLIB format.

    Args:
        instance: The problem instance to write.
        target: The target to write to.
    """
    use_write_file(target, _write_psplib, instance)


def write_json(instance: ProblemInstance, target: Union[str, Path, io.TextIOBase], indent: int = 4):
    """
    Writes the given problem instance to the given target in JSON format.

    Args:
        instance: The problem instance to write.
        target: The target to write to.
    """
    use_write_file(target, _write_json, instance, indent)


def _write_psplib(f: io.TextIOBase, instance: ProblemInstance):
    raise NotImplementedError("PSPLIB writing is not implemented yet.")

def _write_json(f: io.TextIOBase, instance: ProblemInstance, indent: int):
    json.dump(instance, f, cls=ProblemInstanceJSONEncoder, indent=indent)
