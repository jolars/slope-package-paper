"""Materialize scientific inputs independently of problem parameters."""

from importlib import import_module

from artifacts import write_dataset


def _generate(context, family):
    dataset = import_module(f"datasets.{family}").Dataset(**context.parameters)
    values = dataset.get_data()
    return write_dataset(values["X"], values["y"], context.output_dir)


def simulated(context):
    return _generate(context, "simulated")


def breheny(context):
    return _generate(context, "breheny")


def libsvm(context):
    return _generate(context, "libsvm")
