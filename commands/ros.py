import click


@click.group()
def ros():
    pass


@ros.command()
def create_stack():
    """Creates an ROS stack"""
    click.echo("Works like a charm!")
