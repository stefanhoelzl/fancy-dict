from invoke import task

from tasks import doc
from tasks import tests
from tasks import release
from tasks import pip


@task(pre=[doc.clean, release.clean])
def clean(ctx):
    pass


@task(default=True, pre=[tests.unit, doc.build, release.build])
def local(ctx):
    pass


@task(pre=[pip.reset, tests.unit, doc.build, release.build])
def ci(ctx):
    pass
