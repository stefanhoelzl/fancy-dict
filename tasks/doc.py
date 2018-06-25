from invoke import task, Collection


SOURCE = "docs"
TARGET = "{}/_build".format(SOURCE)


@task
def clean(ctx):
    ctx.run("rm -rf {}".format(TARGET), echo=True)


@task(clean, default=True)
def build(ctx):
    ctx.run("sphinx-build -W -b html {} {}".format(SOURCE, TARGET))
