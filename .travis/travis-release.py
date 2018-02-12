import errno
import json
import os
import shutil
import stat

from time import sleep

try:
    from urllib.request import urlretrieve, urlopen
except ImportError:
    from urllib import urlretrieve, urlopen


BASE_GITHUB_API = 'https://api.github.com/repos'
GITHUB_RELEASES_TAGS = '{}/{}/releases/tags/{}'


BASE_APPVEYOR_API = 'https://ci.appveyor.com/api'
APPVEYOR_BUILD_HISTORY = '{}/projects/{}/history?recordsNumber=20'
APPVEYOR_BUILD_VERSION = '{}/projects/{}/build/{}'


class ReleaseException(Exception):
    """Base exception class for release errors."""


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
    print("Downloading: {} (into {}).".format(url, path))
    progress = [0, 0]

    def report(count, size, total):
        progress[0] = count * size
        if progress[0] - progress[1] > 1000000:
            progress[1] = progress[0]
            print("Downloaded {:,}/{:,} ...".format(progress[1], total))

    dest, _ = urlretrieve(url, path, reporthook=report)
    return dest


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


def api_request(url):
    """Send a request to API at url and decode the response as json."""
    response = None
    for _ in range(3):
        try:
            print("Sending API request to '{}'.".format(url))
            response = urlopen(url)
            break
        except Exception as exc:
            print("Failed to call API:", exc)
        print("Retrying ...")
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


def download_github_tagged_release(path, url, tag):
    """Download all assets that belong to GitHub url for given tag.

    The local directory path is cleared of any existing files
    before downloading takes place.
    """
    if os.path.exists(path):
        print("Clearing existing download path '{}'.".format(path))
        clear_dir(path)
    else:
        print("Creating download path '{}'.".format(path))
        os.makedirs(path)

    print("Retrieving GitHub assets for tag '{}'.".format(tag))
    data = api_request(url)
    for asset in data['assets']:
        download_file(asset['browser_download_url'],
                      os.path.join(path, asset['name']))


def check_appveyor_build_status(url):
    """Poll url for final build status for max 30 times with a one minute
    interval.
    """
    status = 'queued'
    for _ in range(30):
        data = api_request(url)
        build = data['build']
        status = build['status']
        if status in ('success', 'failed',
                      'cancelled', 'cancelling'):
            return status
        print("Build status of build with version '{}' and tag '{}' "
              "is {}.".format(build['version'], build['tag'], status))
        sleep(60)
    return status


def check_appveyor_tagged_build(url, tag):
    """Examine the AppVeyor build history for any build with the specified
    tag. When the build still needs to finish keep polling for updates
    until done or timed out.

    Returns true when build is successful or raises an exception otherwise.
    """
    print("Retrieving AppVeyor build history.")
    data = api_request(url)
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
                status = check_appveyor_build_status(av_build_url)
                break
    # Done checking build history, examine final status.
    if status == 'unknown':
        raise AppVeyorBuildTimeout("No build found for tag '{}'".format(tag))
    elif status == 'success':
        print("Build version '{}' with tag '{}' "
              "was successful.".format(build['version'], tag))
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


if __name__ == '__main__':
    tag = os.environ['TRAVIS_TAG']
    gh_url = GITHUB_RELEASES_TAGS.format(BASE_GITHUB_API,
                                         os.environ['TRAVIS_REPO_SLUG'],
                                         tag)
    av_url = APPVEYOR_BUILD_HISTORY.format(BASE_APPVEYOR_API,
                                           os.environ['TRAVIS_REPO_SLUG'])
    if check_appveyor_tagged_build(av_url, tag):
        print("Download assets for tagged release '{}'.".format(tag))
        download_github_tagged_release('release', gh_url, tag)
        print("All assets downloaded for tagged release '{}'.".format(tag))
