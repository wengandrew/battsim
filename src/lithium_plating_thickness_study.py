"""
Lithium plating vs. anode thickness study.

Demonstrates that a thinner anode reduces electrolyte concentration buildup
at the separator/anode interface during charging, lowering plating risk.

Uses PyBaMM's DFN model with varied negative electrode thickness.
"""

import pybamm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO

pybamm.set_logging_level("WARNING")

# ── Model & parameter setup ──────────────────────────────────────────────

model = pybamm.lithium_ion.DFN()
param = pybamm.ParameterValues("Chen2020")

# Baseline negative electrode thickness
L_n_baseline = param["Negative electrode thickness [m]"]
print(f"Baseline negative electrode thickness: {L_n_baseline*1e6:.1f} µm")

# We'll run 3 cases: baseline, 70%, 50% thickness
thickness_fracs = [1.0, 0.7, 0.5]
labels = [f"{f*100:.0f}% ({L_n_baseline*f*1e6:.0f} µm)" for f in thickness_fracs]
colors = ["#d62728", "#2ca02c", "#1f77b4"]  # red, green, blue

# Discharge first to get to a low SOC, then charge at high C-rate
C_rate = 1.5
experiment = pybamm.Experiment(
    [
        "Discharge at 1C for 50 minutes or until 2.5 V",
        "Rest for 5 minutes",
        f"Charge at {C_rate}C for 40 minutes or until 4.2 V",
    ],
)

# ── Run simulations ──────────────────────────────────────────────────────

solutions = []
for frac in thickness_fracs:
    p = param.copy()
    p["Negative electrode thickness [m]"] = L_n_baseline * frac
    sim = pybamm.Simulation(model, parameter_values=p, experiment=experiment)
    sol = sim.solve()
    # Extract only the charging step (cycle index 2 in this API)
    charge_sol = sol.cycles[2].steps[0]
    solutions.append(charge_sol)
    print(f"  Solved for thickness fraction {frac:.0%}")

# ── Extract electrolyte concentration at a snapshot ──────────────────────

fig, axes = plt.subplots(2, 2, figsize=(12, 9))

# Pick a time ~50% through the charge for the snapshot
snapshot_frac = 0.5

for i, (sol, frac, label, color) in enumerate(
    zip(solutions, thickness_fracs, labels, colors)
):
    # Time relative to start of charge step
    t_all = sol["Time [s]"].entries
    t_start = t_all[0]
    t_rel = t_all - t_start  # seconds from start of charge

    t_eval = snapshot_frac * t_rel[-1]
    t_idx = np.argmin(np.abs(t_rel - t_eval))

    # Electrolyte concentration across cell at snapshot
    x = sol["x [m]"].entries[:, 0]
    c_e_var = sol["Electrolyte concentration [mol.m-3]"]
    c_e = c_e_var.entries[:, t_idx]

    # Normalize x to [0, 1] for comparison
    x_norm = (x - x.min()) / (x.max() - x.min())

    t_min_rel = t_rel / 60.0
    snapshot_t_min = t_rel[t_idx] / 60.0

    # Panel 1: Electrolyte concentration profiles (absolute x)
    axes[0, 0].plot(x * 1e6, c_e, color=color, linewidth=2, label=label)

    # Panel 2: Electrolyte concentration profiles (normalized x)
    axes[0, 1].plot(x_norm, c_e, color=color, linewidth=2, label=label)

    # Panel 3: Terminal voltage over time
    V = sol["Voltage [V]"].entries
    axes[1, 0].plot(t_min_rel, V, color=color, linewidth=2, label=label)

    # Panel 4: Anode electrolyte concentration at separator interface over time
    c_e_neg = sol["Negative electrolyte concentration [mol.m-3]"]
    c_e_neg_data = c_e_neg.entries
    # Last spatial point in negative electrode = separator interface
    c_e_at_sep = c_e_neg_data[-1, :]
    axes[1, 1].plot(t_min_rel, c_e_at_sep, color=color, linewidth=2, label=label)


# ── Format plots ─────────────────────────────────────────────────────────

# Panel 1
ax = axes[0, 0]
ax.set_xlabel("Position [µm]", fontsize=11)
ax.set_ylabel("Electrolyte conc. [mol/m³]", fontsize=11)
ax.set_title(f"Electrolyte Concentration Profile (mid-charge)", fontsize=12)
ax.legend(title="Anode thickness", fontsize=9)
ax.axvline(x=0, color="gray", linestyle="--", alpha=0.3)
ax.grid(True, alpha=0.3)

# Panel 2
ax = axes[0, 1]
ax.set_xlabel("Normalized position across cell [–]", fontsize=11)
ax.set_ylabel("Electrolyte conc. [mol/m³]", fontsize=11)
ax.set_title(f"Normalized Position (mid-charge)", fontsize=12)
ax.legend(title="Anode thickness", fontsize=9)
ax.grid(True, alpha=0.3)

# Panel 3
ax = axes[1, 0]
ax.set_xlabel("Time [min]", fontsize=11)
ax.set_ylabel("Voltage [V]", fontsize=11)
ax.set_title("Terminal Voltage During Charge", fontsize=12)
ax.legend(title="Anode thickness", fontsize=9)
ax.grid(True, alpha=0.3)

# Panel 4
ax = axes[1, 1]
ax.set_xlabel("Time [min]", fontsize=11)
ax.set_ylabel("Electrolyte conc. [mol/m³]", fontsize=11)
ax.set_title("Electrolyte Conc. at Anode/Separator Interface", fontsize=12)
ax.legend(title="Anode thickness", fontsize=9)
ax.grid(True, alpha=0.3)

fig.suptitle(
    f"Effect of Anode Thickness on Electrolyte Concentration During {C_rate}C Charge",
    fontsize=14, fontweight="bold", y=1.01
)
fig.tight_layout()
fig.savefig("/home/user/battsim/outputs/lithium_plating_thickness.png", dpi=150, bbox_inches="tight")
print("Saved figure to outputs/lithium_plating_thickness.png")

# ── Also save the figure as base64 for the HTML report ───────────────────
buf = BytesIO()
fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
buf.seek(0)
img_b64 = base64.b64encode(buf.read()).decode("utf-8")

with open("/home/user/battsim/outputs/fig_b64.txt", "w") as f:
    f.write(img_b64)

print("Done.")
