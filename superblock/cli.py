from genericpath import isdir, isfile
import sys
import os
import argparse
from bs4 import BeautifulSoup
from numpy import record
from rich.console import Console
import cProfile
import pstats
import io

# from parser.ast2ele import AstToElementParser
from parser.ele2mod import ElementToModule
from parser.html2ele import HtmlToElementParser

parser = argparse.ArgumentParser(description="SuperBlock CLI")
subparsers = parser.add_subparsers(dest="command")

run_parser = subparsers.add_parser("run")
run_parser.add_argument(
    "-i",
    "--input",
    default=".",
    help="Input directory or file. If a directory is specified, all files in the directory with a '.sb' extension will be parsed.",
)
run_parser.add_argument(
    "-o",
    "--output",
    default="./build",
    help="Directory to output the generated website.",
)


def main():
    args = parser.parse_args()
    if args.command == "run":
        run(args)


def run(args: argparse.Namespace):
    arg_input = args.input
    arg_output = args.output

    files = []
    # If input is a directory, parse all files in the directory.
    if isdir(arg_input):
        files.extend(
            os.path.join(arg_input, f)
            for f in os.listdir(arg_input)
            if f.endswith(".sb")
        )
    elif arg_input.endswith(".sb"):
        files.append(arg_input)
    else:
        print(f"Invalid input file/directory: {arg_input}")
        sys.exit(1)

    if len(files) == 0:
        print("No files found to parse.")
        sys.exit(1)

    if not isdir(arg_output):
        os.makedirs(arg_output)
        print(f"Created output directory: {arg_output}")

    print(f"Parsing {len(files)} files...")
    for f in files:
        print(f"Parsing {f}...")
        run_parse(f, arg_output)

def start_profile():
    pr = cProfile.Profile()
    pr.enable()
    return pr

def end_profile(pr, f):
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('tottime')
    ps.print_stats()
    with open(f, "w") as f:
        f.write(s.getvalue())

def run_parse(arg_input: str, arg_output: str):

    with open(arg_input, "r") as f:
        content = f.read()
    name = os.path.basename(arg_input).replace(".sb", "")
    save_dir = os.path.join(arg_output, name)
    if not isdir(save_dir):
        os.makedirs(save_dir)
    html_output = os.path.join(save_dir, "index.html")
    profile_output = os.path.join(save_dir, "profile.txt")
    
    pr = start_profile()

    parser = HtmlToElementParser()
    root = parser.parse_start(content)

    parser = ElementToModule()
    module = parser.parse_start(root)

    end_profile(pr, profile_output)

    console = Console(record=True)
    console.print(module.env["rich_tree"])
    console.save_html("log.html")

    render = module.render_str()
    soup = BeautifulSoup(render, "html.parser")
    render = soup.prettify()

    with open(html_output, "w") as f:

        f.write(
            '<link href="https://cdn.jsdelivr.net/npm/daisyui@2.2.2/dist/full.css" rel="stylesheet" type="text/css" />'
        )
        f.write('<script src="https://cdn.tailwindcss.com"></script>')
        #f.write('<style>div { border: 2px solid #afafaf5c; }</style>')
        f.write(render)




if __name__ == "__main__":
    main()
