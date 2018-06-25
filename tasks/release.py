from invoke import task, Collection


@task
def build(ctx, dists=("sdist","bdist_wheel")):
    ctx.run("python setup.py {}".format(" ".join(dists)))


@task
def clean(ctx):
    ctx.run("rm -rf build dist fancy_dict.egg-info", echo=True)


@task(build, default=True)
def upload(ctx, test=True):
    test = "-r test" if test else ""
    ctx.run("twine upload {} dist/*".format(test))
