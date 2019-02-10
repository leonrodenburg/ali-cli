import click

from commands.ros import ros


@click.group()
def cli():
    """Ali CLI"""
    pass


cli.add_command(ros)


if __name__ == "__main__":
    cli()
