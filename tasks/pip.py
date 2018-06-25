from invoke import task, Collection


@task
def uninstall(ctx):
    ctx.run("pip freeze | xargs pip uninstall -y")
    ctx.run("pip install invoke")


@task
def install(ctx):
    ctx.run("pip install -r requirements-dev.txt")
    ctx.run("pip install -r requirements.txt")


@task(pre=[uninstall, install])
def reset(ctx):
    pass


ns = Collection(install, uninstall, reset)
