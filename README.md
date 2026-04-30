# YAML to QTI converter.

This application is intended to run a simple Flask application with the purpose of ingesting YAML files (and potentially .zip files) in a predictable format to produce QTI-compatible import packages.

## Setup and installation

### Local dev with pyenv

[Install pyenv](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation).

[Install pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv?tab=readme-ov-file#installation).

Using `pyenv`, make sure the required version of Python is installed and available. This may change over time.

Keep in mind also that the following exports may be necessary in order to properly enable pyenv:
```
# pyenv
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
```

Make sure [make](https://www.gnu.org/software/make/manual/make.html) is installed. Typically you can confirm this by checking the output of `which make` in *nix systems. Otherwise, it's up to you to determine how to use Makefiles on your operating system.

Using `pyenv` and `virtualenv` is recommended regardless of which option you use to run the Flask application, as it will enable you to also use the provided pre-commit hooks that maintain code cleanliness.

Several `make` commands are provided for your convenience:
 * `make dev-check` will check to ensure that the requisite tools `pyenv` and `pyenv-virtualenv` are installed, as well as the required version of Python. If any of the prerequisites are unavailable, you will be notified.
 * `make dev-setup` will, assuming all requirements in `dev-check` pass, automatically create a local dev environment with `pyenv` and `virtualenv`, install all necessary Python packages, and install pre-commit hooks.
 * `make run-local` will, assuming all necessary Python dependencies have been installed, start a local Flask development server.
 * `make start` will start a Flask application server within Docker containers, building the containers if necessary.

Run `make help` to see a full list of commands that will simplify linting your code, running migrations, or starting interactive shell sessions within the container.

### Development

In order to use the local Flask development server, you must also install the application's dependencies alongside the dev environment's dependencies - for convenience, you may do this by running the `make dev-setup-local` command.

You may run the application locally for dev purposes in one of two ways.

#### Flask dev server

You can run the application using the built-in Flask development server via the `make run-local` command (assuming you have set up a pyenv-virtualenv development environment). This will enable frequent and rapid changes to the code while still in development, and can be done without additional Docker setup.

In local virtual environment mode, the application will be available in your browser at http://localhost:5000.

#### Docker container

You may also choose to use the `make start-dev` command (or one of the more specific `start-dev-` commands, as you prefer) to run the application in a Docker container - this will (eventually) more closely mimic the non-development implementation of the application in order to potentially catch any issues specific to running the application alongside NGINX, but is less readily usable than the Flask local development server and may require some understanding of Docker and application containerization.

In Docker mode, the application will be available in your browser at at http://localhost/yaml-to-qti.

##### Cleanup

You may choose to remove any created Docker assets with one of several cleanup commands - `make clean` to remove the containers, `make clean-volumes` to also remove created volumes, and `make clean-volumes-images` to also remove any built Docker images.

### Pre-commit hooks

It is recommended to run the `make dev-setup` command to install pre-commit hooks which should automatically check your Python code prior to allowing git commits.