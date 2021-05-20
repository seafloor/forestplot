import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from .base import check_axes, get_xlim, get_ylim


def check_data(data):
    assert isinstance(data, pd.DataFrame), 'Please supply data as Pandas DataFrame'

    data['sort_order'] = np.arange(data.shape[0])[::-1]

    return data


def forest_plot(data, auc_col, se_col, to_annotate=None, subset_col=None, fig=None, ax=None, add_legend=True,
                legend_loc='upper right', hbar_lim=None, xlim=None, fig_shape=None, anot_base=0.15,
                annot_offset=13, annot_scaler=0.01, add_ci=True, auc_label=None, fargs=None):
    """
    Basic forest plots for meta analyses

    Parameters
    ----------
    data: pandas DataFrame
        contains all columns to be annotated, AUCs and standard errors
    auc_col: str
        named of column containing AUC values
    se_col: str
        name of column containing standard errors
    to_annotate: list of str, default None
        column names for information to annotation on the left of the plot
    subset_col: str, default None
        name of column for splitting data by marker type in plot
    fig: matplotlib figure, default None
        use if matplotlib figure/axes have already been created
    ax: matplotlib axes, default None
        use if matplotlib figure/axes have already been created
    add_legend: bool, default True
        add a legend
    legend_loc: str, default 'upper right'
        location of legend
    hbar_lim: tuple or list, default None
        x-axis limits for the header/tail of table
    xlim: tuple or list, default None
        x-axis limits for plotting AUC and error bars
    fig_shape: tuple, default None
        figure size to use if you want to overwrite the default shape
    anot_base: float, default 0.15
        minimum distance between all columns, regardless of column width
    annot_offset: float, default 13
        estimate of average number of characters per column. Adjust up or down accordingly
    annot_scaler: float, default 0.01
        estimate of the amount by extra/reduced space to give column widths that deviate from annot_offset
    add_ci: bool, default True
        Annotate CI after AUC
    auc_label: str or None, default None
        Label for the forest plot section
    fargs: dict, default None
         kwargs for fontsizes

    Returns
    -------
    fig, ax: matplotlib figure and axes objects
    """
    data = check_data(data)
    fig, ax = check_axes(fig, ax, fig_shape)

    # plot auc and 95% CI
    ax = plot_auc(data, ax, auc_col, se_col, subset_col=subset_col, add_legend=add_legend, legend_loc=legend_loc,
                  xlim=xlim, auc_label=auc_label)

    # add all columns in to_annotate as text
    if to_annotate is not None:
        ax = annotate_columns(data, to_annotate, auc_col, se_col, ax, anot_base=anot_base, annot_offset=annot_offset,
                              annot_scaler=annot_scaler, hbar_lim=hbar_lim, add_ci=add_ci, auc_label=auc_label,
                              fargs=fargs)

    return fig, ax


def parse_auc(data, row, auc, se_col, add_ci=True):
    if add_ci:
        auc = '{:.2f} [{:.2f}-{:.2f}]'.format(auc, auc - (1.96 * data.iloc[row, :][se_col]),
                                              auc + (1.96 * data.iloc[row, :][se_col]))
    else:
        auc = '{:.2f}'.format(auc)

    return auc


def annotate_columns(data, to_annotate, auc_col, se_col, ax, anot_base=0.15, annot_offset=13, annot_scaler=0.01,
                     y_offset=0.25, hbar_lim=None, add_ci=True, auc_label=None, fargs=None):
    xmin, xmax = get_xlim(ax)
    fargs = {'fontsize': 12, 'fontfamily': 'sans-serif', 'clip_on': False} if fargs is None else fargs
    to_annotate = [to_annotate] if isinstance(to_annotate, str) else to_annotate
    assert isinstance(to_annotate, list), 'supply annotation column names as a list of strings'
    to_annotate = to_annotate[::-1]
    column_offsets = []
    annotations = []

    for i, txt in enumerate(np.arange(data.shape[0])):
        xiter = xmin  # moves column annotation outward from plot
        for j, column in enumerate(to_annotate):
            max_len = max(data[column].astype(str).str.len().max(), len(column))  # gets width of a column in characters
            col_shift = anot_base + ((max_len-annot_offset)*annot_scaler)
            if j != 0:
                xiter -= col_shift  # distance away from previous shifted proportional to number of characters
            s = data.iloc[txt, :][column]
            if isinstance(s, (float, np.float)) and np.isnan(s):
                continue
            s = parse_auc(data, txt, s, se_col, add_ci) if column == auc_col else s
            x = xmax if column == auc_col else xiter
            y = data.iloc[txt, :]['sort_order'] - y_offset
            annotations.append(ax.text(x=x, y=y, s=s, **fargs))
            if i == 0:
                auc_label = 'AUC' if auc_label is None else auc_label
                annotations.append(ax.text(x=x, y=data.shape[0]+0.6, s=column, **fargs))
                if add_ci:
                    __ = [annotations.append(ax.text(x=aucx, y=data.shape[0]+0.6, s=auc_label + ' [95%  CI]', **fargs))
                          for aucx in [xmin, xmax]]
                else:
                    __ = [annotations.append(ax.text(x=aucx, y=data.shape[0]+0.6, s=auc_label, **fargs))
                          for aucx in [xmin, xmax]]
                column_offsets.append(col_shift)

    bars = []
    annotations = [a.get_position()[0] for a in annotations]
    if hbar_lim is None:
        #hbar_xmin = 0 - xmin - np.sum(column_offsets) + column_offsets[0]
        #hbar_xmax = 1.22
        if add_ci:
            max_bar = np.max(annotations) if auc_label is None else np.max(annotations) + 0.009 * len(auc_label + ' [95%  CI]')
        else:
            max_bar = np.max(annotations) if auc_label is None else np.max(annotations) + 0.01 * len(auc_label)
        hbar_xmin, hbar_xmax = np.min(annotations), max_bar

    else:
        hbar_xmin, hbar_xmax = hbar_lim

    bargs = {'c': '#333333', 'linestyle': '-'}
    for hbar_ypos, line_width in zip([data.shape[0], data.shape[0]+2, -2.8], [1, 2, 2]):
        bars.append(ax.axhline(y=hbar_ypos, xmin=hbar_xmin, xmax=hbar_xmax, linewidth=line_width, **bargs))
    _ = [b.set_clip_on(False) for b in bars]
    _ = [b.set_transform(ax.transData) for b in bars]

    return ax


def plot_auc(data, ax, auc_col, se_col, subset_col=None, colour='#2E5A86', add_vline=True, add_legend=True,
             legend_loc='upper right', xlim=None, auc_label=None):
    if subset_col is not None:
        subsets = data[subset_col].unique().tolist() if subset_col in data.columns else None
    else:
        subsets = None

    if subsets is not None:
        markers = ['o', 's', '^', 'v', 'X', 'P', 'p'][:len(subsets)]
        assert len(markers) == len(subsets), 'More subsets than markers - overwrite marker list'

        for s, m in zip(subsets, markers):
            ax.errorbar(data.loc[data[subset_col] == s, auc_col],
                        data.loc[data[subset_col] == s, 'sort_order'],
                        xerr=data.loc[data[subset_col] == s, se_col] * 1.96,
                        fmt=m, label=s, c=colour, elinewidth=0.8,
                        **{'markersize': 7})
    else:
        auc_label = auc_label if auc_label is not None else 'AUC (95% CI)'
        ax.errorbar(data[auc_col],
                    data['sort_order'],
                    xerr=data[se_col] * 1.96,
                    fmt='o', label=auc_label, c=colour, elinewidth=0.8,
                    **{'markersize': 7})

    if add_vline:
        ax.axvline(x=0.5, c='#474747', linestyle='--', alpha=0.8, ymin=0,
                   ymax=0.99 * ((data.shape[0] - 1) / data.shape[0]))

    if add_legend:
        leg = ax.legend(loc=legend_loc, frameon=False, title="Validation", fontsize=11,
                        borderaxespad=2.2, framealpha=0.5)
        leg._legend_box.align = "left"
    ax.tick_params(axis='x', labelsize=12)
    ax.set_frame_on(False)
    ax.set_yticks([])
    ax.set_ylim([-1, data.shape[0]+1])
    if xlim is not None:
        ax.set_xlim(*xlim)
    xmin, xmax = get_xlim(ax)
    ymin, ymax = get_ylim(ax)
    ax.add_artist(plt.Line2D((xmin, xmax), (ymin, ymin), color='#262626', linewidth=2))
    ax.tick_params(direction="in", which='major', pad=3, length=7)
    ax.tick_params(direction="in", which='minor', pad=3, length=4)
    ax.minorticks_on()

    return ax
