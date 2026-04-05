# CPDS

Branch-and-cut implementation for PMU placement style models over power-network
graphs with channel limitations, based on forbidden propagation sets.

## Requirements

- Linux
- g++ with C++20 support
- Gurobi (C++ API)
- Boost Program Options
- Local dependencies in _deps:
  - fmt
  - tinyxml2

The current Makefile assumes Gurobi 12.0.3 under:

- /opt/gurobi1203/linux64

If your local install differs, update [Makefile](Makefile).

## Build

From the project root:

```bash
make
```

The deps target is executed automatically and builds:

- _deps/fmt
- _deps/tinyxml2

The resulting executable is:

- pds-lim

## Input Format

Inputs are GraphML files passed through -f/--graph.

Example:

```bash
./pds-lim -s brimkov -w 5 -f inputs/case_ieee30.graphml
```

## Usage

General syntax:

```bash
./pds-lim -s SOLVER -w N_CHANNELS -f FILE1 [FILE2 ...] [options]
```

Main solver options:

- brimkov
- jovanovic
- fpss
- efpss
- forts

## Main Parameters

- -h, --help: show help
- -s, --solver: solver name
- -w, --n-channels: number of channels
- -f, --graph: input GraphML files (multi-token)
- -z, --all-zi: treat all nodes as zero-injection
- -n, --repeat: number of repetitions (default 1)
- -t, --timeout: Gurobi time limit in seconds (default 3600)
- -o, --outdir: output directory (optional)

Constraint/callback toggles:

- --in-prop
- --out-prop
- --init-efps
- --lazy-max

For the full list:

```bash
./pds-lim --help
```

## Output Behavior

Without --outdir:

- logs and solution details are printed to stdout

With --outdir DIR:

- output subfolders are created under DIR:
  - log/
  - stat/
  - sol/
  - cb/

The program also supports resume behavior by skipping runs that already have
their .stat file.

## Experiments

Project scripts are available in [experiments](experiments). A typical batch run
pattern is:

```bash
cd experiments
nohup ./script1.sh &
```

Solver outputs are written to `outputs/` (one subfolder per script). Once runs are
complete, aggregate the per-instance `.stat` files into a single CSV using:

```bash
python stats.py ../outputs/exp1/ stats1.csv
```

The full experimental results are available in
[experiments/stats1.csv](experiments/stats1.csv),
[experiments/stats2.csv](experiments/stats2.csv),
[experiments/stats3.csv](experiments/stats3.csv), and
[experiments/stats4.csv](experiments/stats4.csv).
Analysis plots are generated in
[experiments/analysis.ipynb](experiments/analysis.ipynb).

## Project Structure

- [main.cpp](main.cpp): program entry and CLI parsing
- [src](src): model/solver implementations
- [include](include): headers
- [inputs](inputs): GraphML instances
- [experiments](experiments): experiment scripts and analysis
- [Makefile](Makefile): build configuration

## License

See [LICENSE](LICENSE).