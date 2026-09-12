import re
from stitch.artifactory_generator.SimpleArtifactoryFinder import SimpleArtifactoryFinder, CLASS_NAME_RE


class AppAdUnitIdResolver(SimpleArtifactoryFinder):
    """Moovit's app-level MobileAdsManager ad-unit-id resolver.

    The manager owns a single method that maps a com.moovit.app.ads.AdSource to
    the Firebase-remote-config ad unit id to request. It already returns the
    empty string whenever the build/config says ads are disabled (the
    "is_ads_free_version" / "is_interstitial_ads_free_version" flags, the "na"
    sentinel and the rewarded ad-free period), and every caller treats an empty
    id as "there is no ad for this source".

    Anchors:
      class  -- the remote config key literal "is_interstitial_ads_free_version"
                (a wire key, unique to this class in the whole apk)
      method -- the single (AdSource)String method whose body reads the
                "is_ads_free_version" flag (the sibling fallback resolver has
                the same signature but does not read it)
    """

    AD_UNIT_ID_RE = re.compile(
        r'\.method public final (?P<method_name>\w+)'
        r'(?P<sig>\(Lcom/moovit/app/ads/AdSource;\)Ljava/lang/String;)'
        r'(?:(?!\.end method)[\s\S])*?"is_ads_free_version"')

    def __init__(self, args):
        super().__init__(args)
        self.is_once = True
        self.is_found = False

    def class_filter(self, class_data: str) -> bool:
        return '"is_interstitial_ads_free_version"' in class_data

    def extract_artifacts(self, artifacts: dict, class_data: str) -> None:
        matches = list(self.AD_UNIT_ID_RE.finditer(class_data))
        if len(matches) != 1:
            return
        class_name = CLASS_NAME_RE.match(class_data)
        if class_name is None:
            return
        artifacts['APPAD_ADUNIT_CLASS_NAME'] = class_name.groupdict().get('name').replace('/', '.')
        artifacts['APPAD_ADUNIT_METHOD_NAME'] = matches[0].groupdict().get('method_name')
        artifacts['APPAD_ADUNIT_METHOD_SIG'] = matches[0].groupdict().get('sig')
        self.is_found = True
