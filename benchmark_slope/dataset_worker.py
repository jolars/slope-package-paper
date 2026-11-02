"""Materialize each scientific input once for all compared methods."""

import sys
from importlib import import_module

from artifacts import write_dataset
from metewand import serve_dataset_materializer


def generate(context):
    dataset = import_module(f"datasets.{sys.argv[1]}").Dataset(**context.parameters)
    values = dataset.get_data()
    return write_dataset(values["X"], values["y"], context.output_dir)


if __name__ == "__main__":
    serve_dataset_materializer(generate)
