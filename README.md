# Learn-Branching-Time

LearnFormulas is a Python script that uses a learning algorithm to learn CTL (Computation Tree Logic) formulas and ATL formulas from samples of execution models.

## Requirements

This program has been written in Python 3.10. It relies on PySMT for SAT solving; it can access variety of popular SAT solvers (Z3, CVC4, etc.) that are provided with PySMT.

## Installation

- Clone this repository
   
- Create a virtual python using the following:
```
python3 -m venv venv
```

- Install the requirements
```
pip install -r requirements.txt
python -m pysmt install --solver <solver_name>
```
In the <solver_name> part, one can use different solvers that PySMT allows (z3, msat, cvc4 etc.)


## Usage

You can run basic usage of the learner using the following command:

```bash
python learn_formulas.py [-f INPUT_FILE] [-s FORMULA_SIZE] [-o OPERATORS]
```