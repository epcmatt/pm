import pathlib
import textwrap

import click
import click.testing

import epcpm.cli.parameterstoc


parameters_path = (
    pathlib.Path(__file__).parents[0] / 'test_parameterstoc_parameters.json'
)


def test_():
    runner = click.testing.CliRunner()
    result = runner.invoke(
        epcpm.cli.parameterstoc.cli,
        [
            '--parameters', parameters_path,
        ],
    )
    assert result.exit_code == 0
    assert result.output == textwrap.dedent('''\
    struct GreenType_s
    {
      RedType red;
    };
    typedef struct GreenType_s GreenType_t;
    ''')