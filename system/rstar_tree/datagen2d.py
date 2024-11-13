from numpy.random import default_rng
import pandas as pd
import argparse

rng = default_rng()

parser = argparse.ArgumentParser(description="Run RDF Graph Visualization")
parser.add_argument("--data", type=int, default=30, help="")
args = parser.parse_args()

# data = rng.uniform( low = -60.0, high = 60.0, size = (500,2) )
data = rng.normal( loc=0.0, scale = 32.0, size = (args.data,2) )

df = pd.DataFrame(data)

df.to_csv('rstar_tree/generated_data.csv')
