from invoke import task, Collection


@task(default=True)
def all(ctx):
    ctx.run("PYTHONPATH=. pytest tests", pty=True)


@task
def unit(ctx):
    ctx.run("PYTHONPATH=. pytest tests/unit", pty=True)


@task
def lint(ctx):
    ctx.run("PYTHONPATH=. pytest tests/lint", pty=True)


ns = Collection(unit, lint, all)
