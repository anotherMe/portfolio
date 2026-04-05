
This is the [Textual](https://textual.textualize.io/) frontend for the [FastAPI bakend](backend/README.md).

# Running

After installing the package *textual-dev*, you can run your application with the `--dev` flag, which enables 
the [console](https://textual.textualize.io/guide/devtools/#console):

```sh
(.venv) textual run --dev main.py
```

In another terminal you should run:

```sh
(.venv) textual console
```

or, if you want to filter out some of the messages ( in this example, the EVENT messages ):

```sh
(.venv) textual console -x EVENT
```

# Debugging

If you like old style, breakpoint debugging, one of the possible methods is using [debugpy]().

Add something like this at the top of your app (or in a `if __name__ == "__main__":` block ):

```python
import debugpy

if "--debug" in sys.argv:
    debugpy.listen(("localhost", 5678))
    print("⏳ Waiting for debugger to attach...")
    debugpy.wait_for_client()
```

Then attach your IDE to the port above. For example, assuming VSCode is the IDE of choice, add a launch configuration like this:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Textual App",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/main.py",
      "console": "externalTerminal",
      "args": []
    }
  ]
}
```