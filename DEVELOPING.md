## Running the tests

If using pyenv, ensure all minor Python versions >=3.6 are referenced in
`.python-version` (and reload your shell after making the change), then:

```console
$ tox
```

## Releasing

```console
$ python release.py <version>
```

## Building a development Docker image

```console
$ docker build -t ghcr.io/svaikstude/skippex:dev .
```

And later running this dev image:

```console
$ docker run --rm -v config:/data --network host ghcr.io/svaikstude/skippex:dev run
```

Running the tests inside it:

```console
$ docker run --rm -v config:/data --network host --entrypoint sh ghcr.io/svaikstude/skippex:dev -c ". /venv/bin/activate && python -m pytest"
```

Inspecting it with a shell:

```console
$ docker run --rm -v config:/data --network host --entrypoint sh -it ghcr.io/svaikstude/skippex:dev
```
