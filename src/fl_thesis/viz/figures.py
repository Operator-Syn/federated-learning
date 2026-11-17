"""Build and save figures to disk.

Why the backend is forced here: this module only ever writes files, and a machine can
have ``DISPLAY`` set while the display is unusable, which makes matplotlib pick an
interactive backend and fail at ``subplots`` with a connection error that reads like a
plotting bug. ``Agg`` before ``pyplot`` is imported keeps the module runnable from a
notebook and from a headless shell alike.

Figures are saved and then displayed by the caller from the saved file, because cell
outputs are ephemeral — the Git clean filter strips them before commit.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # must precede the pyplot import; this module never shows a window

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure


def availability_figure(
    stations: np.ndarray,
    *,
    title: str = "synthetic: availability over 20 rounds",
    figsize: tuple[float, float] = (4, 2.2),
) -> Figure:
    """Plot reachable stations per round.

    Args:
        stations: per-round count of reachable stations; length becomes the x axis.
        title: figure title.
        figsize: figure size in inches.

    Returns:
        The unshown figure. The caller owns closing it.
    """
    rounds = np.arange(1, len(stations) + 1)
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(rounds, stations, marker="o", linewidth=1)
    ax.set_xlabel("round")
    ax.set_ylabel("stations available")
    ax.set_title(title)
    ax.grid(alpha=0.3)
    return fig


def save_figure(figure: Figure, path: Path, *, dpi: int = 150) -> Path:
    """Write ``figure`` to ``path`` and close it.

    Args:
        figure: figure to render.
        path: destination file; parent directories are created if needed.
        dpi: raster resolution.

    Returns:
        The path written, so the caller can display or log it without rebuilding it.

    Closing is deliberate: a figure left open is auto-rendered at the end of a notebook
    cell, which duplicates a plot the caller is about to display from its file.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(figure)
    return path
