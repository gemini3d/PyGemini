#!/usr/bin/env python3
from argparse import ArgumentParser
from matplotlib.pyplot import figure, show
import gemini3d.read


def plotplasma(dat: dict):
    for k, v in dat.items():
        if k == "t":
            t = v
            continue

        ax = figure().gca()
        ax.pcolormesh(v.squeeze())
        ax.set_title(f"{k}  {t}")


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("simdir", help="directory where output data files are")
    p.add_argument("time", help="time of frame to plot")
    p = p.parse_args()

    dat = gemini3d.read.frame(p.simdir, p.time)

    plotplasma(dat)

    show()
