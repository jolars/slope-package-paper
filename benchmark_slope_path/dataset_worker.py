"""Materialize the design and reference alpha grid once for every method."""

import sys
from importlib import import_module

from artifacts import GRID_PARAMETERS, write_dataset
from metewand import serve_dataset_materializer
from objective import Objective


def generate(context):
    parameters = dict(context.parameters)
    problem = {name: parameters.pop(name) for name in GRID_PARAMETERS}
    dataset = import_module(f"datasets.{sys.argv[1]}").Dataset(**parameters)
    values = dataset.get_data()
    objective = Objective(**problem)
    objective.set_data(values["X"], values["y"])
    return write_dataset(values["X"], values["y"], objective, context.output_dir)


if __name__ == "__main__":
    serve_dataset_materializer(generate)
