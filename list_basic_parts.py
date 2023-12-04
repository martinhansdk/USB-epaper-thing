"""List resistor, capacitor and inductor values available as basic parts

The data is fetched from the parts.db sqlite3 database file from the kicad-jlcpcb-tools
so you'll need to install that first and download the parts database.
"""

from argparse import ArgumentParser
from functools import total_ordering
from pathlib import Path
import sqlite3
import re

category_parsers = {
    'Chip Resistor - Surface Mount': [re.compile(r'(?P<power>\d+m?W).*?±(?P<precision>\d+%).*?(?P<value>\d+(\.\d+)?[mkM]?Ω)')],
    'Multilayer Ceramic Capacitors MLCC - SMD/SMT': [re.compile(r'(?P<power>\d+k?V).*?(?P<value>\d+(\.\d+)?[pnu]?F).*?±(?P<precision>\d+%)')]
}

VALUE_PARSER = re.compile(r'(?P<amount>\d+(\.\d+)?)(?P<multiplier>[pnumkM]?)[ΩF]$')

MULTIPLIERS = {
    'p': 1.0e-12,
    'n': 1.0e-9,
    'u': 1.0e-6,
    'm': 1.0e-3,
    '':  1.0,
    'k': 1.0e3,
    'M': 1.0e6,
}

@total_ordering
class Value:
    def __init__(self, strvalue: str):

        self.strvalue = strvalue

        mo = VALUE_PARSER.match(strvalue)
        assert mo, f"VALUE_PARSER does not match {strvalue}"

        self.amount = float(mo.group('amount')) * MULTIPLIERS[mo.group('multiplier')]

    def __eq__(self, other):
        return self.amount == other.amount
    
    def __lt__(self, other):
        return self.amount < other.amount
    
    def __str__(self):
        return self.strvalue
    
    def __repr__(self):
        return self.strvalue.__repr__()


DEFAULT_DATABASE = None
for dbpath in [Path("~/KiCad/7.0/3rdparty/plugins/com_github_bouni_kicad-jlcpcb-tools/jlcpcb/parts.db").expanduser(),
               Path("~/Documents/KiCad/7.0/3rdparty/plugins/com_github_bouni_kicad-jlcpcb-tools/jlcpcb/parts.db").expanduser()]:
    if dbpath.exists():
        DEFAULT_DATABASE = dbpath
        break

def basic_parts(database):
    cur = database.cursor()
    return cur.execute('SELECT "Second Category", "Package", "Description" FROM parts WHERE "Library Type" = \'Basic\'').fetchall()

def main():
    """Run as script."""

    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-d', '--database', default=DEFAULT_DATABASE, help='Database file from kicad-jlcpcb-tools. Default: %(default)s')

    args = parser.parse_args()

    db = sqlite3.connect(args.database)

    parts = {}

    for category, package, description in basic_parts(db):
        if category in category_parsers:
            if category not in parts:
                parts[category] = {}

            if package not in parts[category]:
                parts[category][package] = []

            match = False
            for regex in category_parsers[category]:
                if mo := regex.search(description):
                    match = True
                    parts[category][package].append((Value(mo.group('value')), mo.group('precision'), mo.group('power')))
                    parts[category][package].sort()
                    break

            if not match:
                print(f"NO match: {category=} {package=} {description=}")

    for category in parts.keys():
        print(f"---- {category}")
        for package in parts[category].keys():
            print(f"-- {package}")
            for value, precision, power in parts[category][package]:
                print(f"{str(value) : >7} {precision : >3} {power : >5}")

if __name__ == '__main__':
    main()