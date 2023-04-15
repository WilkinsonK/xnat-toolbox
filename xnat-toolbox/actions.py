#!python3
import pathlib, os, shutil, subprocess, sys
import typing

import click


def as_absolute(path: os.PathLike | str):
    return pathlib.Path(path).absolute()


def as_project(path: os.PathLike | str):
    return pathlib.Path(__file__).parent / path


def with_subprocess(cmd: typing.Iterable[str], strict: bool | None = None):
    # I'm not convinced stout & sterr from a SP
    # call gets directed to the root stdout &
    # sterr.
    # Paranoia is the best mechanism against
    # hubris.
    rcode = subprocess.call(cmd, stderr=sys.stderr, stdout=sys.stdout) #type: ignore[arg-type]
    if not rcode and strict:
        exit(rcode)


def callpy(*args: str, **kwds):
    with_subprocess([sys.executable, *args], **kwds)


def git(*args: str, **kwds):
    with_subprocess(["git", *args], **kwds)


class dir_context:
    _dir_stack: list[pathlib.Path] # LIFO

    @property
    def current(self):
        return self._dir_stack[-1]

    def push(self, path: os.PathLike | str):
        path = as_absolute(path)
        if not os.path.isdir(path):
            raise NotADirectoryError(f"{path!s} is not a directory.")
        if path == self.current:
            raise ValueError(f"{path!s} cannot push current path onto stack.")
        
        self._dir_stack.append(path) #type: ignore[arg-type]
        os.chdir(self.current)

    def pop(self):
        path = self._dir_stack.pop()
        os.chdir(path)

    def __init__(self, path: os.PathLike | str):
        self._dir_stack = [as_absolute(os.curdir)]
        self.push(path or os.curdir)

    def __enter__(self):
        return self

    def __exit__(self, t, v, tb):
        while len(self._dir_stack):
            self.pop()


@click.group()
def main_cli():
    """Actions available for this environment."""


@main_cli.command
@click.argument("project")
@click.option("-c", "--clean",
              is_flag=True,
              help="invalidates all build files.")
def build(project: str, *, clean: bool):
    """
    Builds a package distributable from the
    target project.
    """

    with dir_context(as_project(project)) as ctx:
        if clean:
            shutil.rmtree(ctx.current / "build")
            shutil.rmtree(ctx.current / "dist")
            shutil.rmtree(ctx.current / f"{project}.egg-info")

        callpy("-c",
               "import setuptools; setuptools.setup()",
               "sdist",
               "bdist_wheel")


@main_cli.command
@click.argument("project")
def publish(project: str):
    """
    Publish the target package. This command
    assumes that the project has been built.
    """

    with dir_context(as_project(project)) as ctx:
        callpy("-m", "twine", "upload", "dist/*")


if __name__ == "__main__":
    exit(main_cli())