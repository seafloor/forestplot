import matplotlib.pyplot as plt


def check_axes(fig, ax, fig_shape=None):
    if all([x is None for x in [fig, ax]]):
        fig_shape = (8, 19) if fig_shape is None else None
        fig, ax = plt.subplots(figsize=fig_shape)

    return fig, ax


def get_xlim(ax):
    xmin, xmax = ax.get_xaxis().get_view_interval()

    return xmin, xmax


def get_ylim(ax):
    ymin, ymax = ax.get_yaxis().get_view_interval()

    return ymin, ymax


def save_fig(fig, file_name, save_type='pdf', dpi=500):
    if save_type == 'pdf':
        fig.savefig('{}.pdf'.format(file_name), transparent=False, dpi=dpi,
                    bbox_inches='tight')

    elif save_type == 'tiff':
        fig.savefig('{}.tiff'.format(file_name), transparent=False, dpi=dpi,
                    bbox_inches='tight', pil_kwargs={'compression': 'tiff_lzw'})
    else:
        raise ValueError('Figure type not supported')
