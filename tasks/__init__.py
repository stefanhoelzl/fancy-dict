from invoke import Collection
from tasks import make, doc, tests, release, pip


ns = Collection(make, doc, tests, release, pip)
