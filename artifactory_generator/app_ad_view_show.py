import re
from stitch.artifactory_generator.SimpleArtifactoryFinder import SimpleArtifactoryFinder, CLASS_NAME_RE


class AppAdViewShow(SimpleArtifactoryFinder):
    """com.moovit.app.ads.MoovitAdView's "build and request the banner" entry.

    The only method of the (non obfuscated) view class that takes
    (MoovitApplication, MoovitBaseComponentActivity, AdSource, String adUnitId)
    and returns void. Its body constructs a Google mobile-ads banner AdView,
    calls load on it, adds it to the view's FrameLayout and reports the AD
    analytics event. Every early-out inside it ends in the view's own
    "removeAdView" path, so suppressing it is behaviour the class already
    supports.

    Anchors:
      class  -- the surviving class name com/moovit/app/ads/MoovitAdView
      method -- the unique four argument signature, made of three
                non-obfuscated com.moovit types plus String
    """

    SHOW_RE = re.compile(
        r'\.method public final (?P<method_name>\w+)'
        r'(?P<sig>\(Lcom/moovit/MoovitApplication;Lcom/moovit/MoovitBaseComponentActivity;'
        r'Lcom/moovit/app/ads/AdSource;Ljava/lang/String;\)V)')

    def __init__(self, args):
        super().__init__(args)
        self.is_once = True
        self.is_found = False

    def class_filter(self, class_data: str) -> bool:
        return '.class public Lcom/moovit/app/ads/MoovitAdView;' in class_data

    def extract_artifacts(self, artifacts: dict, class_data: str) -> None:
        matches = list(self.SHOW_RE.finditer(class_data))
        if len(matches) != 1:
            return
        class_name = CLASS_NAME_RE.match(class_data)
        if class_name is None:
            return
        artifacts['APPAD_VIEW_SHOW_CLASS_NAME'] = class_name.groupdict().get('name').replace('/', '.')
        artifacts['APPAD_VIEW_SHOW_METHOD_NAME'] = matches[0].groupdict().get('method_name')
        artifacts['APPAD_VIEW_SHOW_METHOD_SIG'] = matches[0].groupdict().get('sig')
        self.is_found = True
