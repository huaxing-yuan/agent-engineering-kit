# Sample app

A synthetic example for Agent Engineering Kit. It contains one domain module, a passing test suite, one durable decision, and one draft plan.

## Run

From the repository root:

```bash
python -m pip install -e .
aeng --root examples/sample-app check
aeng --root examples/sample-app docs check
aeng --root examples/sample-app report
python -m unittest discover -s examples/sample-app/tests -v
```

Or from this directory:

```bash
python -m pip install -e .
aeng check
aeng report
python -m unittest discover -s tests -v
```

The draft plan intentionally remains unlanded. It demonstrates how future work is tracked without pretending the work is complete.
