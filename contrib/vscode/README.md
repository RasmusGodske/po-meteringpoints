Configuration for VS Code
=========================

[VS Code](https://code.visualstudio.com/) requires additional configuration for Python. 

In order to get the VS Code testing up and running, first copy the content of `settings.json` into `.vscode/`, then copy the contents of the `.env.test` into the root of the project as `.env.test` this makes sure that pytest runs the tests within `tests/` with  `src/` as the current working directory. This is required for the test modules to find source code. See [Use of the PYTHONPATH variable](https://code.visualstudio.com/docs/python/environments#_use-of-the-pythonpath-variable).

## Copy files to project
```bash
mkdir .vscode
cp ./contrib/vscode/settings.json .vscode/settings.json
cp ./contrib/vscode/.env.test .env.test
```