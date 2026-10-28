import hashlib
import importlib.util
import json
import sys
import threading
import time
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


def package_with_progress(pRoot, strInput=""):
    import fcntl

    pOutput = pRoot / "Build/Release"
    pOutput.mkdir(parents=True, exist_ok=True)
    with (pOutput / ".Packaging.lock").open("a") as hLock:
        try:
            fcntl.flock(hLock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError("Packaging is already running for this project. Wait for it to finish before starting another build.") from None
        aExisting = set(pOutput.glob("Package-*"))
        dStart = time.monotonic()
        hFinished = threading.Event()

        def progress():
            while not hFinished.wait(10):
                uBytes = 0
                for pDirectory in set(pOutput.glob("Package-*")) - aExisting:
                    for pArchive in pDirectory.glob("*.ipa"):
                        try:
                            uBytes += pArchive.stat().st_size
                        except FileNotFoundError:
                            pass
                print(f"Packaging: {time.monotonic() - dStart:.0f}s elapsed, temporary IPA {uBytes / (1024 * 1024):.1f} MiB. Writing or verifying archive; please wait.", file=sys.stderr, flush=True)

        print("Packaging IPA: checking the input, writing the archive and verifying retained files. Large IPAs can take several minutes.", file=sys.stderr, flush=True)
        hProgress = threading.Thread(target=progress, daemon=True)
        hProgress.start()
        try:
            stReport = package(pRoot, strInput)
            print(f"Packaging verified in {time.monotonic() - dStart:.1f}s. Ready to sign: {stReport['output']}", file=sys.stderr, flush=True)
            return stReport
        finally:
            hFinished.set()
            hProgress.join()


if __name__ == "__main__":
    try:
        print(json.dumps(package_with_progress(Path(sys.argv[1]).resolve(), sys.argv[2] if len(sys.argv) > 2 else ""), indent=2))
    except (ValueError, OSError) as stError:
        print(f"Packaging failed: {stError}", file=sys.stderr, flush=True)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Packaging cancelled.", file=sys.stderr, flush=True)
        sys.exit(130)
