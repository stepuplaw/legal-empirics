#!/usr/bin/env python3
"""Size the trustee-compensation lanes before designing the study.

    python3 size_lanes.py                # Florida slice, seconds
    python3 size_lanes.py --national     # 51 jurisdictions, minutes

Counts OPINIONS, not decisions. This is lane triage for
`protocols/trustee-fees.md` stage 3, not the study funnel.

Two hazards this is checking for.

  VOCABULARY. Eastern states call fiduciary compensation "commissions" (NY SCPA
  2309), most others call it "fees". A lane built on one word measures a region.

  DOCTRINE. "Attorney's fees paid from the trust" is a different question from
  "the trustee's own compensation", and it is far more voluminous. If they are
  not separated the study measures fee-shifting and calls it trustee
  compensation -- the same shape as the ambiguity/statutory-construction trap.

Every candidate is counted CROSSED with trustee, never alone.
"""
import os, sys, time, json
sys.path.insert(0, os.path.expanduser("~/caselaw"))
import clcorpus as cc

T = "(trustee OR trustees)"
LANES = {
 # -- the trustee's own compensation
 "trustee's compensation":   '"trustee\'s compensation" OR "trustees\' compensation" OR "trustee compensation"',
 "trustee's fee(s)":         '"trustee\'s fee" OR "trustee\'s fees" OR "trustees\' fees" OR "trustee fees"',
 "trustee's commission(s)":  '"trustee\'s commission" OR "trustee\'s commissions" OR "trustees\' commissions" OR "trustee commissions"',
 "commissions AND trustee":  f'commissions AND {T}',
 "reasonable compensation":  f'"reasonable compensation" AND {T}',
 "excessive fees/comp":      f'("excessive fees" OR "excessive compensation" OR "excessive commissions") AND {T}',
 "extraordinary services":   f'"extraordinary services" AND {T}',
 "double compensation":      f'("double compensation" OR "double commissions") AND {T}',
 "fee schedule":             f'"fee schedule" AND {T}',
 "published fee schedule":   '"published fee schedule"',
 "termination fee":          f'"termination fee" AND {T}',
 "percentage of the corpus": f'("percentage of the corpus" OR "percentage of the trust" OR "of the principal") AND {T}',
 # -- the contaminant: fee-shifting, a different doctrine
 "attorney's fees AND trustee": f'("attorney\'s fees" OR "attorneys\' fees" OR "attorney fees") AND {T}',
 # -- statutory hooks
 "UTC 708 words":            f'("reasonable under the circumstances" OR "unreasonably low or high") AND {T}',
 "736.0708":                 '"736.0708"',
 "SCPA 2309":                '"2309" AND commissions',
}

national = "--national" in sys.argv
con, info = cc.connect(scope="all" if national else "fl", national=national)
out = {}
for name, q in LANES.items():
    t0 = time.time()
    out[name] = len(cc.fts_ids(con, q, warn_at=10**9))
    print(f"{name:30s} {out[name]:>9,}   [{time.time()-t0:.0f}s]", flush=True)
tag = "national" if national else "fl"
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"fees_{tag}.json"), "w"), indent=2)
print("DONE", flush=True)
