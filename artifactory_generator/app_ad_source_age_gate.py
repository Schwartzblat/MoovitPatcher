import re
from stitch.artifactory_generator.SimpleArtifactoryFinder import SimpleArtifactoryFinder, CLASS_NAME_RE


class AppAdSourceAgeGate(SimpleArtifactoryFinder):
    """"Is this ad source allowed for a user this old?" helper.

    A static (AdSource, long userAgeSeconds) -> boolean that compares the user
    age against the remote config value "<adUnitIdKey>_user_age_seconds" and
    returns true when the source may be requested. Moovit checks it before
    building a banner in MoovitAdView, before showing an interstitial and
    before pre-loading a source.

    Anchors:
      class  -- the remote config key suffix literal "_user_age_seconds"
                (unique to this class in the whole apk)
      method -- the single static (AdSource, long)Z whose body reads that key
    """

    AGE_GATE_RE = re.compile(
        r'\.method public static (?P<method_name>\w+)'
        r'(?P<sig>\(Lcom/moovit/app/ads/AdSource;J\)Z)'
        r'(?:(?!\.end method)[\s\S])*?"_user_age_seconds"')

    def __init__(self, args):
        super().__init__(args)
        self.is_once = True
        self.is_found = False

    def class_filter(self, class_data: str) -> bool:
        return '"_user_age_seconds"' in class_data

    def extract_artifacts(self, artifacts: dict, class_data: str) -> None:
        matches = list(self.AGE_GATE_RE.finditer(class_data))
        if len(matches) != 1:
            return
        class_name = CLASS_NAME_RE.match(class_data)
        if class_name is None:
            return
        artifacts['APPAD_SOURCE_AGE_CLASS_NAME'] = class_name.groupdict().get('name').replace('/', '.')
        artifacts['APPAD_SOURCE_AGE_METHOD_NAME'] = matches[0].groupdict().get('method_name')
        artifacts['APPAD_SOURCE_AGE_METHOD_SIG'] = matches[0].groupdict().get('sig')
        self.is_found = True
