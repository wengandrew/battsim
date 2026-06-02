# battsim

Battery simulation workspace using PyBaMM and related tools.

## Project structure

```
src/               Python simulation scripts
outputs/           Generated figures (PNG)
docs/              HTML reports served via GitHub Pages
*.ipynb            Jupyter notebooks (exploratory analyses)
requirements.txt   Python dependencies
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running simulations

```bash
source venv/bin/activate
python3 src/<script>.py
```

Jupyter notebooks:
```bash
jupyter notebook
```

## Key dependencies

- **PyBaMM** — electrochemical battery models (DFN, SPMe, SPM)
- **liionpack** — pack-level simulation
- **matplotlib** — plotting
- **numpy / scipy** — numerical computing

## Conventions

- Simulation scripts go in `src/`
- Generated figures go in `outputs/`
- HTML reports go in `docs/` (served via GitHub Pages)
- Notebooks are date-prefixed: `YYYY_MM_DD_<description>.ipynb`
- Parameter sets: prefer `Chen2020` unless a specific chemistry is needed
