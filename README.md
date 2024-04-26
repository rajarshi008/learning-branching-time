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
python -m pysmt install --<solver_name>
```
In the <solver_name> part, one can use different solvers that PySMT allows (z3, msat, cvc4 etc.)


## Usage

You can run basic usage of the learner using the following command:

```bash
python learn_formulas.py [-f INPUT_FILE] [-s FORMULA_SIZE] [-o OPERATORS]
```

We allow the following parameters for the learning algorithm:
| Short Option | Long Option     | Default Value | Description |
|--------------|-----------------|---------------|-------------|
| `-f`         | `--input_file`  | `sample_cgs.sp` | The input sample file |
| `-s`         | `--formula_size`| `20`          | The size upper of formula |
| `-o`         | `--operators`   | `[]`          | Choice of CTL/ATL operators |
| `-z`         | `--solver`      | `msat`        | Choice of (installed) solver |
| `-j`         | `--json_file`   | `metadata.json` | The json file to store metadata |
| `-g`         | `--game`        | `False`       | Input is a CGS sample file |
| `-a`         | `--atl`         | `False`       | Learn CTL instead of ATL |
| `-n`         | `--neg_props`   | `False`       | Using NNF syntax tree |
| `-w`         | `--without_until`| `False`      | Without Until operator |

For the format of the sample of structures, we refer the users to check the .sp files presented in the repository.