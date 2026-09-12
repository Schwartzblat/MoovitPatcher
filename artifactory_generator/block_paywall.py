import re
from stitch.artifactory_generator.SimpleArtifactoryFinder import SimpleArtifactoryFinder, CLASS_NAME_RE


class BlockPaywall(SimpleArtifactoryFinder):
    """Locates the "is the hard block paywall active?" predicate.

    MoovitAppActivity consults it on every launch and, when it returns true,
    replaces the requested activity with
    ``com.moovit.app.plus.paywall.BlockPaywallActivity``:

        invoke-static {p0}, Lee1;->a(Lcom/moovit/MoovitActivity;)Z
        move-result v0
        if-nez v0, :cond_7          # true  -> keep going towards the paywall
        goto :goto_3                # false -> run the activity normally
        ...
        const-string v8, "com.moovit.app.plus.paywall.BlockPaywallActivity"

    The holder class is anchored on its SharedPreferences keys, which are
    persisted data and therefore cannot be renamed: "user_acquisition" occurs
    in this class only, and it is paired with the "block_paywall" preference
    file name. The predicate itself is pinned by its parameter type
    ``com/moovit/MoovitActivity`` (a surviving Moovit class name) plus the
    "block_paywall" literal inside the body.
    """

    IS_BLOCKED_RE = re.compile(
        r'\.method public static final (?P<method_name>\w+)'
        r'(?P<sig>\(Lcom/moovit/MoovitActivity;\)Z)'
        r'(?:(?!\.end method)[\s\S])*?'
        r'"block_paywall"'
        r'(?:(?!\.end method)[\s\S])*?'
        r'Ljava/lang/Boolean;->booleanValue\(\)Z')

    def __init__(self, args):
        super().__init__(args)
        self.is_once = True
        self.is_found = False

    def class_filter(self, class_data: str) -> bool:
        return '"user_acquisition"' in class_data and '"block_paywall"' in class_data

    def extract_artifacts(self, artifacts: dict, class_data: str) -> None:
        matches = list(self.IS_BLOCKED_RE.finditer(class_data))
        if len(matches) != 1:
            return
        class_match = CLASS_NAME_RE.match(class_data)
        if class_match is None:
            return
        artifacts['PAYWALL_BLOCK_CLASS_NAME'] = \
            class_match.groupdict().get('name').replace('/', '.')
        artifacts['PAYWALL_BLOCK_METHOD_NAME'] = matches[0].groupdict().get('method_name')
        artifacts['PAYWALL_BLOCK_METHOD_SIG'] = matches[0].groupdict().get('sig')
        self.is_found = True
