# %%
import pandas as pd
import json
from pathlib import Path
# remove col limit
# %%
RACES = [
  "NH_BLACK",
  "NH_WHITE",
  "HISP",
  "NH_ASIAN",
  "NH_OTHER",
]
# %%
def summarize_election(
  election_path
):
  back_half = election_path.stem.split("samples_100")[1]
  _, plan, district, seat_count, cohesion, alpha = back_half.split("_")
  counts = {}
  with open(election_path, "r") as f:
    for line in f:
      election = json.loads(line)
      winners = election["winners"]
      for _winner in winners:
        winner = "_".join(_winner.split("_")[:-1])
        if winner not in counts:
          counts[winner] = 0
        counts[winner] += 1
  # divide each by number of runs
  for winner in counts:
    counts[winner] = counts[winner] / 100
  for race in RACES:
    if race not in counts:
      counts[race] = 0
  return {
    "plan": plan,
    "district": district,
    "seat_count": seat_count,
    "cohesion": cohesion,
    "alpha": alpha,
    **counts,
  }

# %%
if __name__ == "__main__":
  DATA_DIR = Path("../data")
  PLAN_DIR = DATA_DIR / "plan_results"
  seats5_results = PLAN_DIR.glob("stv_slate_pl_voters_1000_seats_5*.jsonl")
  output = []
  for result_file in seats5_results:
    output.append(summarize_election(result_file))
  df = pd.DataFrame(output)
  df.to_parquet(DATA_DIR / "scenario_outcomes" / "scenario_outcomes.parquet")

# %%
