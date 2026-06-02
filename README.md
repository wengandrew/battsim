# Battery Simulation Workspace

Andrew Weng

Simulation workspace for battery modeling using [PyBaMM](https://www.pybamm.org/) and related tools.

## Reports

HTML reports are published via GitHub Pages:

- [Lithium Plating vs. Anode Thickness](https://wengandrew.github.io/battsim/lithium_plating_thickness_report.html) — Why thinner anodes reduce plating risk during fast charge

## Project Structure

```
src/               Simulation scripts
docs/              HTML reports (GitHub Pages)
outputs/           Generated figures
*.ipynb            Exploratory Jupyter notebooks
```

## Getting Started

Set up a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run a simulation:

```bash
python3 src/lithium_plating_thickness_study.py
```

Or launch Jupyter for notebook-based exploration:

```bash
jupyter notebook
```

## Simulations

| Script | Description |
|--------|-------------|
| `src/lithium_plating_thickness_study.py` | DFN model study of anode thickness effect on electrolyte concentration and plating risk |
| `src/single_cell_eocv_r_rc.py` | Equivalent circuit model (OCV-R-RC) simulation |
