"""
命令行界面模块
"""

import click
from . import __version__
from .game import main_game_loop


@click.group()
@click.version_option(version=__version__)
def cli():
    """终端贪吃蛇游戏"""
    pass


@cli.command()
@click.option('--verbose', '-v', is_flag=True, help='显示详细输出')
def run(verbose):
    """运行主程序"""
    if verbose:
        click.echo('详细模式已启用')
    
    main_game_loop()


@cli.command()
def info():
    """显示程序信息"""
    click.echo(f'snake3 v{__version__}')
    click.echo('终端贪吃蛇游戏')


if __name__ == '__main__':
    cli()

