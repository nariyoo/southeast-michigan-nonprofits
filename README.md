# Southeast Michigan Nonprofits

Workshop example: a searchable map and directory of social service nonprofits, built with a coding agent.

Data: IRS Exempt Organizations Business Master File, Michigan file. 501(c)(3) organizations with ZIP codes 480 to 483, without hospitals and medical care organizations. Missions, websites and staff counts come from e-filed Form 990s. Map positions come from Census ZIP code centers. Check the original filings before relying on a number.

Design: colors and layout adapted from a DESIGN.md in VoltAgent/awesome-design-md. No affiliation with any brand.

To rebuild, run in order: `build_snapshot.py`, `build_map_data.py`, `build_history.py`, `build_missions.py`, `build_design.py`.
