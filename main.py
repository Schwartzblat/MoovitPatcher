import argparse
from pathlib import Path

from stitch import Stitch
from stitch.common import ExternalModule
from artifactory_generator.subscription_manager import SubscriptionManager
# premium / subscription state
from artifactory_generator.premium_state import PremiumState
from artifactory_generator.premium_feature_packages import PremiumFeaturePackages
# paywall / feature gates
from artifactory_generator.block_paywall import BlockPaywall
# ad loaders (com.moovit.ads)
# app ad layer (com.moovit.app.ads)
from artifactory_generator.app_ad_unit_id_resolver import AppAdUnitIdResolver
from artifactory_generator.app_ad_source_age_gate import AppAdSourceAgeGate
from artifactory_generator.app_ad_view_show import AppAdViewShow
from artifactory_generator.app_banner_ad_load import AppBannerAdLoad
from artifactory_generator.app_map_ads_layer import AppMapAdsLayer


# Stitch writes this into the target's manifest as the provider's android:name,
# and the paywall module generates a class of that name from PAYWALL_PROVIDER_CLASS.
# Both are derived from this one constant so they cannot drift: a manifest naming
# a class that is not in the dex installs fine and dies at launch.
PAYWALL_PROVIDER = 'com.paywall.InitProviderPaywallMoovit'


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
    parser.add_argument('--no-sign', dest='should_sign', help='Whether to sign the output APK', action='store_false',
                        required=False, default=True)
    parser.add_argument('--extra-artifacts', dest='extra_artifacts',
                        help='Extra artifact to add to the artifactory, in the format "key:value"',
                        required=False, default=[], nargs='+')
    parser.add_argument('--paywall', dest='paywall', help='Whether to add the paywall patch', required=False,
                        default=None)
    args, _ = parser.parse_known_args()
    return args


def main():
    args = get_args()
    extra_artifacts = {artifact.split(':')[0]: artifact.split(':')[1] for artifact in args.extra_artifacts}
    external_modules = [
        ExternalModule(Path(__file__).parent / './smali_generator',
                       'com.smali_generator.InitProviderMoovit')
    ]
    if args.paywall is not None:
        extra_artifacts.setdefault('PAYWALL_PROVIDER_CLASS', PAYWALL_PROVIDER.rsplit('.', 1)[1])
        external_modules.append(ExternalModule(Path(args.paywall), PAYWALL_PROVIDER))
    artifactory_list = [
        SubscriptionManager(args),
        PremiumState(args),
        PremiumFeaturePackages(args),
        BlockPaywall(args),
        AppAdUnitIdResolver(args),
        AppAdSourceAgeGate(args),
        AppAdViewShow(args),
        AppBannerAdLoad(args),
        AppMapAdsLayer(args),
    ]
    with Stitch(
            apk_path=args.apk_path,
            output_apk=args.output,
            temp_path=args.temp_path,
            artifactory_list=artifactory_list,
            google_api_key=args.api_key,
            external_modules=external_modules,
            should_sign=args.should_sign,
            extra_artifacts=extra_artifacts,
    ) as stitch:
        stitch.patch()


if __name__ == '__main__':
    main()
