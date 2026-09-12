import re

from stitch.artifactory_generator.SimpleArtifactoryFinder import SimpleArtifactoryFinder, CLASS_NAME_RE


class PremiumState(SimpleArtifactoryFinder):
    """Locates Moovit's synchronous "is Moovit Premium active" boolean.

    The method is a static ``(Context) -> boolean`` that ANDs the local
    subscription check with the ``is_moovit_premium_enabled`` remote-config
    kill switch, and it is what the app consults for the premium look-and-feel
    and as the initial value of the injected ``isPremium`` state flow.

    Anchors, none of which R8 can rename:
      * the remote-config key string literal ``is_moovit_premium_enabled``,
      * the framework descriptor ``(Landroid/content/Context;)Z``.
    """

    DECLARATION_RE = re.compile(r'\.method public static \w+\(Landroid/content/Context;\)Z')

    IS_PREMIUM_RE = re.compile(
        r'\.method public static (?P<method_name>\w+)(?P<sig>\(Landroid/content/Context;\)Z)'
        r'(?:(?!\.end method)[\s\S])*?"is_moovit_premium_enabled"')

    def __init__(self, args):
        super().__init__(args)
        self.is_once = True
        self.is_found = False

    def class_filter(self, class_data: str) -> bool:
        return ('"is_moovit_premium_enabled"' in class_data
                and self.DECLARATION_RE.search(class_data) is not None)

    def extract_artifacts(self, artifacts: dict, class_data: str) -> None:
        matches = list(self.IS_PREMIUM_RE.finditer(class_data))
        if len(matches) != 1:
            return
        class_match = CLASS_NAME_RE.match(class_data)
        if class_match is None:
            return
        artifacts['PREMIUM_STATE_CLASS_NAME'] = \
            class_match.groupdict().get('name').replace('/', '.')
        artifacts['PREMIUM_STATE_METHOD_NAME'] = matches[0].groupdict().get('method_name')
        artifacts['PREMIUM_STATE_METHOD_SIG'] = matches[0].groupdict().get('sig')
        self.is_found = True
