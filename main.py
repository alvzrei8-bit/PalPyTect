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

    
    print(f"[+] Scanning {target_file}...")
    try:
        if not MalwareScanner.scan(target_file):
            print("[!] Security Alert: malware detected. Dont obfuscate bad code!!!.")
            sys.exit(1)
    except Exception as e:
        print(f"[!] Scan Error: {e}")
        sys.exit(1)

    
    with open(target_file, 'r') as f:
        source = f.read()

    
    print("[+] compiling.. ")
    compiler = CustomCompiler()
    try:
        instructions, consts = compiler.compile(source)
    except Exception as e:
        print(f"[!] Compilation failed: {e}")
        sys.exit(1)

    
    print("[+] almost done..")
    generator = Generator(source) 
    protected_code = generator.generate_stub()

    
    output_file = f"protected_{target_file}"
    with open(output_file, 'w') as f:
        f.write(protected_code)

    print(f"[SUCCESS] Protected file written to: {output_file}")

if __name__ == "__main__":
    main()