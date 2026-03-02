import os
import sys

module_path = [os.path.dirname(os.path.abspath(__file__))]
for path in module_path:
    if path not in sys.path:
        sys.path.append(path)

if __name__ == "__main__":
    print("Welcome to the Cryogenic Material Properties package...")
    print("This package was created by Henry Nachman and others for the general public.")
    from setup import VERSION
    print(f"Current version is v{VERSION}")

    print("""Summary__________
    The Cryogenic Material Properties package is designed to enable a suite of thermal conductivity calculations and modeling using a library of thermal conductivity data.
     """)