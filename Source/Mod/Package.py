import hashlib
import importlib.util
import json
import sys
from pathlib import Path

pstSpec = importlib.util.spec_from_file_location("shared_package", Path(__file__).parents[1] / "Tools/Package.py")
mod = importlib.util.module_from_spec(pstSpec)
pstSpec.loader.exec_module(mod)


def customize(zInput, strApp, stInfo, pRoot):
    byLogo = (pRoot / "Source/Mod/Resources/Omega172.png").read_bytes()
    if not byLogo.startswith(bytes.fromhex("89504e470d0a1a0a")):
        raise ValueError("Expected PNG logo")
    stDetails = {
        "branding": "Mod by Omega172, once per app launch",
        "logo_sha256": hashlib.sha256(byLogo).hexdigest(),
    }
    return {}, {strApp + "/Omega172.png": (byLogo, 0o100644)}, stDetails


def package(pRoot, strInput=""):
    return mod.package(pRoot, strInput, customize)


if __name__ == "__main__":
    print(json.dumps(package(Path(sys.argv[1]).resolve(), sys.argv[2] if len(sys.argv) > 2 else ""), indent=2))
