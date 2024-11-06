from mdh import run_mdh
import argparse
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def run(args):
            
    run_mdh(args.data, args.print)

def main():
    parser = argparse.ArgumentParser(description="Run RDF Graph Visualization")
    parser.add_argument("--data", type=str, default="data_demo", help="Name of the data directory")
    parser.add_argument("--print", type=str, default=False, help="Print the results of each step or not")
    args = parser.parse_args()

    run(args)


if __name__ == "__main__":
    main()
