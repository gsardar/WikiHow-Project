import json
import subprocess
import time
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Batch runner for all continuum analyses")
    parser.add_argument("--enhanced", action="store_true",
                        help="Use enhanced analysis (contributions + temporal)")
    parser.add_argument("--parallel", action="store_true",
                        help="Use parallel mode for faster processing")
    parser.add_argument("--publication", action="store_true",
                        help="Use publication-quality visualizations (100%% stacked bars)")
    parser.add_argument("--grayscale", action="store_true",
                        help="Use grayscale colors (publication mode only)")
    parser.add_argument("--workers", type=int, default=5,
                        help="Number of parallel workers (default: 5)")
    parser.add_argument("--script", default=None,
                        help="Override script to use")
    parser.add_argument("--categories", nargs="+",
                        help="Pilot Mode: Analyze only these specific categories")
    parser.add_argument("--limit", type=int, default=None,
                        help="Pilot Mode: Article limit per category")

    args = parser.parse_args()

    # Determine which script to use
    if args.script:
        script = args.script
    elif args.publication:
        script = "plots/plot_spectrum_publication.py"
    elif args.parallel:
        script = "plots/plot_spectrum_parallel.py"
    elif args.enhanced:
        script = "plots/plot_spectrum_enhanced.py"
    else:
        script = "plots/plot_spectrum.py"

    print(f"Using script: {script}")
    if args.categories:
        print(f"PILOT MODE: Running for specific categories: {args.categories}")
        spaces = {"pilot": {"title": "Pilot Test", "cats": args.categories}}
    else:
        print("Reading mapped spaces...")
        try:
            # Prioritize the expanded semantic mapping if available
            mapping_file = 'data/mapped_spaces_expanded.json'
            if not os.path.exists(mapping_file):
                mapping_file = 'data/mapped_spaces.json'
            
            print(f"  Source: {mapping_file}")
            with open(mapping_file, 'r') as f:
                spaces = json.load(f)
        except Exception as e:
            print(f"Error reading mapped spaces: {e}")
            return

    print(f"Starting master batch run for {len(spaces)} continuums...")

    for c_id, space in spaces.items():
        title = space["title"]
        cats = space["cats"]

        print(f"\n======================================")
        print(f"Launching script for: {title}")
        print(f"Categories: {cats}")
        print(f"======================================")

        if not cats:
            print(f"Skipping {title} - no valid categories mapped.")
            continue

        cmd_args = ["py", "-u", script, c_id, title] + cats

        # Add optional arguments
        if args.parallel or args.publication:
            cmd_args += ["--workers", str(args.workers)]

        if args.limit:
            cmd_args += ["--limit", str(args.limit)]

        if args.publication and args.grayscale:
            cmd_args += ["--grayscale"]

        # We use subprocess.run to call the existing parameterized script so we
        # don't duplicate code and we just let it churn for as long as it takes.
        import os
        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd() + os.pathsep + env.get("PYTHONPATH", "")
        result = subprocess.run(cmd_args, env=env)

        if result.returncode != 0:
            print(f"Error running script for {title}")
        else:
            print(f"Successfully generated {title} analysis.")

        print("Cooling down for 10 seconds to avoid IP block...")
        time.sleep(10)

    print("\n==========================================")
    print("All continuums processed!")
    print("==========================================")

if __name__ == "__main__":
    main()
