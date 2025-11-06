"""
命令行界面模块
"""

import click
from . import __version__
from .core import main_function


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
    
    result = main_function()
    click.echo(f'执行结果: {result}')


@cli.command()
def info():
    """显示程序信息"""
    click.echo(f'snake2 v{__version__}')
    click.echo('终端贪吃蛇游戏')


if __name__ == '__main__':
    cli()

