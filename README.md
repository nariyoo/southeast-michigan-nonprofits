# Southeast Michigan Nonprofits

Workshop example: a searchable map and directory of social service nonprofits, built with a coding agent.

Data: IRS Exempt Organizations Business Master File, Michigan file. 501(c)(3) organizations with ZIP codes 480 to 483, without hospitals and medical care organizations. Map positions come from Census ZIP code centers. Check the original filings before relying on a number.

Design: colors and layout adapted from a DESIGN.md in VoltAgent/awesome-design-md. No affiliation with any brand.

To rebuild: `python build_snapshot.py`, `python build_map_data.py`, `python build_design.py`.
