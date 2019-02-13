import click
import json


def output_success(message):
    click.secho(message, fg="green", bold=True)


def output_json(json):
    click.secho(_format_response(json), fg="cyan")


def output_error(message):
    click.secho("Error - %s" % message, fg="red", bold=True)


def _format_response(response):
    return json.dumps(json.loads(response), indent=4, sort_keys=True)
