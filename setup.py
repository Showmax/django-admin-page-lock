from __future__ import unicode_literals

import imp
import io
import os

from setuptools import find_packages, setup


def get_file_contents(filename):
    """Return file contents."""
    file_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), filename)

    with io.open(file_path, encoding="utf-8") as fd:
        return fd.read().strip().replace("\r", "")


def get_module():
    """Return module."""
    init_path = os.path.join(
        os.path.realpath(os.path.join(os.path.dirname(__file__))),
        "admin_page_lock",
        "__init__.py",
    )

    return imp.load_source("page_lock", init_path)


# Allow setup.py to be run from any path.
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    author="Vojtech Stefka",
    author_email="oss+djangopage@showmax.com",
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Framework :: Django :: 1.8",
        "Framework :: Django :: 1.9",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.0",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    description="Page Lock application prevents users from editing "
    "a page while it is being edited by someone else. "
    "The application is tailored to django admin implementation.",
    include_package_data=True,
    install_requires=[],
    keywords=["django", "admin", "locking", "concurrency"],
    license="Apache License, Version 2.0",
    long_description=get_file_contents("README.md"),
    long_description_content_type="text/markdown",
    name=get_module().NAME,
    packages=find_packages(),
    platforms=["any"],
    version=get_module().VERSION,
    url="https://github.com/ShowMax/django-admin-page-lock",
)
