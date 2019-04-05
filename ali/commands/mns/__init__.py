import click

from ali.commands.mns.queue import queue


@click.group()
def mns():
    """Message Service (MNS)"""
    pass


@click.group()
def topic():
    """Topic commands"""
    pass


mns.add_command(queue)
# mns.add_command(topic)
