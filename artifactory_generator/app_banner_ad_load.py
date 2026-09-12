import re
from stitch.artifactory_generator.SimpleArtifactoryFinder import SimpleArtifactoryFinder, CLASS_NAME_RE


class AppBannerAdLoad(SimpleArtifactoryFinder):
    """com.moovit.app.ads.MoovitBannerAdView's "load the banner" entry.

    The no-argument void method that resolves the hosting activity, gives up via
    the view's own "removeAdView" path when there is no activity/application/ad
    source, and otherwise asks the app ads manager for an ad reference and
    attaches the resulting banner. It is the single place this view starts an ad
    request from (called by setAdSource, onSizeChanged, onWindowVisibilityChanged
    and the ads-updated broadcast receiver).

    Anchors:
      class  -- the surviving class name com/moovit/app/ads/MoovitBannerAdView
      method -- the only ()V in the class whose body logs the
                "Loading ad: adSource=%s" trace line
    """

    LOAD_RE = re.compile(
        r'\.method public final (?P<method_name>\w+)(?P<sig>\(\)V)'
        r'(?:(?!\.end method)[\s\S])*?"Loading ad: adSource=%s"')

    def __init__(self, args):
        super().__init__(args)
        self.is_once = True
        self.is_found = False

    def class_filter(self, class_data: str) -> bool:
        return '.class public Lcom/moovit/app/ads/MoovitBannerAdView;' in class_data

    def extract_artifacts(self, artifacts: dict, class_data: str) -> None:
        matches = list(self.LOAD_RE.finditer(class_data))
        if len(matches) != 1:
            return
        class_name = CLASS_NAME_RE.match(class_data)
        if class_name is None:
            return
        artifacts['APPAD_BANNER_LOAD_CLASS_NAME'] = class_name.groupdict().get('name').replace('/', '.')
        artifacts['APPAD_BANNER_LOAD_METHOD_NAME'] = matches[0].groupdict().get('method_name')
        artifacts['APPAD_BANNER_LOAD_METHOD_SIG'] = matches[0].groupdict().get('sig')
        self.is_found = True
