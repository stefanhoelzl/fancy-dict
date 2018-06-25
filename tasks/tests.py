from invoke import task, Collection


@task(default=True)
def unit(ctx):
    ctx.run("PYTHONPATH=. pytest tests", pty=True)


ns = Collection(unit)
