from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='fancy_dict',
    version='0.0.0',
    description='Dictionary extended by merge/load/query functions',
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
    ],
    keywords='dict merge yaml json',
    url='http://github.com/stefanhoelzl/fancy-dict',
    author='Stefan Hoelzl',
    author_email='stefan.hoelzl@posteo.de',
    license='MIT',
    packages=['fancy_dict'],
    install_requires=[
        'pyyaml'
    ],
    include_package_data=True,
    zip_safe=False
)
