# Run
from deeponto.align.oaei import *

# If has_score is False, assume default ranking (see tips below)
ranking_eval("scored.test.cands.tsv", has_score=True, Ks=[1, 5, 10])