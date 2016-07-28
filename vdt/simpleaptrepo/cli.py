import click

from vdt.simpleaptrepo.repo import SimpleAPTRepo
from vdt.simpleaptrepo.utils import platform_is_debian

apt_repo = SimpleAPTRepo()


@click.group()
def cli():
    pass


@cli.command(name='create-repo')
@click.argument('name')
@click.argument('path', default=".")
@click.option('--gpgkey', help='The GPG key to sign the packages with')
def create_repo(name, path, gpgkey=""):
    """Creates a repository"""
    try:
        apt_repo.add_repo(name, path, gpgkey)
    except ValueError as e:
        raise click.BadParameter(e.message)

    click.echo("Repository '%s' created" % name)
    click.echo("Now add a component with the 'addcomponent' command")


@cli.command(name='add-component')
@click.argument('name')
@click.argument('component', default="main")
def add_component(name, component):
    """Creates a component (ie, 'main', 'production')"""
    try:
        apt_repo.add_component(name, component)
    except ValueError as e:
        raise click.BadParameter(e.message)

    click.echo("Component '%s' created in repo '%s'" % (component, name))


@cli.command(name='update-repo')
@click.argument('name')
@click.argument('component', default="main")
def update_repo(name, component):
    """Updates a repo by scanning the debian packages
        and add the index files
    """
    try:
        repo_cfg = apt_repo.get_repo_config(name)
        component_path = apt_repo.get_component_path(name, component)
    except ValueError as e:
        raise click.BadParameter(e.message)

    gpgkey = repo_cfg.get('gpgkey', None)

    try:
        apt_repo.update_component(
            component_path, gpgkey, output_command=click.echo)
    except ValueError as e:
        raise click.UsageError(e.message)


@cli.command('list-repos')
def list_repos():
    """List currently configured repos"""
    repos = apt_repo.list_repos()
    for repo in repos:
        click.echo(repo.get('name'))
        for component in repo.get('components'):
            click.echo("   {0}".format(component))


def main():
    if platform_is_debian():
        cli()
    else:
        click.echo("You are not on debian or ubuntu, aborting!")

if __name__ == "__main__":
    main()
