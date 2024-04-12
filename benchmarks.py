import json
import subprocess
import sys
import os
from datetime import datetime, timedelta
import re

def collect_tests(test_path):
    """Collect tests from the specified path."""
    command = ['poetry', 'run', 'pytest', '--collect-only', '-q', test_path]
    result = subprocess.run(command, capture_output=True, text=True)
    tests = re.findall(r'^autotx\S+', result.stdout, re.MULTILINE)

    if not tests:
        print(result)

    return tests

def run_test(test_name, iterations, avg_time_across_tests, completed_tests, remaining_tests):
    """Runs a specific test multiple times and captures the output and results."""
    pass_count, fail_count = 0, 0
    run_times = []

    for iteration in range(1, iterations + 1):
        cmd = f"poetry run pytest -s {test_name}"
        start_time = datetime.now()
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        run_times.append(duration)

        test_dir = f"{test_name.replace('/', '_').replace('::', '_')}"
        iteration_dir = f"{output_dir}/{test_dir}/{'passes' if result.returncode == 0 else 'fails'}/{iteration}"
        os.makedirs(iteration_dir, exist_ok=True)

        with open(f"{iteration_dir}/stdout.txt", 'w') as f_out, open(f"{iteration_dir}/stderr.txt", 'w') as f_err:
            f_out.write(result.stdout)
            f_err.write(result.stderr)

        if result.returncode == 0:
            pass_count += 1
        else:
            fail_count += 1

        # Estimate time after each iteration
        avg_time_current_test = sum(run_times) / len(run_times)
        remaining_iterations_current_test = iterations - iteration
        remaining_time_current_test = avg_time_current_test * remaining_iterations_current_test

        estimated_avg_time_across_tests = 0
        if avg_time_across_tests:
            estimated_avg_time_across_tests = (avg_time_across_tests * completed_tests + avg_time_current_test * iterations) / (completed_tests + 1)
        else:
            estimated_avg_time_across_tests = avg_time_current_test * iterations

        estimated_time_left = remaining_time_current_test + (estimated_avg_time_across_tests * remaining_tests)
        total_completion_time = datetime.now() + timedelta(seconds=estimated_time_left)

        print(f"\nIteration {iteration}: {'Pass' if result.returncode == 0 else 'Fail'} in {duration:.2f} seconds")
        print("=" * 50)
        print(f"Estimated time until completion for all tests: {estimated_time_left/60:.2f} minutes")
        print(f"Estimated completion time: {total_completion_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)

    return pass_count, fail_count, run_times

def print_summary_table(test_path: str, iterations: int, tests_results: dict, total_run_time: float, output_dir: str, total_benchmarks: dict):
    """Prints a summary table of all tests in markdown format to the console and a file, including total success percentage."""
  
    # Calculate total passes and fails
    total_passes = sum(result['passes'] for result in tests_results)
    total_fails = sum(result['fails'] for result in tests_results)
    total_attempts = total_passes + total_fails

    # Calculate total success percentage
    total_success_percentage = (total_passes / total_attempts * 100) if total_attempts > 0 else 0

    prev_rates = sum(float(total_benchmarks["benchmarks"][result["name"]] if total_benchmarks["benchmarks"].get(result["name"]) else 0.0) for result in tests_results)
    any_prev_rate = any(True if total_benchmarks["benchmarks"].get(result["name"]) else False for result in tests_results)
    prev_total_success_percentage = (prev_rates / len(tests_results)) if len(tests_results) > 0 else 0
    total_success_color = "lightgreen" if total_success_percentage > prev_total_success_percentage and any_prev_rate else "none" if total_success_percentage == prev_total_success_percentage or prev_total_success_percentage == 0.0 else "red"
    
    total_sign = "+" if total_success_percentage >= prev_total_success_percentage else ""
    total_diff = f"({total_sign}{total_success_percentage - prev_total_success_percentage:.0f})" if any_prev_rate and total_success_percentage != prev_total_success_percentage else ""

    # Constructing the markdown content
    md_content = []
    md_content.append(f"### Test Run Summary\n")
    md_content.append(f"- **Run from:** `{test_path}`")
    md_content.append(f"- **Iterations:** {iterations}")
    md_content.append(f"- **Total Success Rate (%):** ${{\\color{{{total_success_color}}} \\LARGE \\texttt {{{total_success_percentage:.2f}}} \\large \\texttt {{{total_diff}}} }}$\n")
    md_content.append(f"### Detailed Results\n")
    md_content.append(f"| Test Name | Success Rate (%) | Passes | Fails | Avg Time |")
    md_content.append(f"| --- | --- | --- | --- | --- |")

    for test_result in tests_results:
        prev_success_rate = float(total_benchmarks["benchmarks"][test_result["name"]] if total_benchmarks["benchmarks"].get(test_result["name"]) else 0.0)
        success_rate = (test_result['passes'] / (test_result['passes'] + test_result['fails'])) * 100
        color = "lightgreen" if success_rate > prev_success_rate and prev_success_rate != 0.0 else "none" if success_rate == prev_success_rate or prev_success_rate == 0.0 else "red"
        
        sign = "+" if success_rate >= prev_success_rate else ""
        diff = f"({sign}{success_rate - prev_success_rate:.0f})" if prev_success_rate != 0.0 and success_rate != prev_success_rate else ""

        avg_time = f"{test_result['avg_time']:.0f}s" if test_result['avg_time'] < 60 else f"{test_result['avg_time']/60:.2f}m"
        md_content.append(f"| `{test_result['name']}` | ${{\\color{{{color}}} \\large \\texttt {{{success_rate:.0f}}} \\normalsize \\texttt {{{diff}}} }}$ | ${{\\color{{{color}}} \\large \\texttt {{{test_result['passes']}}}}}$ | ${{\\color{{{color}}} \\large \\texttt {{{test_result['fails']}}}}}$ | {avg_time} |")

    md_content.append(f"\n**Total run time:** {total_run_time/60:.2f} minutes\n")

    for test_result in tests_results:
        success_rate = (test_result['passes'] / (test_result['passes'] + test_result['fails'])) * 100
        
        avg_time = f"{test_result['avg_time']:.0f}s" if test_result['avg_time'] < 60 else f"{test_result['avg_time']/60:.2f}m"
        print(f"| `{test_result['name']}` | {success_rate:.0f} | {test_result['passes']} | {test_result['fails']} | {avg_time} |")

    print(f"\n**Total run time:** {total_run_time/60:.2f} minutes\n")

    # Write the markdown content to a file
    with open(f"{output_dir}/summary.md", 'w') as summary_file:
        summary_file.write("\n".join(md_content))

if __name__ == "__main__":
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print("Usage: python benchmarks.py <save_results=-s> <path_to_test_file> <iterations> <benchmark_name>")
        sys.exit(1)

    should_save_results = sys.argv[1] == "-s"
    offset = 1 if should_save_results else 0
    test_path, iterations = sys.argv[1 + offset], int(sys.argv[2 + offset])
    benchmark_name = sys.argv[3 + offset] if len(sys.argv) == (4 + offset) else None

    path_parts = test_path.split(',')
    tests = []

    for path in path_parts:
        tests += collect_tests(path)

    # Filter unique tests
    tests = list(set(tests))

    if not tests:
        print("No tests found.")
        sys.exit(1)

    print("=" * 50)
    print(f"Target: {test_path}")
    print(f"Tests found: {len(tests)}")
    for test in tests:
        print(test)

    print("=" * 50)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    benchmark_label = benchmark_name if benchmark_name else str(timestamp)
    output_dir = f"benchmarks/{benchmark_label}"

    os.makedirs(output_dir, exist_ok=True)

    # Load existing benchmarks
    if os.path.exists("benchmarks.json"):
        with open("benchmarks.json", 'r') as f:
            total_benchmarks = json.load(f)
    else:
        total_benchmarks = {
            "benchmarks": {},
            "iterations": iterations
        }

    total_tests = len(tests)
    completed_tests = 0
    total_run_time = 0
    remaining_tests = total_tests
    tests_results = []

    for test in tests:
        print(f"\nRunning: {test}")
        avg_time_across_tests = total_run_time / completed_tests if completed_tests else 0
        pass_count, fail_count, run_times = run_test(test, iterations, avg_time_across_tests, completed_tests, remaining_tests - 1)
        test_time = sum(run_times)
        total_run_time += test_time
        completed_tests += 1
        remaining_tests -= 1
        avg_time = test_time / iterations if iterations else 0

        tests_results.append({
            'name': test,
            'passes': pass_count,
            'fails': fail_count,
            'avg_time': avg_time
        })

        test_dir = f"{test.replace('/', '_').replace('::', '_')}"
        with open(f"{output_dir}/{test_dir}/results.txt", 'w') as result_file:
            result_file.write(f"Test: {test}\n")
            for i, time in enumerate(run_times, 1):
                result_file.write(f"Iteration {i}: {'Pass' if i <= pass_count else 'Fail'} in {time:.2f} seconds\n")
            result_file.write(f"Average Time: {avg_time:.2f}s\n")
            result_file.write(f"Passes: {pass_count}, Fails: {fail_count}\n")
            
        print(f"\nEnded: {test}\n| Passes: {pass_count}, Fails: {fail_count}, Avg Time: {avg_time:.2f}s |")

    print("\n" + "=" * 50)
    print("All tests completed.")
    print("=" * 50 + "\n")
    print_summary_table(test_path, iterations, tests_results, total_run_time, output_dir, total_benchmarks)

    if should_save_results:
        run_benchmarks = {
            "benchmarks": {},
            "iterations": iterations
        }

        for result in tests_results:
            rate = result["passes"] / iterations * 100
            total_benchmarks["benchmarks"][result["name"]] = f"{rate:.2f}"
            run_benchmarks["benchmarks"][result["name"]] = f"{rate:.2f}"

        with open("benchmarks.json", 'w') as f:
            json.dump(total_benchmarks, f, indent=4)

        with open(f"{output_dir}/benchmarks.json", 'w') as f:
            json.dump(run_benchmarks, f, indent=4)

    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Summary written to: {output_dir}/summary.md")
