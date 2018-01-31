# Whirlpool ChangeLog

## [Unreleased]

### Added
- Port to Python 3.

### Fixed
- Fix struct function declaration prototype warnings.
- Fix pointer warnings.

### Changed
- Started using [semantic versioning][semver] together with
  [keep a changelog][keepachangelog].
- Restructured package setup.

### Deprecated
- Removed the old deprecated `hash()` interface.

## [0.3] - 2013-01-23

### Added
- Added the same interface as other Python digest algorithms (hashlib).

### Changed
- Created proper unit tests.

### Deprecated
- The `hash()` function is deprecated. Please transition to the hashlib
  interface and use `new()` and `hexdigest()`.

## 0.2 - Never released

## [0.1] - 2011-05-18

### Added
- Initial commit.

[Unreleased]: https://github.com/oohlaf/python-whirlpool
[0.3]: https://github.com/oohlaf/python-whirlpool
[0.1]: https://github.com/oohlaf/python-whirlpool
[semver]: https://semver.org/spec/v2.0.0.html
[keepachangelog]: http://keepachangelog.com/en/1.0.0/
