"""
Lithium plating vs. anode thickness study.

Demonstrates that a thinner anode reduces electrolyte concentration gradients
during charging, lowering plating risk.

Uses PyBaMM's DFN model with varied negative electrode thickness at the
SAME absolute current (not same C-rate) to isolate the transport path effect.
"""

import pybamm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO

pybamm.set_logging_level("WARNING")

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
})

# ── Model & parameter setup ──────────────────────────────────────────────

model = pybamm.lithium_ion.DFN()
param = pybamm.ParameterValues("Chen2020")

L_n_baseline = param["Negative electrode thickness [m]"]
print(f"Baseline negative electrode thickness: {L_n_baseline*1e6:.1f} µm")

# Calculate baseline nominal capacity and 1.5C current
cap_model = pybamm.lithium_ion.DFN()
cap_sim = pybamm.Simulation(
    cap_model,
    parameter_values=param,
    experiment=pybamm.Experiment(["Discharge at C/20 for 30 hours or until 2.5 V"]),
)
cap_sol = cap_sim.solve()
Q_baseline_Ah = abs(cap_sol["Discharge capacity [A.h]"].entries[-1])
I_baseline_1p5C = 1.5 * Q_baseline_Ah
print(f"Baseline capacity: {Q_baseline_Ah:.2f} Ah")
print(f"Baseline 1.5C current: {I_baseline_1p5C:.2f} A")

# 3 cases: baseline, 70%, 50% thickness
# ALL at the same absolute current to isolate transport path effect
thickness_fracs = [1.0, 0.7, 0.5]
labels = [f"{f*100:.0f}% ({L_n_baseline*f*1e6:.0f} µm)" for f in thickness_fracs]
colors = ["#d62728", "#2ca02c", "#1f77b4"]

I_charge = I_baseline_1p5C
experiment = pybamm.Experiment(
    [
        f"Discharge at {I_charge:.4f} A for 60 minutes or until 2.5 V",
        "Rest for 5 minutes",
        f"Charge at {I_charge:.4f} A for 60 minutes or until 4.2 V",
    ],
)

# ── Run simulations ──────────────────────────────────────────────────────

solutions = []
for frac in thickness_fracs:
    p = param.copy()
    p["Negative electrode thickness [m]"] = L_n_baseline * frac
    sim = pybamm.Simulation(model, parameter_values=p, experiment=experiment)
    sol = sim.solve()
    charge_sol = sol.cycles[2].steps[0]
    solutions.append(charge_sol)
    eff_C = I_charge / (Q_baseline_Ah * frac)
    print(f"  Solved: thickness={frac:.0%}, eff. C-rate={eff_C:.1f}C")

# ── Extract and plot ─────────────────────────────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(12, 9))

snapshot_frac = 0.5

for i, (sol, frac, label, color) in enumerate(
    zip(solutions, thickness_fracs, labels, colors)
):
    t_all = sol["Time [s]"].entries
    t_start = t_all[0]
    t_rel = t_all - t_start

    t_eval = snapshot_frac * t_rel[-1]
    t_idx = np.argmin(np.abs(t_rel - t_eval))

    x = sol["x [m]"].entries[:, 0]
    c_e_var = sol["Electrolyte concentration [mol.m-3]"]
    c_e = c_e_var.entries[:, t_idx]

    x_norm = (x - x.min()) / (x.max() - x.min())
    t_min_rel = t_rel / 60.0

    axes[0, 0].plot(x * 1e6, c_e, color=color, linewidth=2, label=label)
    axes[0, 1].plot(x_norm, c_e, color=color, linewidth=2, label=label)

    V = sol["Voltage [V]"].entries
    axes[1, 0].plot(t_min_rel, V, color=color, linewidth=2, label=label)

    c_e_neg = sol["Negative electrolyte concentration [mol.m-3]"]
    c_e_neg_data = c_e_neg.entries
    c_e_at_sep = c_e_neg_data[-1, :]
    axes[1, 1].plot(t_min_rel, c_e_at_sep, color=color, linewidth=2, label=label)

# ── Format plots ─────────────────────────────────────────────────────────

for ax in axes.flat:
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.5)
        spine.set_color("#999999")
    ax.tick_params(direction="out", length=4, width=0.5, colors="#999999")

ax = axes[0, 0]
ax.set_xlabel("Position [µm]")
ax.set_ylabel("Electrolyte conc. [mol/m³]")
ax.set_title("Electrolyte Concentration Profile (mid-charge)")
ax.legend(title="Anode thickness", fontsize=9)

ax = axes[0, 1]
ax.set_xlabel("Normalized position across cell")
ax.set_ylabel("Electrolyte conc. [mol/m³]")
ax.set_title("Normalized Position (mid-charge)")
ax.legend(title="Anode thickness", fontsize=9)

ax = axes[1, 0]
ax.set_xlabel("Time [min]")
ax.set_ylabel("Voltage [V]")
ax.set_title(f"Terminal Voltage During Charge ({I_charge:.1f} A)")
ax.legend(title="Anode thickness", fontsize=9)

ax = axes[1, 1]
ax.set_xlabel("Time [min]")
ax.set_ylabel("Electrolyte conc. [mol/m³]")
ax.set_title("Electrolyte Conc. at Anode/Separator Interface")
ax.legend(title="Anode thickness", fontsize=9)

fig.suptitle(
    f"Effect of Anode Thickness on Electrolyte Concentration\n"
    f"(Same absolute current: {I_charge:.1f} A across all cases)",
    fontsize=14, fontweight="bold", y=1.02
)
fig.tight_layout()
fig.savefig(
    "/home/user/battsim/outputs/lithium_plating_thickness.png",
    dpi=150, bbox_inches="tight", facecolor="white", edgecolor="none",
)
print("Saved figure")

buf = BytesIO()
fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="white", edgecolor="none")
buf.seek(0)
img_b64 = base64.b64encode(buf.read()).decode("utf-8")

with open("/home/user/battsim/outputs/fig_b64.txt", "w") as f:
    f.write(img_b64)

print("Done.")
