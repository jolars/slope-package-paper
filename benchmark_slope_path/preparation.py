"""Construct the problem-dependent path grid once before solver measurement."""

from artifacts import read_dataset, write_preparation
from objective import Objective


def prepare_grid(data, context):
    X, y = read_dataset(context.dataset_dir)
    objective = Objective(**context.problem_parameters)
    objective.set_data(X, y)
    return write_preparation(objective, context.output_dir)
