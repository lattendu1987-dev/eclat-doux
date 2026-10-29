"""`python -m eclat site` : génère le site dans public/.
`python -m eclat affiliation` : simulation des commissions."""

import sys

cmd = sys.argv[1] if len(sys.argv) > 1 else "site"
if cmd == "site":
    from .site import build
    print(f"Site généré : {build()}")
elif cmd == "affiliation":
    from .affiliate import table_md
    print(table_md())
else:
    print(__doc__)
    raise SystemExit(2)
