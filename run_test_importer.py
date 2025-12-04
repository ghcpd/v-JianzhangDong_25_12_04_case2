import sys
import importlib.util

def main():
    if len(sys.argv) < 2:
        print("Usage: run_test_importer.py script.py")
        return 2
    pyfile = sys.argv[1]
    spec = importlib.util.spec_from_file_location('mod', pyfile)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print('Loaded', pyfile)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
