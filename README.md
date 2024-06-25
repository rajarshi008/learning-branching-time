# Learn-Branching-Time

LearnFormulas is a Python script that uses a learning algorithm to learn CTL (Computation Tree Logic) formulas and ATL formulas from samples of execution models.

## Requirements

This program has been written in Python 3.10. It relies on PySMT for SAT solving; it can access variety of popular SAT solvers (Z3, CVC4, etc.) that are provided with PySMT.

## Installation

- Clone this repository
   
- Create and activate a virtual python environment:
```
python3 -m venv venv
source venv/bin/activate
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

In the benchmark files, Kripke structures are represented as follows:
```
Intial state
---
Labels
---
Transitions
```
Concurrent Game structures are represented as follows:
```
Intial state
---
Labels with players
---
Transitions
---
Player set
```
The set of positive and negative examples are separated by `---\n---\n---`, while examples the both the sets is separated by `---\n---`


## Running experiments

For running the experiment presented in research paper, one can use the following script:
```bash
python rq_scripts.py [-e EXP_NUM] [-t TIMEOUT] [-a ALL]
```
with the following parameters:
| Short Option | Long Option     | Default Value | Description |
|--------------|-----------------|---------------|-------------|
| `-e`         | `--exp`  | `ctl` | Choice of experiment, `ctl`, `ctl_wu`, `atl`, `atl_tb` |
| `-t`         | `--timeout`| `900`          | Choice of timeout |
| `-a`         | `--all`   | `False`          | Whether to run on all benchmarks |

The choices of experiments `ctl`, `ctl_wu`, `atl`, `atl_tb` represent CTL learning, CTL learning without U (until) operator, ATL learning and ATL learning with turn-based encoding, the four experiments presented in the paper. By default, the experiments will run on a small subset of the entire benchmark suite.
Using option `-a` starts running the code on the entire benchmark suite, which can highly resource intensive. The entire set of experiments for the paper were run on several cluster machines using mutiple cores. The output will be generated in a csv file with a name corresponding to the experiment name.