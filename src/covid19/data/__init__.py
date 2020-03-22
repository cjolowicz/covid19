import rki
import rki_arcgis


def load(name: str, source: str = "rki"):
    if source == "rki":
        return rki.load(name)

    if source == "rki_arcgis":
        return rki_arcgis.load(name)

    raise ValueError(f"invalid source {source}")
