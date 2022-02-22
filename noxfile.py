import nox_poetry


@nox_poetry.session(python=["3.9", "3.10"])
def lint(session):
    session.install(".", "pylint")
    session.run("pylint", "qlligraphy", "tests")


@nox_poetry.session(python=["3.9", "3.10"])
def black(session):
    session.install("black")
    session.run("black", "--check", ".")


@nox_poetry.session(python=["3.9", "3.10"])
def mypy(session):
    session.install("mypy")
    session.run("mypy", "qlligraphy")


@nox_poetry.session(python=["3.9", "3.10"])
def tests(session):
    session.install(".", "pytest", "coverage")
    session.run("coverage", "run", "-m", "pytest")
    session.run("coverage", "report")
