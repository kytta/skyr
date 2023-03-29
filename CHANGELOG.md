# Skyr / Change Log

## 0.2.0 - 2023-03-29

### Added

* [#9](https://github.com/kytta/skyr/issues/9):
  Allow execution of scripts from `./.skyr/`.

### Changed

* due to [#9](https://github.com/kytta/skyr/issues/9):
  script directory resolution logic was changed: if provided script dir doesn't
  exist, Skyr will fall back to `./.skyr/`, then `./script/`

## 0.1.1 - 2023-03-29

## Fixed

* [`80afa7e3`](https://github.com/kytta/skyr/commit/80afa7e3ca3e3de47a1d1129efe866c743049954):
  Fixed setuptools module discovery

## Behind-the-scenes

* [#7](https://github.com/kytta/skyr/pull/7):
  Eat our own dog food
  * this means, Skyr uses Skyr scripts ✨
* [#12](https://github.com/kytta/skyr/pull/12):
  Add GitHub Pages site

## 0.1.0 - 2023-02-07

## Added

- [#4](https://github.com/kytta/skyr/pull/4):
  Ability to run scripts inside `./script/`
