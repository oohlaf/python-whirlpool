"""
AppVeyor will at least have few Pythons around so there's no point of implementing a bootstrapper in PowerShell.

This is a port of https://github.com/pypa/python-packaging-user-guide/blob/master/source/code/install.ps1
with various fixes and improvements that just weren't feasible to implement in PowerShell.
"""
from __future__ import print_function

import logging

from os import environ
from os.path import exists
from subprocess import check_call

try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve


log = logging.getLogger(__name__)


BASE_URL = "https://www.python.org/ftp/python/"
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"
GET_PIP_PATH = "C:\get-pip.py"
URLS = {
    ("2.6", "64"): BASE_URL + "2.6.6/python-2.6.6.amd64.msi",
    ("2.6", "32"): BASE_URL + "2.6.6/python-2.6.6.msi",
    ("2.7", "64"): BASE_URL + "2.7.10/python-2.7.13.amd64.msi",
    ("2.7", "32"): BASE_URL + "2.7.10/python-2.7.13.msi",
    # NOTE: no .msi installer for 3.3.6
    ("3.3", "64"): BASE_URL + "3.3.3/python-3.3.5.amd64.msi",
    ("3.3", "32"): BASE_URL + "3.3.3/python-3.3.5.msi",
    ("3.4", "64"): BASE_URL + "3.4.3/python-3.4.6.amd64.msi",
    ("3.4", "32"): BASE_URL + "3.4.3/python-3.4.6.msi",
    ("3.5", "64"): BASE_URL + "3.5.0/python-3.5.3-amd64.exe",
    ("3.5", "32"): BASE_URL + "3.5.0/python-3.5.3.exe",
    ("3.6", "64"): BASE_URL + "3.6.0/python-3.6.0-amd64.exe",
    ("3.6", "32"): BASE_URL + "3.6.0/python-3.6.0.exe",
}
INSTALL_CMD = {
    # Commands are allowed to fail only if they are not the last command.  Eg: uninstall (/x) allowed to fail.
    "2.6": [["msiexec.exe", "/L*+!", "install.log", "/qn", "/x", "{path}"],
            ["msiexec.exe", "/L*+!", "install.log", "/qn", "/i", "{path}", "TARGETDIR={home}"]],
    "2.7": [["msiexec.exe", "/L*+!", "install.log", "/qn", "/x", "{path}"],
            ["msiexec.exe", "/L*+!", "install.log", "/qn", "/i", "{path}", "TARGETDIR={home}"]],
    "3.3": [["msiexec.exe", "/L*+!", "install.log", "/qn", "/x", "{path}"],
            ["msiexec.exe", "/L*+!", "install.log", "/qn", "/i", "{path}", "TARGETDIR={home}"]],
    "3.4": [["msiexec.exe", "/L*+!", "install.log", "/qn", "/x", "{path}"],
            ["msiexec.exe", "/L*+!", "install.log", "/qn", "/i", "{path}", "TARGETDIR={home}"]],
    "3.5": [["{path}", "/quiet", "TargetDir={home}"]],
    "3.6": [["{path}", "/quiet", "TargetDir={home}"]],
}


def download_file(url, path):
    log.info("Downloading: %s (into %s).", url, path)
    progress = [0, 0]

    def report(count, size, total):
        progress[0] = count * size
        if progress[0] - progress[1] > 1000000:
            progress[1] = progress[0]
            log.info("Downloaded %n/%n ...", progress[1], total)

    dest, _ = urlretrieve(url, path, reporthook=report)
    return dest


def install_python(version, arch, home):
    log.info("Installing Python %s for %s bit architecture to '%s'.",
             version, arch, home)
    if exists(home):
        return

    path = download_python(version, arch)
    log.info("Installing '%s' to '%s'.", path, home)
    success = False
    for cmd in INSTALL_CMD[version]:
        cmd = [part.format(home=home, path=path) for part in cmd]
        log.info("Running '%s'.", " ".join(cmd))
        try:
            check_call(cmd)
        except Exception as exc:
            log.exception("Failed command '%s'.", " ".join(cmd))
            if exists("install.log"):
                with open("install.log") as fh:
                    log.error(fh.read())
        else:
            success = True
    if success:
        log.info("Installation complete.")
    else:
        log.error("Installation failed.")


def download_python(version, arch):
    for _ in range(3):
        try:
            return download_file(URLS[version, arch], "installer.exe")
        except Exception as exc:
            log.exception("Failed to download.")
        log.info("Retrying ...")


def install_pip(home):
    pip_path = home + "/Scripts/pip.exe"
    python_path = home + "/python.exe"
    if exists(pip_path):
        log.info("pip already installed.")
    else:
        log.info("Installing pip.")
        download_file(GET_PIP_URL, GET_PIP_PATH)
        log.info("Executing: %s %s", python_path, GET_PIP_PATH)
        check_call([python_path, GET_PIP_PATH])


def install_packages(home, *packages):
    cmd = [home + "/Scripts/pip.exe", "install"]
    cmd.extend(packages)
    check_call(cmd)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    install_python(environ['PYTHON_VERSION'], environ['PYTHON_ARCH'], environ['PYTHON_HOME'])
    install_pip(environ['PYTHON_HOME'])
    install_packages(environ['PYTHON_HOME'], "setuptools>=36.4.0", "wheel")
