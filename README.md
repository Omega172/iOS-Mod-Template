# iOS Mod Template

An arm64 iOS dylib starter using Theos, Linux or Windows through WSL. Add your mod code to `Source/Mod/Mod.mm`.

## Configure

Edit `Project.json`:

```json
{
  "ProjectName": "MyMod",
  "SdkVersion": "16.5",
  "MinimumIOSVersion": "15.0",
  "CxxStandard": "c++2b"
}
```

`ProjectName` controls the dylib target, install name, IPA filename and release asset names. Use letters, numbers or underscores, starting with a letter. No folders or scripts need renaming.

The other settings select the installed iOS SDK, minimum deployment target and compiler dialect. `c++2b` enables the C++23 dialect supported by the existing toolchain. Use a newer supported dialect when upgrading your compiler.

These settings do not change the app. The packager preserves its bundle ID, display name, version and `Info.plist` bytes. Mod code and signing choices are separate from the project name.

## Build

Packaging prints progress every ten seconds, including elapsed time and temporary IPA size. Simultaneous packaging jobs for the same project are rejected. Wait for the ready-to-sign message before deploying. Large IPAs can take several minutes to write and verify.


Keep Theos, its Linux iOS toolchain and the selected SDK inside Linux. Set `THEOS`, or use `$HOME/theos`. Install Python 3.11+ in the build environment. Project and toolchain paths must not contain spaces.

Windows uses whichever distribution and user plain `wsl` selects:

```powershell
.\Build.bat
.\Package.bat "C:/Path/Original-Decrypted.ipa"
```

Linux:

```bash
bash ./Build.sh
bash ./Package.sh "/path/Original-Decrypted.ipa"
```

You can pass a direct HTTPS IPA URL instead of a file path. Omit the argument when exactly one IPA is in the project root.

Outputs are `Build/Release/<ProjectName>.dylib` and `Build/Release/<ProjectName>-NeedsSigning.ipa`. Successful packaging replaces the previous IPA. The source IPA is unchanged.

Sign the entire output IPA, including embedded frameworks and dylibs, before installing. Use the existing app's bundle ID and compatible signing identity when updating an installation. Certificates and device-specific deploy scripts are not included.

## GitHub Actions

- **Build and Draft IPA Release** takes a new version tag and a direct HTTPS decrypted IPA URL. Its draft contains the IPA and dylib.
- **Build and Draft Dylib Release** takes a new version tag. Its draft contains only the dylib.

Both read `Project.json`, install Theos and the configured SDK, run tests and generate a changelog since the previous published release. Review the draft under Releases. The workflow version is the release tag and does not change the app's version.

## Scope

The starter includes the Omega172 credits popup, shown once per app launch with the logo, Dismiss button and optional GitHub link. It fades away after ten seconds. `Source/Mod/Credits.m` handles the card and packaging automatically adds `Source/Mod/Resources/Omega172.png` to the app bundle. Library-only injection also needs that PNG in the app bundle.

The mod entry point is empty. No ad, currency or gameplay patches are included. Hooks and offsets must be implemented for each app.

Packaging supports decrypted arm64 executables, including arm64 slices in universal binaries. Other slices remain unchanged. Injection requires existing Mach-O header padding. Insufficient padding or declared encryption causes an error rather than shifting binary sections. A cleared encryption flag alone does not prove a valid decrypted dump.

Old signature folders and embedded provisioning profiles are omitted for re-signing. All other retained files are checked byte for byte. The package is unsigned and device behavior still needs testing. Apps with extensions may need additional provisioning profiles when signing.

IPAs, signing credentials, Theos, build outputs and caches are excluded by `.gitignore`. Select a license in `LICENSE` before publishing.

Tests:

```bash
python3 -B -m unittest discover -s Source/Tests -p 'Test*.py'
```
