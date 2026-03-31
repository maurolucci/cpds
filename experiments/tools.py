import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import functools
from math import ceil, isnan
import numpy as np
import perfprof as pp

# Global plot style
sns.set_style("whitegrid")
sns.set_context("paper")
sns.set_palette("deep")


def merge2_dataframes(data, solvers):
    datas = [data[data.solver == solver] for solver in solvers]
    data2 = datas[0].copy()
    for i in range(1, len(solvers) - 1):
        data2 = data2.merge(
            datas[i],
            on=["instance", "vertices", "edges", "propagating_vertices", "k"],
            suffixes=["", "_" + solvers[i]],
        )
    data2 = data2.merge(
        datas[len(solvers) - 1],
        on=["instance", "vertices", "edges", "propagating_vertices", "k"],
        suffixes=["_" + solvers[0], "_" + solvers[len(solvers) - 1]],
    )
    return data2


# First criterior: most solved instances
# Second criterion: lowest execution time
# Third criterion: lowest upper bound
# Fourth criterion: greatest lower bound
def compare(t1, t2):
    if t1[1] > t2[1]:
        return -1
    elif t1[1] < t2[1]:
        return 1
    if t1[2] < t2[2]:
        return -1
    elif t1[2] > t2[2]:
        return 1
    if t1[3] < t2[3]:
        return -1
    elif t1[3] > t2[3]:
        return 1
    if t1[4] > t2[4]:
        return -1
    elif t1[4] < t2[4]:
        return 1
    return 0


def get_tuple(serie, solver):
    return (
        serie["solver_" + solver],
        serie["result_" + solver],
        serie["time_opt_" + solver],
        serie["upper_bound_" + solver],
        serie["lower_bound_" + solver],
    )


def get_winner(serie, solvers):
    ls = [get_tuple(serie, solver) for solver in solvers]
    ls = sorted(ls, key=functools.cmp_to_key(compare))
    if compare(ls[0], ls[1]) == 0:
        return "tie"
    return ls[0][0]


def get_result_winner(serie):
    winner = serie.winner
    if winner == "tie":
        return 0
    result = serie["result_" + winner]
    return result


def show_best_solver(data, solvers, colors, markers, success=False):

    # Get winner solver
    data = merge2_dataframes(data, solvers)
    data["winner"] = data.apply(get_winner, solvers=solvers, axis=1)
    data["result_winner"] = data.apply(get_result_winner, axis=1)
    data2 = data.groupby("winner", as_index=False).agg(number=("instance", "count"))
    data2 = data2.sort_values(by="number")

    name = ""
    for solver in solvers:
        name += "_" + solver

    # Scatterplot
    fig, ax = plt.subplots(
        1, 2, figsize=(6.25, 5), gridspec_kw={"width_ratios": [20, 1]}
    )
    if not success:
        sns.scatterplot(
            x=data.instance,
            y=data.k,
            hue=data.winner,
            hue_order=np.sort(data.winner.unique()),
            palette=colors,
            style=data.winner,
            markers=markers,
            s=70,
            ax=ax[0],
        )
        ax[0].legend()
    else:
        sns.scatterplot(
            x=data.instance,
            y=data.k,
            hue=data.winner,
            hue_order=np.sort(data.winner.unique()),
            palette=colors,
            style=data.winner,
            markers=markers,
            size=data.result_winner,
            sizes=(40, 100),
            s=80,
            ax=ax[0],
        )

        solvers = np.sort(data.winner.unique())
        handles, labels = ax[0].get_legend_handles_labels()
        model_labels = [model for model in solvers]
        model_handles = handles[1 : len(solvers) + 1]
        opt_labels = [f"{i*20}%" for i in sorted(data.result_winner.unique())]
        opt_handles = handles[len(solvers) + 2 :]

        # Create and position separate legends
        legend_opt = ax[0].legend(
            opt_handles, opt_labels, title="Optimality", loc="upper left"
        )
        legend_model = ax[0].legend(
            model_handles,
            model_labels,
            title="Model",
            loc="upper left",
            bbox_to_anchor=(0.2, 1),
        )

        # Add the species legend back as creating the second legend replaces the first
        ax[0].add_artist(legend_opt)

    # Put the legend out of the figure
    ax[0].grid(alpha=0.5, zorder=-1, axis="y")
    ax[0].tick_params("x", rotation=90)

    # Barplot
    data["x"] = ""
    sns.histplot(
        data=data,
        x="x",
        hue="winner",
        hue_order=np.sort(data.winner.unique()),
        palette=colors,
        multiple="fill",
        stat="proportion",
        discrete=True,
        legend=False,
        ax=ax[1],
    )
    ax[1].set_xlabel("")
    ax[1].set_ylabel("")
    ax[1].set_yticks([])
    for container in ax[1].containers:
        # Create custom labels: show value if above threshold, else empty string
        custom_labels = [f"{v:.1%}" if v >= 0.01 else "" for v in container.datavalues]
        ax[1].bar_label(container, labels=custom_labels, label_type="center")

    plt.savefig("figs/scatter-best" + name + ".pdf", format="pdf", bbox_inches="tight")
    plt.show()
    plt.show()


def show_execution_time(data, solvers, colors, markers, log_scale: bool = False):
    data = data[data.solver.isin(solvers)]
    plt.figure(figsize=(6, 5))
    sns.lineplot(
        data=data,
        x="instance",
        y="t_solver",
        hue="solver",
        style="solver",
        palette=colors,
        markers=markers,
        errorbar=None,
        linewidth=2,
        markersize=5,
    )
    if log_scale:
        plt.yscale("log")
    plt.ylim(top=1000)
    plt.ylabel("time (s)")
    plt.xticks(rotation=90)
    plt.legend(title="Model")
    name = ""
    for solver in solvers:
        name += "_" + solver
    plt.savefig("figs/time" + name + ".pdf", format="pdf", bbox_inches="tight")
    plt.show()


def show_execution_time_grid(
    data, solvers,  colors, markers, n, cols, legend_xpos=0.5, log_scale: bool = False, sharey=True
):
    instances = data.instance.unique()
    alt_seq = range(len(instances) - 1, -1, -max(1, int(len(instances) / n)))
    finstances = [instances[i] for i in alt_seq]
    finstances = finstances[:n]
    finstances.reverse()

    data = data[(data.solver.isin(solvers)) & (data.instance.isin(finstances))]
    g = sns.FacetGrid(data, col="instance", col_wrap=cols, sharex=False, sharey=sharey)
    g.map_dataframe(
        sns.lineplot,
        "k",
        "t_solver",
        errorbar=None,
        hue="solver",
        style="solver",
        palette=colors,
        markers=markers,
        linewidth=1.5,
        markersize=4,
    )
    if log_scale:
        g.set(yscale="log")
    # for ax in g.axes.flat:
    #    ax.legend()
    g.add_legend(
        title="Model",
        ncol=len(solvers),
        loc="upper center",
        bbox_to_anchor=(legend_xpos, 1.05),
    )
    g.set_axis_labels("k", "time (s)")
    name = ""
    for solver in solvers:
        name += "_" + solver
    plt.savefig("figs/time_grid" + name + ".pdf", format="pdf", bbox_inches="tight")

def show_cumulative_gap(data, solvers, colors, log_scale: bool = False, xlim: tuple[float, float] = (10e-4, 1), ylim: tuple[float, float] = (0, 1)):
    data = data[data.solver.isin(solvers)]
    plt.figure(figsize=(6, 5))
    ax = sns.ecdfplot(
            data=data[data.solver.isin(solvers)],
            x="gap",
            hue=data[data.solver.isin(solvers)].solver,
            palette=colors,
            log_scale=log_scale,
        )
    ax.set(
        xlabel="Relative gap g",
        ylabel="Runs achieving gap ≤ g (%)",
        xlim = xlim,
        ylim = ylim,
    )
    sns.move_legend(ax, "lower right", title="Model")
    name = ""
    for solver in solvers:
        name += "_" + solver
    plt.savefig("figs/cumulative_gap" + name + ".pdf", format="pdf", bbox_inches="tight")
    plt.show()

def show_cumulative_time(data, solvers, colors, log_scale: bool = True):
    ax = sns.ecdfplot(
        data=data[data.solver.isin(solvers)],
        x="t_solver",
        hue=data[data.solver.isin(solvers)].solver,
        palette=colors,
        log_scale=log_scale,
    )
    ax.set(
        xlabel="Time t (seconds)",
        ylabel="Runs achieving time ≤ t (%)",
    )
    sns.move_legend(ax, "lower right", title="Model")
    name = ""
    for solver in solvers:
        name += "_" + solver
    plt.savefig("figs/cumulative_time" + name + ".pdf", format="pdf", bbox_inches="tight")
    plt.show()

#########################################

def show_performance_profile(data, solvers, log_scale: bool = False):
    data = data[data.solver.isin(solvers)]
    data2 = data[["instance", "k", "solver", "time_all"]].pivot_table(
        index=["instance", "k"], columns="solver", values="time_all"
    )
    palette = [
        "o-C0",
        "x--C1",
        "s-.C2",
        "+:C3",
        "o-C4",
        "o-C5",
        "x--C6",
        "s-.C7",
        "+:C8",
        "o-C9",
    ]
    pp.perfprof(data2, palette, markersize=4, markevery=[0])
    plt.legend(data2.columns)
    if log_scale:
        plt.xscale("log")
    plt.show()
