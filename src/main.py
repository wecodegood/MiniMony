import os
import sys
import importlib.util
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
import math
import time

def get_scraptor_files():
    """Find all scraptor files in scraptor/subfolders (absolute paths)

    This resolves the `scraptor` directory relative to this module file so
    the function works regardless of the current working directory.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(script_dir, "scraptor")

    if not os.path.exists(base_dir):
        print(f"Directory '{base_dir}' not found.")
        return []

    scraptor_files = []

    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path):
            target_file = f"{item}Scraptor.py"
            target_path = os.path.join(item_path, target_file)

            if os.path.exists(target_path):
                scraptor_files.append({
                    'name': item,
                    'path': target_path,
                    'module_path': os.path.dirname(target_path)
                })

    return scraptor_files

def load_and_run_scraptor(scraptor_info, product=None):
    """Load and execute a single scraptor module"""
    try:
        sys.path.insert(0, scraptor_info['module_path'])

        spec = importlib.util.spec_from_file_location(
            scraptor_info['name'], 
            scraptor_info['path']
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if hasattr(module, 'run'):
            print(f"Running {scraptor_info['name']}...")
            # Call the scraptor's run() and capture its return value.
            try:
                if product is not None:
                    data = module.run(product)
                else:
                    data = module.run()
            except TypeError:
                # If the scraptor's run() doesn't accept args
                data = module.run()

            print(f"Completed {scraptor_info['name']}")
            return {'name': scraptor_info['name'], 'ok': True, 'data': data}
        else:
            msg = f"No 'run' function found in {scraptor_info['name']}"
            print(msg)
            return {'name': scraptor_info['name'], 'ok': False, 'error': msg}
            
    except Exception as e:
        print(f"Error running {scraptor_info['name']}: {e}")
        return False
    finally:
        if scraptor_info['module_path'] in sys.path:
            sys.path.remove(scraptor_info['module_path'])

def run_parallel(scraptor_files, product=None):
    """Run scraptors in parallel (one scraptor per worker)"""
    num_scraptors = len(scraptor_files)

    if num_scraptors == 0:
        print("No scraptors found.")
        return

    results = {}

    if num_scraptors == 1:
        print("Running single scraptor...")
        res = load_and_run_scraptor(scraptor_files[0], product=product)
        results[res['name']] = res
        return results

    num_cores = multiprocessing.cpu_count()
    usable_cores = max(1, num_cores - 1) if num_cores > 4 else num_cores

    workers = min(usable_cores, num_scraptors)

    print(f"Running {num_scraptors} scraptors using {workers} worker processes")

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(load_and_run_scraptor, s, product): s for s in scraptor_files}

        for future in as_completed(futures):
            scr = futures[future]
            try:
                res = future.result()
                # res is a dict with keys: name, ok, data/error
                results[res['name']] = res
                if not res.get('ok'):
                    print(f"Scraptor reported failure: {res.get('name')} {res.get('error')}")
            except Exception as e:
                print(f"Process error for {scr['name']}: {e}")
                results[scr['name']] = {'name': scr['name'], 'ok': False, 'error': str(e)}

    return results

def run_scraptor_group(scraptor_group):
    """Run a group of scraptors sequentially in a single process"""
    results = []
    for scraptor_info in scraptor_group:
        result = load_and_run_scraptor(scraptor_info)
        results.append(result)
    return all(results)


def run_scraptors(product=None, parallel=True):
    """Public helper to run all scraptors.

    - `product`: optional search term passed to each scraptor's `run()`.
    - `parallel`: use process pool when True.
    """
    scraptor_files = get_scraptor_files()
    if not scraptor_files:
        print("No scraptor files found to run.")
        return {}

    if parallel:
        results = run_parallel(scraptor_files, product=product)
    else:
        results = {}
        for s in scraptor_files:
            res = load_and_run_scraptor(s, product=product)
            results[res['name']] = res

    # Normalize results to a simple mapping name -> data (or empty list/error)
    output = {}
    for name, info in results.items():
        if info.get('ok'):
            output[name] = info.get('data')
        else:
            output[name] = []

    return output

if __name__ == "__main__":
    start = time.perf_counter()

    scraptor_files = get_scraptor_files()
    
    if not scraptor_files:
        print("No scraptor files found. Expected structure:")
        print("scraptor/")
        print("├── site1/")
        print("│   └── site1Scraptor.py")
        print("├── site2/")
        print("│   └── site2Scraptor.py")
        sys.exit(1)
    
    print(f"Found {len(scraptor_files)} scraptors:")
    for scraptor in scraptor_files:
        print(f"  - {scraptor['name']}")
    
    # Default: run all scraptors (no product query) using parallel executor
    run_parallel(scraptor_files)
    end = time.perf_counter()

    elp = end - start 

    print("All scraptors completed.")
    # print the time here
    print(f"{int(elp)} second untill getting the hole ads")
