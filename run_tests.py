import sys
import os

def check_file_for_patterns(path, patterns):
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()
    return all(p in src for p in patterns)


def main():
    if len(sys.argv) < 3:
        print("Usage: run_tests.py <file> <mode:vulnerable|fixed>")
        return 2
    path = sys.argv[1]
    mode = sys.argv[2]
    if not os.path.exists(path):
        print("file not found", path)
        return 2
    if mode == 'vulnerable':
        patterns = [
            "PAYMENT_TOKEN =",
            "hashlib.md5",
            "WHERE id = '%s'",
            "subprocess.Popen",
        ]
        ok = check_file_for_patterns(path, patterns)
        if ok:
            print("VULNERABLE patterns present in", path)
            return 0
        else:
            print("Expected vulnerable patterns NOT found in", path)
            return 1
    elif mode == 'fixed':
        bad_patterns = ["hashlib.md5", "subprocess.Popen", "WHERE id = '%s'"]
        with open(path, 'r', encoding='utf-8') as f:
            src = f.read()
        ok = all(bp not in src for bp in bad_patterns) and 'hmac.new' in src and "WHERE id = ?" in src
        if ok:
            print("Fixed secure patterns present in", path)
            return 0
        else:
            print("Secure patterns NOT found as expected in", path)
            return 1
    else:
        print("Unknown mode", mode)
        return 2


if __name__ == '__main__':
    sys.exit(main())
