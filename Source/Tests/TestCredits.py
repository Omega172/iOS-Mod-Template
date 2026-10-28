import importlib.util
import json
import plistlib
import tempfile
import unittest
import zipfile
from pathlib import Path
import TestPackage

pstSpec = importlib.util.spec_from_file_location("credits_package", Path(__file__).parents[1] / "Mod/Package.py")
mod = importlib.util.module_from_spec(pstSpec)
pstSpec.loader.exec_module(mod)


class clCreditsTests(unittest.TestCase):
    def setUp(self):
        self.m_stTemporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.m_stTemporary.cleanup)
        self.m_pRoot = Path(self.m_stTemporary.name)
        (self.m_pRoot / "Build/Release").mkdir(parents=True)
        (self.m_pRoot / "Source/Mod/Resources").mkdir(parents=True)
        stConfig = {"ProjectName": "ExampleMod", "SdkVersion": "16.5", "MinimumIOSVersion": "15.0", "CxxStandard": "c++2b"}
        (self.m_pRoot / "Project.json").write_text(json.dumps(stConfig))
        (self.m_pRoot / "Build/Release/ExampleMod.dylib").write_bytes(TestPackage.image(uFileType=6))
        self.m_byLogo = (Path(__file__).parents[1] / "Mod/Resources/Omega172.png").read_bytes()
        (self.m_pRoot / "Source/Mod/Resources/Omega172.png").write_bytes(self.m_byLogo)
        self.m_byPlist = plistlib.dumps({"CFBundleIdentifier": "com.example.unchanged", "CFBundleDisplayName": "Original", "CFBundleExecutable": "Example", "CFBundleVersion": "12"}, fmt=plistlib.FMT_BINARY)
        self.m_pInput = self.m_pRoot / "Original.ipa"
        with zipfile.ZipFile(self.m_pInput, "w") as z:
            z.writestr("Payload/Example.app/Info.plist", self.m_byPlist)
            z.writestr("Payload/Example.app/Example", TestPackage.image())

    def test_logo_is_packaged_without_changing_app_identity(self):
        stReport = mod.package(self.m_pRoot, str(self.m_pInput))
        with zipfile.ZipFile(stReport["output"]) as z:
            self.assertEqual(z.read("Payload/Example.app/Omega172.png"), self.m_byLogo)
            self.assertEqual(z.read("Payload/Example.app/Info.plist"), self.m_byPlist)
            self.assertEqual(z.getinfo("Payload/Example.app/Omega172.png").external_attr >> 16, 0o100644)
        self.assertEqual(stReport["branding"], "Mod by Omega172")

    def test_invalid_logo_is_rejected(self):
        (self.m_pRoot / "Source/Mod/Resources/Omega172.png").write_bytes(b"invalid")
        with self.assertRaisesRegex(ValueError, "Expected PNG"):
            mod.package(self.m_pRoot, str(self.m_pInput))

    def test_existing_logo_is_not_overwritten(self):
        with zipfile.ZipFile(self.m_pInput, "a") as z:
            z.writestr("Payload/Example.app/Omega172.png", b"existing app resource")
        with self.assertRaisesRegex(ValueError, "Invalid custom added file"):
            mod.package(self.m_pRoot, str(self.m_pInput))


if __name__ == "__main__":
    unittest.main()
