import os
import sys
import importlib.util
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
import math
import time

def get_scraptor_files():
    """Find all scraptor files in scraptor/subfolders"""
    base_dir = "scraptor"
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

def load_and_run_scraptor(scraptor_info):
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
            module.run()
            print(f"Completed {scraptor_info['name']}")
            return True
        else:
            print(f"No 'run' function found in {scraptor_info['name']}")
            return False
            
    except Exception as e:
        print(f"Error running {scraptor_info['name']}: {e}")
        return False
    finally:
        if scraptor_info['module_path'] in sys.path:
            sys.path.remove(scraptor_info['module_path'])

def run_parallel(scraptor_files):
    """Run scraptors in parallel with optimal core distribution"""
    num_scraptors = len(scraptor_files)
    
    if num_scraptors == 0:
        print("No scraptors found.")
        return
    
    if num_scraptors == 1:
        print("Running single scraptor...")
        load_and_run_scraptor(scraptor_files[0])
        return
    
    num_cores = multiprocessing.cpu_count()
    usable_cores = max(1, num_cores - 1) if num_cores > 4 else num_cores
    
    processes_to_use = min(usable_cores, num_scraptors)
    
    scraptors_per_process = math.ceil(num_scraptors / processes_to_use)
    
    print(f"Running {num_scraptors} scraptors using {processes_to_use} processes")
    print(f"Distribution: ~{scraptors_per_process} scraptors per process")
    
    scraptor_groups = []
    for i in range(0, num_scraptors, scraptors_per_process):
        group = scraptor_files[i:i + scraptors_per_process]
        scraptor_groups.append(group)
    
    with ProcessPoolExecutor(max_workers=processes_to_use) as executor:
        futures = []
        
        for group in scraptor_groups:
            future = executor.submit(run_scraptor_group, group)
            futures.append(future)
        
        for future in as_completed(futures):
            try:
                result = future.result()
                if not result:
                    print("A scraptor group failed")
            except Exception as e:
                print(f"Process error: {e}")

def run_scraptor_group(scraptor_group):
    """Run a group of scraptors sequentially in a single process"""
    results = []
    for scraptor_info in scraptor_group:
        result = load_and_run_scraptor(scraptor_info)
        results.append(result)
    return all(results)

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
    
    run_parallel(scraptor_files)
    end = time.perf_counter()

    elp = end - start 

    print("All scraptors completed.")
    # print the time here
    print(f"{int(elp)} second untill getting the hole ads")
