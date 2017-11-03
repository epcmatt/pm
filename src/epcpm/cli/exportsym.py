import pathlib

import click

import epcpm.parameterstohierarchy
import epcpm.project
import epcpm.symbolstosym


def relative_path(target, reference):
    reference = pathlib.Path(reference)
    if reference.is_file():
        reference = reference.parents[0]

    return pathlib.Path(target).resolve().relative_to(reference.resolve())


@click.command()
@click.option('--project', 'project_file', type=click.File(), required=True)
@click.option('--sym', 'sym_file', type=click.File('w'), required=True)
@click.option(
    '--hierarchy', 'hierarchy_file',
    type=click.File('w'),
    required=True,
)
def cli(project_file, sym_file, hierarchy_file):
    project = epcpm.project.load(project_file)

    sym_builder = epcpm.symbolstosym.builders.wrap(
        wrapped=project.models.symbols.root,
        parameter_uuid_finder=project.models.symbols.node_from_uuid,
    )

    hierarchy_builder = epcpm.parameterstohierarchy.builders.wrap(
        wrapped=project.models.parameters.root,
        symbol_root=project.models.symbols.root,
    )

    sym = sym_builder.gen()
    hierarchy = hierarchy_builder.gen(indent=4)

    sym_file.write(sym)
    hierarchy_file.write(hierarchy)
