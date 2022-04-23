# Contributing

👋 Want to add a contribution to **gitclone**? Feel free to send me a [pull request](https://github.com/evyli/gitclone/compare).

# Terminal Recording

The terminal recording is done with [Terminalizer](https://github.com/faressoft/terminalizer) by running:

```bash
terminalizer record demo
terminalier render demo.yml
```

The *demo.yml* file is slightly modified, e.g. modify some of the delays or omit lines at the beginning of the recording session. For the other values except for `records`, the current [file](https://github.com/evyli/gitclone/blob/master/img/terminalizer/demo.yml) can be used as a reference. The resulting gif as well as the recordings file are checked into the repository.

# How to Create Releases

A release commit should advance the version set in the *setup.py* file.

```python
setup_info = dict(
    name="gitclone",
    version="1.0.0",
    ...
)
```

The commit should also be tagged (annotated) with the version and the tag should be pushed to *github.com*:

```bash
git tag -a "v1.0.0" -m "Version v1.0.0"
git push --tags
```

After that a release should be published at *github.com/evyli* named as *v1.0.0* with a description describing the new features and fixes, e.g.:

```markdown
# Test release

## New features

- Some change
- Another change

## Bugfixes

- Some fix
- Another fix

## See also

**Full Changelog**: https://github.com/evyli/gitclone/commits/v1.0.0
```

Now create an account on https://pypi.org/account/register/

The package can be build and uploaded with:

```bash
pip install -r requirements-dev.txt
rm -rf dist
python setup.py sdist
twine upload dist/*
```