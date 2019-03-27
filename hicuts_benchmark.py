import time
from hicuts import *

rules = load_rules_from_file("classbench/acl1_100k")
start = time.time()
cuts = HiCuts(rules)
cuts.train()
print("Total split time", time.time() - start)
