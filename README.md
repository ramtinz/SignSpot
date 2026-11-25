# SignSpot

<p align="center">
  <img src="assets/signspotlogo-transparent.png" alt="SignSpot — spot we trust" width="280">
</p>

**Find parking. Report unclear signs.**

SignSpot is a community mapping app for sharing free-parking locations and reporting signs that are hidden, damaged, missing, or difficult to understand. Contributors can mark a single location or highlight an area, record the conditions shown on a sign, and give feedback on existing reports.

[Open SignSpot](https://signspot.streamlit.app/) · [Report an issue](https://github.com/ramtinz/SignSpot/issues) · [Cite the project](#citation)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18874701.svg)](https://doi.org/10.5281/zenodo.18874701)

## Why SignSpot?

Parking information can be difficult to interpret on the ground. A sign may be obscured, its wording unclear, or its conditions limited to certain hours or vehicles. SignSpot gives people a way to record those observations at the location where they matter and share them with other drivers.

Use the map to explore reported free-parking locations, identify sign issues, and review restrictions before visiting a location. Each report can describe an individual spot or a larger area covered by the same conditions.

## Add a report in three steps

1. **Choose a location.** Select a city, then choose **Mark a spot** and tap the map, or choose **Highlight area** and drag over the relevant spaces. Select **Use selected location** to continue.
2. **Describe the spot.** Choose **Free parking** or **Unclear or damaged sign**, select a reason, and choose **Continue to review**.
3. **Review and submit.** Add any known restrictions, confirm the location, and submit. The app displays a confirmation after saving.

To explore existing contributions, use the map filters or open **Community reports**. Reports include community agreement and disagreement counts.

### Highlight an area

The highlighter works like a thick marker. Select a stroke width of **4, 8, 12, or 20 metres**, then drag to mark the parking spaces. Add several strokes if needed, use **Undo stroke** to remove the latest one, or **Clear selection** to start again. Switch to **Move map** to pan and zoom.

The highlighted ground area retains its dimensions when zooming. Saved areas appear as shaded boundaries. Include only spaces covered by the same parking conditions.

### Record parking conditions

Open **Parking restrictions (optional)** to add the details you can confirm.

| Detail | Examples |
| --- | --- |
| Vehicle types | Cars, motorcycles, vans, motorhomes or campervans |
| Reserved access | Electric vehicles, authorized shared cars, residents, disabled parking permits |
| Charging | Required, optional, or no charger |
| Hours and payment | Applicable days, free periods, payment conditions, maximum stay |
| Size limits | Height, length, or weight restrictions |
| Motorhomes | Separate parking and overnight/camping permissions |
| Supporting information | An official information URL and date checked on site |

The access options distinguish **electric AND authorized shared cars** from **electric OR authorized shared cars**. Leave uncertain details as **Unknown**. Restrictions appear in map popups and the report list; older reports display **Restrictions not recorded**.

## Run locally

Use Python 3.11 and create a separate environment.

```bash
git clone https://github.com/ramtinz/SignSpot.git
cd SignSpot
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run main.py
```

On Windows, activate the environment with `.venv\Scripts\Activate.ps1` in PowerShell.

### Implementation and storage

SignSpot uses Streamlit for the interface, Leaflet and OpenStreetMap for the map, and Turf for geographic highlighter strokes. The map is packaged as a local Streamlit component and requires no frontend build step.

Reports, votes, and area boundaries are stored in `parking_reports.db`, which is created automatically and excluded from Git. The current hosted app uses local SQLite storage. Durable storage across hosted restarts and redeployments remains a deployment improvement.

## Feedback and collaboration

Suggestions, bug reports, and contributions are welcome through [GitHub Issues](https://github.com/ramtinz/SignSpot/issues). For collaboration or commercial licensing enquiries, contact **ramtin.zargari AT gmail.com**.

Developed by [Ramtin Zargari Marandi, PhD](https://www.linkedin.com/in/rzm/).

## Citation

```bibtex
@software{zargari_marandi_2026_signspot,
  author       = {Zargari Marandi, Ramtin},
  title        = {SignSpot},
  year         = 2026,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.18874701},
  url          = {https://doi.org/10.5281/zenodo.18874701}
}
```

Machine-readable citation metadata is available in [CITATION.cff](CITATION.cff).

## License

SignSpot is available under a custom non-commercial license. Non-commercial use is permitted under its terms; commercial use requires permission. See [LICENSE](LICENSE).

Leaflet and Turf retain their own licenses. Their notices are included in [parking_map/frontend/vendor](parking_map/frontend/vendor).

## Use and responsibility

**Use at your own risk.** SignSpot is a crowdsourced app - data accuracy depends on community contributions. Always verify parking rules yourself before parking.

**Legal Responsibility:** Users are solely responsible for ensuring that their use of SignSpot complies with applicable laws and regulations in their country and local jurisdiction. The use of this app is intended only for legal purposes. The developer assumes no responsibility for any legal consequences resulting from users' use of the app in violation of local, regional, or national laws.
