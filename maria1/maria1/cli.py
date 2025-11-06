"""
命令行界面模块
"""

import click
from . import __version__
from .game import main_game_loop


@click.group()
@click.version_option(version=__version__)
def cli():
    """命令行版超级玛丽游戏"""
    pass


@cli.command()
@click.option('--verbose', '-v', is_flag=True, help='显示详细输出')
def run(verbose):
    """运行主程序"""
    if verbose:
        click.echo('详细模式已启用')
    
    try:
        main_game_loop()
    except Exception as e:
        click.echo(f'错误: {e}', err=True)
        click.echo('提示: 此游戏需要在交互式终端中运行（不支持非交互式环境）', err=True)
        click.echo('请在真正的终端中运行: python -m maria1 run', err=True)


@cli.command()
def info():
    """显示程序信息"""
    click.echo(f'maria1 v{__version__}')
    click.echo('命令行版超级玛丽游戏')


if __name__ == '__main__':
    cli()

