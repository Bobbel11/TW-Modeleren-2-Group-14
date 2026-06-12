import pulp as lp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from collections import defaultdict

def _generate_distinct_colors(
    base_hex,
    n,
    hue_step=0.02,          
    sat_jitter=0.15,
    val_jitter=0.15,
    max_span=0.1           
):
    """
    Generate n visually distinct colors around a base color in HSV space.
    Hue spacing is consistent per step, but total span adapts to n.
    """
    base_rgb = np.array(mcolors.to_rgb(base_hex))
    base_hsv = np.array(mcolors.rgb_to_hsv(base_rgb.reshape(1, 1, 3))[0, 0])

    base_h, base_s, base_v = base_hsv

    if n == 1:
        return [mcolors.hsv_to_rgb([base_h, base_s, base_v])]

    # adaptive span based on number of colors
    span = min(hue_step * (n - 1), max_span)
    step = span / (n - 1)

    # center the group around base hue
    start_h = base_h - span / 2

    colors = []
    for i in range(n):
        h = (start_h + i * step) % 1.0

        s = np.clip(base_s + np.random.uniform(-sat_jitter, sat_jitter), 0.4, 1)
        v = np.clip(base_v + np.random.uniform(-val_jitter, val_jitter), 0.4, 1)

        rgb = mcolors.hsv_to_rgb([h, s, v])
        colors.append(rgb)

    return colors


def graph(x, durations, surgeries, dayno, roomno, capacity, keys):
    """
    keys[i] = surgery type (0–6)
    """

    # type base colors
    type_base_colors = {
        0: "#002d4e",  # Hart en vaat
        1: "#FAC000",  # Heup en knie
        2: "#005600",  # Laparoscopische
        3: "#910202",  # Overige buik
        4: "#5300a1",  # KNO
        5: "#4b3430",  # Keizersnede
        6: "#00CAE5",  # Staar/meniscus
    }

    # group surgeries by type
    type_to_indices = defaultdict(list)
    for i, t in enumerate(keys):
        type_to_indices[t].append(i)

    # assign distinct colors per surgery
    surgery_colors = [None] * len(surgeries)

    for t, idxs in type_to_indices.items():
        base = type_base_colors.get(t, "#7f7f7f")
        colors = _generate_distinct_colors(base, len(idxs))

        for i, c in zip(idxs, colors):
            surgery_colors[i] = c

    surgery_load = np.array([
        [[lp.value(x[i][r][t]) * durations.iloc[i]
          for i in range(len(surgeries))]
         for t in range(dayno)]
        for r in range(roomno)
    ])

    # plot
    fig, axes = plt.subplots(1, dayno, figsize=(5 * dayno, 6), sharey=True)
    if dayno == 1:
        axes = [axes]

    for t, ax in enumerate(axes):
        for r in range(roomno):
            bottom = 0

            for i in range(len(surgeries)):
                height = surgery_load[r][t][i]

                if height > 0:
                    ax.bar(
                        r,
                        height,
                        bottom=bottom,
                        color=surgery_colors[i],
                        edgecolor="white",
                        linewidth=0.5
                    )

                    ax.text(
                        r,
                        bottom + height / 2,
                        f"S{i+1}",
                        ha="center",
                        va="center",
                        fontsize=14,
                        color="white",
                        fontweight="bold"
                    )

                    bottom += height

        ax.axhline(capacity, color="black", linestyle="--", linewidth=1)
        ax.text(
            roomno-0.3,        # x position (right edge)
            capacity,            # y position (on the line)
            f"{capacity} min",
            color="red",
            fontsize=9,
            va="center",
            ha="left",
            fontweight="bold"
        )

        ax.set_title(f"Day {t+1}")
        ax.set_xticks(range(roomno))
        ax.set_xticklabels([f"Room {r+1}" for r in range(roomno)])
        ax.spines[["top", "right"]].set_visible(False)

    axes[0].set_ylabel("Minutes")
    fig.suptitle("Optimal surgery schedule with no additional rooms", fontsize=18)

    # legend
    type_labels = [
        "Cardiovascular",
        "Hip and knee",
        "Laparoscopic abdominal procedures",
        "Other abdominal surgery",
        "ENT (Ear, Nose, Throat)",
        "Cesarean section",
        "Cataract / meniscus surgery"
    ]

    type_handles = [
        plt.Rectangle((0, 0), 1, 1, color=c)
        for c in type_base_colors.values()
    ]

    fig.legend(
        type_handles,
        type_labels,
        loc="upper right",
        title="Surgery Types"
    )

    plt.show()