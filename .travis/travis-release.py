import errno
import json
import logging
import os
import re
import shutil
import stat

from time import sleep

try:
    from urllib.request import urlretrieve, urlopen, Request
except ImportError:
    from urllib import urlretrieve
    from urllib2 import urlopen, Request


log = logging.getLogger(__name__)


DIST_DIR = 'dist'

BASE_GITHUB_API = 'https://api.github.com/repos'
GITHUB_RELEASES_TAGS = '{}/{}/releases/tags/{}'

BASE_APPVEYOR_API = 'https://ci.appveyor.com/api'
APPVEYOR_BUILD_HISTORY = '{}/projects/{}/history?recordsNumber=20'
APPVEYOR_BUILD_VERSION = '{}/projects/{}/build/{}'


class ReleaseException(Exception):
    """Base exception class for release errors."""


class ReleaseVersionException(ReleaseException):
    """Version mismatch between code and tagged release."""


class ApiTimeout(ReleaseException):
    """Could not reach API endpoint."""


class AppVeyorBuildFailed(ReleaseException):
    """Exception raised on failed build runs."""


class AppVeyorBuildCancelled(ReleaseException):
    """Exception raised on cancelled build."""


class AppVeyorBuildTimeout(ReleaseException):
    """Exception raised on build timeout."""


def download_file(url, path):
    """Download the target of url and store as local file in path."""
    log.info("Downloading: %s (into %s).", url, path)
    progress = [0, 0]

    def report(count, size, total):
        progress[0] = count * size
        if progress[0] - progress[1] > 1000000:
            progress[1] = progress[0]
            log.info("Downloaded %n/%n ...", progress[1], total)

    dest, _ = urlretrieve(url, path, reporthook=report)
    return dest


def api_request(url, token):
    """Send a request to API at url and decode the response as json."""
    response = None
    for i in range(3):
        try:
            log.info("Sending API request to '%s'.", url)
            request = Request(url)
            if token is not None:
                request.add_header('Authorization', 'token {}'.format(token))
            response = urlopen(request)
            break
        except Exception:
            log.exception("Failed to call API.")
        log.info("Retrying ...")
        sleep(i)
    if response is None:
        raise ApiTimeout("Could not reach API at '{}'.".format(url))

    try:
        charset = response.info().get_content_charset()
    except AttributeError:
        charset = response.info().getparam('charset')
        if not charset:
            charset = 'utf-8'
    data = json.loads(response.read().decode(charset))
    return data


def is_regular_dir(path):
    """Return non-zero if path is a directory."""
    try:
        mode = os.lstat(path).st_mode
    except os.error:
        mode = 0
    return stat.S_ISDIR(mode)


def force_remove_file_or_symlink(path):
    """Try to remove the file referenced by path. If it fails try again by
    setting write permission.
    """
    try:
        os.remove(path)
    except OSError:
        os.lchmod(path, stat.S_IWRITE)
        os.remove(path)


def remove_readonly(func, path, excinfo):
    """Error handling function for shutil.rmtree to try the file or directory
    remove operation again by setting write permission.

    Function taken from: https://stackoverflow.com/a/1889686
    """
    if func is os.rmdir:
        os.chmod(path, stat.S_IWRITE)
        os.rmdir(path)
    elif func is os.remove:
        os.lchmod(path, stat.S_IWRITE)
        os.remove(path)


def clear_dir(path):
    """Remove all files and directories from path. The path itself remains
    untouched.

    Function taken from: https://stackoverflow.com/a/24844618
    """
    if is_regular_dir(path):
        for name in os.listdir(path):
            fullpath = os.path.join(path, name)
            if is_regular_dir(fullpath):
                shutil.rmtree(fullpath, onerror=remove_readonly)
            else:
                force_remove_file_or_symlink(fullpath)
    else:
        raise OSError(errno.ENOTDIR, os.strerror(errno.ENOTDIR), path)


def download_github_tagged_release(path, url, tag, token):
    """Download all assets that belong to GitHub url for given tag.

    The local directory path is cleared of any existing files
    before downloading takes place.
    """
    filenames = []
    if os.path.exists(path):
        log.info("Clearing existing download path '%s'.", path)
        clear_dir(path)
    else:
        log.info("Creating download path '%s'.", path)
        os.makedirs(path)

    log.info("Retrieving GitHub assets for tag '%s'.", tag)
    data = api_request(url, token)
    for asset in data['assets']:
        download_file(asset['browser_download_url'],
                      os.path.join(path, asset['name']))
        filenames.append(asset['name'])
        sleep(5)
    return filenames


def check_appveyor_build_status(url, token):
    """Poll url for final build status for max 20 times with a three minute
    interval.
    """
    status = 'queued'
    for _ in range(20):
        data = api_request(url, token)
        build = data['build']
        status = build['status']
        if status in ('success', 'failed',
                      'cancelled', 'cancelling'):
            return status
        log.info("Build status of build with version '%s' and tag '%s' "
                 "is %s.", build['version'], build['tag'], status)
        sleep(180)
    return status


def check_appveyor_tagged_build(url, tag, token):
    """Examine the AppVeyor build history for any build with the specified
    tag. When the build still needs to finish keep polling for updates
    until done or timed out.

    Returns true when build is successful or raises an exception otherwise.
    """
    log.info("Retrieving AppVeyor build history.")
    data = api_request(url, token)
    status = 'unknown'
    for build in data['builds']:
        if build['isTag'] and build['tag'] == tag:
            status = build['status']
            if status in ('success', 'failed'):
                # Found a final state, no need to check prior builds.
                break
            elif status in ('cancelled', 'cancelling'):
                # Try to see if a prior build was successful.
                continue
            elif status in ('queued', 'running'):
                av_build_url = APPVEYOR_BUILD_VERSION.format(
                    BASE_APPVEYOR_API,
                    os.environ['TRAVIS_REPO_SLUG'],
                    build['version'])
                status = check_appveyor_build_status(av_build_url, token)
                break
    # Done checking build history, examine final status.
    if status == 'unknown':
        raise AppVeyorBuildTimeout("No build found for tag '{}'".format(tag))
    elif status == 'success':
        log.info("Build version '%s' with tag '%s' "
                 "was successful.", build['version'], tag)
        return True
    elif status in ('cancelled', 'cancelling'):
        raise AppVeyorBuildCancelled("Build version '{}' with tag '{}' was "
                                     "cancelled.".format(build['version'],
                                                         tag))
    elif status == 'failed':
        raise AppVeyorBuildFailed("Build version '{}' with tag '{}' "
                                  "failed.".format(build['version'],
                                                   tag))
    elif status in ('queued', 'running'):
        raise AppVeyorBuildTimeout("Build version '{}' with tag '{}' "
                                   "timed out.".format(build['version'],
                                                       tag))
    else:
        raise ReleaseException("Unrecognized status '{}' for build version "
                               "'{}' with tag '{}'.".format(status,
                                                            build['version'],
                                                            tag))


def check_code_version(filenames, tag):
    """Check if the asset filenames relate to the tag version.

    When tag is in the form v0.1.2 the first character is stripped.

    Raises ReleaseVersionException when the tag is not found in any
    of the asset file names.
    """
    if re.match(r"v\d+\.\d+\.\d+", tag) is not None:
        file_tag = tag[1:]
    else:
        file_tag = tag
    wheel_part = "-{}-".format(file_tag)
    targz_part = "-{}.tar.gz".format(file_tag)
    for filename in filenames:
        if (filename[-4:] == '.whl') and (wheel_part not in filename):
            log.error("Filename '%s' does not correspond "
                      "to tag '%s'.", filename, tag)
            raise ReleaseVersionException("Version mismatch "
                                          "between code and tag")
        if (filename[-7:] == '.tar.gz') and (targz_part not in filename):
            log.error("Filename '%s' does not correspond "
                      "to tag '%s'.", filename, tag)
            raise ReleaseVersionException("Version mismatch "
                                          "between code and tag")
    return True


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format="%(message)s")

    tag = os.environ['TRAVIS_TAG']
    gh_token = os.environ.get('GITHUB_API_TOKEN')
    av_token = os.environ.get('APPVEYOR_API_TOKEN')
    gh_url = GITHUB_RELEASES_TAGS.format(BASE_GITHUB_API,
                                         os.environ['TRAVIS_REPO_SLUG'],
                                         tag)
    av_url = APPVEYOR_BUILD_HISTORY.format(BASE_APPVEYOR_API,
                                           os.environ['TRAVIS_REPO_SLUG'])
    if check_appveyor_tagged_build(av_url, tag, av_token):
        log.info("Download assets for tagged release '%s'.", tag)
        filenames = download_github_tagged_release(DIST_DIR,
                                                   gh_url, tag,
                                                   gh_token)
        log.info("All assets downloaded for tagged release '%s'.", tag)
        check_code_version(filenames, tag)
