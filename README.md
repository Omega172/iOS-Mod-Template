# iOS Mod Template

An arm64 iOS dylib starter using Theos, with builds on Linux or Windows through WSL.

## Features

- Empty mod entry point in `Source/Mod/Mod.mm`.
- Omega172 credits popup, shown once per app launch.
- Decrypted IPA packaging that preserves app identity and verifies retained files.

Add hooks and patches for your target app. No gameplay changes are included.

## Build

Edit `Project.json` to set the project name, SDK, minimum iOS target and C++ dialect. `ProjectName` controls output filenames.

Install Theos, its iOS compiler and the selected SDK in Linux, along with Python 3.11+. Set `THEOS` or use `$HOME/theos`. Project and toolchain paths must not contain spaces.

On Windows, run `Build.bat`. On Linux, run `bash ./Build.sh`. Output: `Build/Release/<ProjectName>.dylib`.

### Package a provided IPA

Unchanged files keep their original ZIP compression, avoiding recompression. CRC and retained-file integrity checks still run before publishing the output.

On Windows:

```powershell
.\Package.bat "C:/Path/Original-Decrypted.ipa"
```

On Linux:

```bash
bash ./Package.sh "/path/Original-Decrypted.ipa"
```

A direct HTTPS IPA URL also works. Omit the argument when exactly one IPA is in the project root.

Packaging prints progress every ten seconds and rejects simultaneous jobs. Large IPAs can take several minutes. Wait for the ready-to-sign message.

Output: `Build/Release/<ProjectName>-NeedsSigning.ipa`. Sign the complete IPA before sideloading. The original IPA and app identifiers are preserved. Library-only injection also needs `Source/Mod/Resources/Omega172.png` in the app bundle.

### Build with GitHub Actions

Use **Build and Draft IPA Release** with a version tag and decrypted IPA URL, or **Build and Draft Dylib Release** with a version tag. Both read `Project.json` and create draft releases.

### Tests

```bash
python3 -B -m unittest discover -s Source/Tests -p 'Test*.py'
```
