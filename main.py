import sys
import os
from analyzer.malware_scanner import MalwareScanner
from core.compiler import CustomCompiler
from core.generator import Generator

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <target_file.py>")
        sys.exit(1)

    target_file = sys.argv[1]

    # 1. Security Analysis
    print(f"[+] Scanning {target_file}...")
    try:
        if not MalwareScanner.scan(target_file):
            print("[!] Security Alert: Malicious patterns detected.")
            sys.exit(1)
    except Exception as e:
        print(f"[!] Scan Error: {e}")
        sys.exit(1)

    # 2. Read Source
    with open(target_file, 'r') as f:
        source = f.read()

    # 3. Compile to IR
    print("[+] Compiling to IR...")
    compiler = CustomCompiler()
    try:
        instructions, consts = compiler.compile(source)
    except Exception as e:
        print(f"[!] Compilation failed: {e}")
        sys.exit(1)

    # 4. Generate Polymorphic Stub
    print("[+] Generating Polymorphic VM...")
    # Matches the class name in core/generator.py
    generator = Generator(instructions, consts) 
    protected_code = generator.generate_stub()

    # 5. Write Output
    output_file = f"protected_{target_file}"
    with open(output_file, 'w') as f:
        f.write(protected_code)

    print(f"[SUCCESS] Protected file written to: {output_file}")

if __name__ == "__main__":
    main()
