from matplotlib.pyplot import savefig, close, subplots
from climada.entity.exposures.base import Exposures
from os.path import join
from process import DOMAIN
from climada.hazard.tc_tracks import TCTracks as TCTracks_type
from climada.engine.impact import Impact as Impact_type

def plot_litpop(workdir: str, litpop_obj: Exposures):
    """Plot LitPop

    Args:
        workdir (str): Working directory
        litpop_obj (Exposures): Exposures map
    """

    litpop_obj.plot_raster(cmap="Reds", figsize=(12, 16), adapt_fontsize=False)

    country = DOMAIN["country"].replace(" ", "_")
    savefig(
        join(workdir, f"LitPop_{country}.png"),
        bbox_inches='tight',
        dpi=200)
    close()


def plot_tc(workdir: str, tc_obj: TCTracks_type) -> Impact_type:
    """Plot LitPop

    Args:
        workdir (str): Working directory
        tc_obj (TCTracks_type): TC object
    """
    tc_obj.plot(figsize=(16, 12), adapt_fontsize=False)
    savefig(
        join(workdir, "tc.png"),
        bbox_inches='tight',
        dpi=200)
    close()


def plot_impact(workdir: str, impact_obj: Impact_type):
    """Plot LitPop

    Args:
        workdir (str): Working directory
        impact_obj (Impact_type): impact object
    """
    impact_obj.plot_hexbin_eai_exposure(figsize=(16, 12), adapt_fontsize=False, buffer=1, vmax=2000.0)
    savefig(
        join(workdir, "impact.png"),
        bbox_inches='tight',
        dpi=200)
    close()
