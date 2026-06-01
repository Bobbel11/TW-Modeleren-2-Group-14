import matplotlib.pyplot as plt
import numpy as np


# collect per-room overtime from the solution
def graph(x, durations, surgeries, dayno, roomno, capacity):
    surgery_load = np.array([
        [[lp.value(x[i][r][t]) * durations.iloc[i] for i in range(len(surgeries))]
        for t in range(dayno)]
        for r in range(roomno)
    ])

    fig, axes = plt.subplots(1, dayno, figsize=(5 * dayno, 6), sharey=True)
    if dayno == 1:
        axes = [axes]

    cmap = plt.get_cmap("tab20")
    surgery_colors = [cmap(i % 20) for i in range(len(surgeries))]

    for t, ax in enumerate(axes):
        for r in range(roomno):
            bottom = 0
            for i in range(len(surgeries)):
                height = surgery_load[r][t][i]
                if height > 0:
                    ax.bar(r, height, bottom=bottom, color=surgery_colors[i], edgecolor="white", linewidth=0.5)
                    ax.text(r, bottom + height / 2, f"S{i+1}", ha="center", va="center", fontsize=7, color="white")
                    bottom += height

        # draw capacity line
        ax.axhline(capacity, color="black", linestyle="--", linewidth=1, label="Capacity")
        ax.text(roomno - 0.5, capacity + 2, f"{capacity} min", color="red", fontsize=8, va="bottom", ha="left")
        ax.set_title(f"Day {t+1}")
        ax.set_xticks(range(roomno))
        ax.set_xticklabels([f"Room {r+1}" for r in range(roomno)])
        ax.spines[["top", "right"]].set_visible(False)

    axes[0].set_ylabel("Minutes")
    fig.suptitle("Surgery schedule per room per day (ILP)", y=0.95, fontsize=20)

    # legend
    handles = [plt.Rectangle((0,0),1,1, color=surgery_colors[i]) for i in range(len(surgeries))]
    labels = [f"S{i+1}: {surgeries.iloc[i]}" for i in range(len(surgeries))]
    fig.legend(handles, labels, loc="center right", bbox_to_anchor=(1.15, 0.5), fontsize=8, title="Surgery")

    plt.show()