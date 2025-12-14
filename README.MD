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
```
Requirements installation:
```bash
pip install -r requirements.txt
```
## Usage

```bash
python main.py -p ./moovit.apkm -g YOUR_GOOGLE_API_KEY

adb install-multiple output_bundle_apks/*.apk
```

## Google API Key
To get a Google API key, follow these steps:
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Navigate to the "APIs & Services" section.
4. Click on "Enable APIs and Services" and search for the "Maps SDK for Android".
5. Enable the API for your project.
6. Go to the "Credentials" tab and click on "Create Credentials".
7. Select "API Key" from the dropdown menu.
8. Copy the generated API key and use it in the Moovit Patcher.
9. Make sure to restrict the API key to your app's package name and SHA-1 certificate fingerprint for security.

## Contributing

If you want to add patches you can open an issue and I will implement it, or you can add patches yourself and open pull request.

## Disclaimer

For educational purpose only or something like that. I am not responsible for any misuse of this software.

## Credits
I took the 0auth bypass method (with your own Google-Api key) from this great project:
https://github.com/Tom-stack3/moovit-patcher, so give him a star too :)