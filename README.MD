# Moovit Patcher

Moovit patcher is a program that patches Moovit apk and bundles(!!).

## Features
|            Feature             | Availability |
|:------------------------------:|:------------:|
|             No Ads             |      ✔       |
|         Live Location          |      ✔       |

## Requirements
1. Python3
2. JDK 17+

## Installation

```bash
git clone https://github.com/Schwartzblat/MoovitPatcher.git

cd MoovitPatcher

git submodule update --init --recursive
```
Requirements installation:
```bash
pip install -r requirements.txt
```
## Usage

```bash
python main.py -p ./moovit.apkm -g YOUR_GOOGLE_API_KEY

unzip -q ./output.apk -d output_bundle_apks

adb install-multiple output_bundle_apks/*.apk
```

## Google API Key
To get a Google API key, follow these steps:
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Navigate to the "APIs & Services" section.
4. Click on "Enable APIs and Services" and search for the "Maps SDK for Android" and for "Places API (Legacy)" (https://console.cloud.google.com/apis/library/places-backend.googleapis.com).
5. Enable the API for your project.
6. Go to the "Credentials" tab and click on "Create Credentials".
7. Select "API Key" from the dropdown menu.
8. Copy the generated API key and use it in the Moovit Patcher.
9. Make sure to restrict the API key to your app's package name (`com.tranzmate`) and SHA-1 certificate fingerprint (see below) for security.

## Getting the SHA-1 certificate fingerprint
```bash
# assuming Android Studio is installed
# apksigner is supposed to be located at ~/Android/Sdk/build-tools/<version>/
apksigner verify --print-certs ./output_bundle_apks/base.apk
```

## Contributing

If you want to add patches you can open an issue and I will implement it, or you can add patches yourself and open pull request.

## Disclaimer

For educational purpose only or something like that. I am not responsible for any misuse of this software.

## Credits
I took the 0auth bypass method (with your own Google-Api key) from this great project:
https://github.com/Tom-stack3/moovit-patcher, so give him a star too :)