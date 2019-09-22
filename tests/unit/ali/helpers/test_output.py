import json

from unittest import mock

from ali.helpers.output import output_success, output_json, output_error


@mock.patch("ali.helpers.output.click")
def test_output_success(click):
    output_success("test")
    click.secho.assert_called_once_with("test", fg="green", bold=True)


@mock.patch("ali.helpers.output.click")
def test_output_error(click):
    output_error("test")
    click.secho.assert_called_once_with("Error: test", fg="red", bold=True)


@mock.patch("ali.helpers.output.formatters")
@mock.patch("ali.helpers.output.lexers")
@mock.patch("ali.helpers.output.highlight")
@mock.patch("ali.helpers.output.click")
def test_output_json(click, highlight, lexers, formatters):
    lexer_mock = mock.MagicMock()
    formatter_mock = mock.MagicMock()
    lexers.get_lexer_by_name.return_value = lexer_mock
    formatters.get_formatter_by_name.return_value = formatter_mock

    value = json.dumps({"test": {"items": [1, 2, 3]}})
    highlight.return_value = "highlighted"
    output_json(value)

    highlight.assert_called_once_with(
        json.dumps(json.loads(value), indent=4, sort_keys=True),
        lexer_mock,
        formatter_mock,
    )
    click.secho.assert_called_once_with("highlighted")
