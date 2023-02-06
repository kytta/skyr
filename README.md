# Skyr

> Low-fat task runner.

Skyr is a task runner, similar to Make. Just like Make, it can have tasks that
depend on each other and are executed only if a file changes. But, unlike Make,
Skyr doesn't actually have to be installed on your machine to run. That's
because Skyr uses Shell scripts to define build commands and looks for special
comments for special features. This means you can very easily integrate Skyr
into your existing project.

## Install

### Using `pipx` (recommended)

```sh
pipx install skyr
```

### Using plain `pip`

```sh
pip install --user skyr
```

## Drop-in executable

```sh
wget "https://raw.githubusercontent.com/kytta/skyr/main/skyr.py"
```

## Usage

For example, to execute `script/test`:

```sh
skyr test
```

If you don't provide the script name, it will default to `build`:

```sh
skyr  # same as 'skyr build'
```

By default, Skyr searches for your scripts inside `./script`. To change that,
use `--script-dir`:

```sh
skyr --script-dir ./dev/ test
```

## Roadmap

- [x] Basic script running: Run .sh, .bash, .zsh, and other files from the
      `script/` directory.
- [ ] Target dependencies: Run scripts if other depend on them.
- [ ] Dependency age: Run scripts only if the files it depends on changed.
- [ ] Script validation: Check that Skyr understands the scripts it was given.
- [ ] Make mode: Support running very basic Makefiles.
- [ ] Make migration mode: Support migrating from a Makefile to a `script/`
      directory.
- [ ] Just mode: Support running very basic Justfiles.
- [ ] Just migration mode: Support migrating from `just` to a `script/`
      directory.

## Licence

© 2023 [Nikita Karamov]\
Code licensed under the [ISC License].

---

This project is hosted on GitHub:
<https://github.com/kytta/skyr.git>

[isc license]: https://spdx.org/licenses/ISC.html
[nikita karamov]: https://www.kytta.dev/
