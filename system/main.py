import argparse
import sys
import io
from mdh.mdh import run_mdh
from rstar_tree.rtvis_3d import run_rstar_tree

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def run(args):
    if(args.mdh):
        run_mdh(data=args.data, print_output=args.print, visualize = args.visualize, number_charts = args.number_charts)
    if(args.rstar_tree):
        run_rstar_tree(data=args.data, M=args.M, m=args.m, p=args.p, print_output=args.print, number_charts = args.number_charts, depth_chart=args.depth_chart)

def main():
    parser = argparse.ArgumentParser(description="Run RDF Graph Visualization")
    parser.add_argument("--data", type=str, default="data_demo", help="Name of the data directory")
    parser.add_argument("--mdh", type=bool, default=False, help="build mdh chart")
    parser.add_argument("--rstar_tree", type=bool, default=False, help="build r*-tree index structure")
    parser.add_argument("--print", type=bool, default=False, help="Print the results of each step or not")
    parser.add_argument("--visualize", type=bool, default=False, help="visualize model rdf data into graph")
    parser.add_argument("--number_charts", type=int, default=10, help="Maximum number of charts")
    parser.add_argument("--M", type=int, default=4, help="maximum number of children")
    parser.add_argument("--m", type=int, default=2, help="minimum number of children. try m = floor(0.4*M)")
    parser.add_argument("--p", type=int, default=1, help="Parameter controlling how overflow is treated. try p = floor(0.3*M)")
    parser.add_argument("--depth_chart", type=int, default=3, help="depth of chart")

    args = parser.parse_args()

    run(args)


if __name__ == "__main__":
    main()
