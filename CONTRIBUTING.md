# Contributing

👋 Want to add a contribution to **gitclone**? Feel free to send me a [pull request](https://github.com/leahevy/gitclone/compare).

---

# Terminal Recording

The terminal recording is done with [asciinema](https://asciinema.org/) by running:

```bash
asciinema rec
asciicast2gif FILENAME gitclone.gif
```

---

# Development

Please check the source code with `python setup.py pre_commit` before committing.

You can also use [pre-commit](https://github.com/pre-commit/pre-commit) for that by running:

```bash
pip install -e .[dev]
pre-commit install
```

Also regenerate the badges with `python setup.py badges` before committing.

---

# How to Create Releases

A release commit should advance the version set in the *VERSION* file.

```txt
1.0.0
```

The commit should also be tagged (annotated) with the version and the tag should be pushed to *github.com*:

```bash
git tag -a "v1.0.0" -m "Version v1.0.0"
git push --tags
```

After that a release should be published at *github.com/leahevy* named as *v1.0.0* with a description describing the new features and fixes, e.g.:

```markdown
# Version 1.0.0

## New features

- Some change
- Another change

## Bugfixes

- Some fix
- Another fix

## See also

**Full Changelog**: https://github.com/leahevy/gitclone/compare/v0.0.9...v1.0.0
```

Now create an account on https://pypi.org/account/register/

The package can be build and uploaded with:

```bash
pip install -r requirements-dev.txt
rm -rf dist
python setup.py sdist
twine upload dist/*
```