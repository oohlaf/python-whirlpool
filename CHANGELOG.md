# Whirlpool ChangeLog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog][keepachangelog] and this
project adheres to [Semantic Versioning][semver].

## [Unreleased]

### Added

- Port to Python 3.
- Added PyPy support (PyPy3 does not work due to functions
  that have not yet been ported, like `PyUnicode_New`).
- Added Continuous Integration using Travis CI and AppVeyor.
- Added automatic upload to PyPI on successful build tags.

### Fixed

- Fix struct function declaration prototype warnings.
- Fix pointer warnings.

### Changed

- Package ownership transferred to Olaf Conradi.
- Started using [Semantic Versioning][semver] together with
  [Keep a Changelog][keepachangelog].
- Restructured package setup and distribution scripts.

### Deprecated

- Removed the old deprecated `hash()` interface.

## [0.3] (2013-01-23)

### Added

- Added the same interface as other Python digest algorithms have
  (like the default `hashlib` module).

### Changed

- Created proper unit tests.

### Deprecated

- The `hash()` function is deprecated. Please transition to the hashlib
  interface and use `new()` and `hexdigest()`.

## 0.2 (unreleased)

- This release was skipped.

## 0.1 (2011-05-18)

### Added

- Initial commit by James Cleveland.

[Unreleased]: https://github.com/oohlaf/python-whirlpool/compare/v0.3...HEAD
[0.3]: https://github.com/oohlaf/python-whirlpool/compare/v0.1...v0.3
[semver]: https://semver.org/spec/v2.0.0.html
[keepachangelog]: http://keepachangelog.com/en/1.0.0/
