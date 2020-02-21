import json

import click
from pygments import highlight, lexers, formatters


def output_success(message):
    click.secho(message, fg="green", bold=True)


def output_json(json):
    click.secho(
        highlight(
            _format_response(json),
            lexers.get_lexer_by_name("json"),
            formatters.get_formatter_by_name("terminal"),
        )
    )


def output_text(output):
    click.echo(output)


def output_error(message):
    click.secho("Error: %s" % message, fg="red", bold=True)


def _format_response(response):
    return json.dumps(json.loads(response), indent=4, sort_keys=True)
