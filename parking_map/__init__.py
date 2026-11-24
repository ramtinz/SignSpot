from pathlib import Path

from streamlit.components.v1 import declare_component

_component = declare_component("signspot_parking_map", path=str(Path(__file__).parent / "frontend"))


def parking_map(center, reports, selection=None, key=None):
    return _component(center=center, reports=reports, selection=selection, key=key, default=None)
