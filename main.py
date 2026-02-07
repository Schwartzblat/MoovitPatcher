import argparse
from pathlib import Path

from stitch import Stitch
from stitch.common import ExternalModule
from artifactory_generator.subscription_manager import SubscriptionManager


def get_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-p', '--apk-path', dest='apk_path', help='APK path', required=True)
    parser.add_argument('-o', '--output', dest='output', help='Output APK path', required=False, default='output.apk')
    parser.add_argument('-t', '--temp', dest='temp_path', help='Temp path for extracted content', required=False,
                        default='./temp')
    parser.add_argument('-g', '--google-api-key', dest='api_key', help='Custom google api key', required=False,
                        default=None)
    parser.add_argument('--artifactory', dest='artifactory', help='Artifactory path', required=False,
                        default='./artifactory.json')
    return parser.parse_args()


def main():
    args = get_args()
    artifactory_list = [
        SubscriptionManager(args),
    ]
    with Stitch(
            apk_path=args.apk_path,
            output_apk=args.output,
            temp_path=args.temp_path,
            artifactory_list=artifactory_list,
            google_api_key=args.api_key,
            external_modules=[ExternalModule(Path('./smali_generator'),
                                             'invoke-static {}, Lcom/smali_generator/TheAmazingPatch;->on_load()V')]
    ) as stitch:
        stitch.patch()


if __name__ == '__main__':
    main()
