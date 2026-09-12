import re

from stitch.artifactory_generator.SimpleArtifactoryFinder import SimpleArtifactoryFinder

# Rename-proof anchors. The two string literals are a broadcast action and an
# analytics constant, both load-bearing at runtime; the class path fragment is
# one of the com/moovit/** names that survived R8.
FOREGROUND_ACTION = '"com.moovit.app.action.foreground"'
STATE_ENUM_PATH = 'premium/packages/SubscriptionPackageState;'
ACTIVE_ANALYTICS_CONSTANT = '"package_state_active"'


class PremiumFeaturePackages(SimpleArtifactoryFinder):
    """Locates the per-feature Moovit Plus entitlement state accessor.

    Every premium feature (ad free, AI search, trip on map, traffic on map,
    safe ride, share ride, trip plan sort / advanced route / time picker, trip
    insights, ...) is represented by a subscription-package object that caches
    one enum state: INACTIVE / OFFER / PENDING_ACTIVATION / ACTIVE. The app's
    feature gate reads that cached state and grants access only when it is
    ACTIVE, so the cached-state getter is the entitlement source of truth.

    Two classes are inspected, in whatever order the smali walk reaches them:

      * the abstract subscription-package base class, recognised by the
        foreground broadcast action plus a reference to the state enum. Its
        cached-state getter is the only ``public final () -> <state enum>``
        method that casts a value to the state enum before falling back to a
        constant of it (the sibling getter that returns the active state
        unconditionally has no such cast).
      * the state enum itself, recognised by the analytics constant of its
        active entry, which yields the field that holds that entry.

    Nothing fires until both halves agree on the same state enum class.
    """

    STATE_GETTER_RE = re.compile(
        r'\.method public final (?P<method_name>\w+)(?P<sig>\(\)L(?P<state_class>[\w/$]+);)'
        r'(?:(?!\.end method)[\s\S])*?check-cast \w+, L(?P=state_class);'
        r'(?:(?!\.end method)[\s\S])*?sget-object \w+, L(?P=state_class);->\w+:')

    ACTIVE_STATE_RE = re.compile(
        ACTIVE_ANALYTICS_CONSTANT + r'(?:(?!\.end method)[\s\S])*?'
        r'sput-object \w+, L(?P<state_class>[\w/$]+);->(?P<active_field>\w+):L(?P=state_class);')

    def __init__(self, args):
        super().__init__(args)
        self.is_once = True
        self.is_found = False
        self.package_class = None
        self.getter_name = None
        self.getter_sig = None
        self.state_class = None
        self.active_field = None

    def class_filter(self, class_data: str) -> bool:
        if ACTIVE_ANALYTICS_CONSTANT in class_data:
            return True
        return FOREGROUND_ACTION in class_data and STATE_ENUM_PATH in class_data

    def extract_artifacts(self, artifacts: dict, class_data: str) -> None:
        if ACTIVE_ANALYTICS_CONSTANT in class_data:
            self._extract_active_state(class_data)
        else:
            self._extract_state_getter(class_data)
        self._emit(artifacts)

    def _extract_state_getter(self, class_data: str) -> None:
        matches = list(self.STATE_GETTER_RE.finditer(class_data))
        if len(matches) != 1:
            return
        class_match = re.match(r'\.class .*?L(?P<name>[\w/$]+);', class_data)
        if class_match is None:
            return
        groups = matches[0].groupdict()
        self.package_class = class_match.groupdict().get('name')
        self.getter_name = groups.get('method_name')
        self.getter_sig = groups.get('sig')

    def _extract_active_state(self, class_data: str) -> None:
        matches = list(self.ACTIVE_STATE_RE.finditer(class_data))
        if len(matches) != 1:
            return
        groups = matches[0].groupdict()
        self.state_class = groups.get('state_class')
        self.active_field = groups.get('active_field')

    def _emit(self, artifacts: dict) -> None:
        if None in (self.package_class, self.getter_name, self.getter_sig,
                    self.state_class, self.active_field):
            return
        # Both halves must describe the same enum, otherwise the shape changed.
        if self.getter_sig != '()L' + self.state_class + ';':
            return
        artifacts['PREMIUM_FEATURE_PACKAGE_CLASS_NAME'] = self.package_class.replace('/', '.')
        artifacts['PREMIUM_FEATURE_PACKAGE_METHOD_NAME'] = self.getter_name
        artifacts['PREMIUM_FEATURE_PACKAGE_METHOD_SIG'] = self.getter_sig
        artifacts['PREMIUM_FEATURE_STATE_CLASS_NAME'] = self.state_class.replace('/', '.')
        artifacts['PREMIUM_FEATURE_STATE_ACTIVE_FIELD'] = self.active_field
        self.is_found = True
