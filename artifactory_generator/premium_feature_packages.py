import re

from stitch.artifactory_generator.SimpleArtifactoryFinder import SimpleArtifactoryFinder

# Rename-proof anchors. The string literals are a broadcast action, an
# analytics constant and log text, all load-bearing at runtime; the class path
# fragment is one of the com/moovit/** names that survived R8.
FOREGROUND_ACTION = '"com.moovit.app.action.foreground"'
STATE_ENUM_PATH = 'premium/packages/SubscriptionPackageState;'
ACTIVE_ANALYTICS_CONSTANT = '"package_state_active"'
UPDATE_LOG_TAG = '"SubscriptionPackage"'
UPDATE_LOG_TEXT = '", initiator="'

# Inside one method body; smali puts .line directives between instructions.
BODY = r'(?:(?!\.end method)[\s\S])*?'
LINES = r'\s+(?:\.line \d+\s+)*'


class PremiumFeaturePackages(SimpleArtifactoryFinder):
    """Locates the per-feature Moovit Plus entitlement state.

    Every premium feature (ad free, AI search, trip on map, traffic on map,
    safe ride, share ride, trip plan sort / advanced route / time picker, trip
    insights, ...) is a subscription-package object that holds one enum state,
    INACTIVE / OFFER / PENDING_ACTIVATION / ACTIVE, in a LiveData. The feature
    gates read that LiveData and grant access only when it holds ACTIVE.

    The constructor creates the LiveData holding INACTIVE. Its only writer is
    the coroutine SubscriptionPackage$updateStateAsync$2, launched by the
    package's update method (initiator String) -> void, which computes the
    state and sets it. Up to 5.201.1 a getter wrapped the read; 5.201.6 inlined
    it into the gates, so the LiveData itself is the target: the hook sets
    ACTIVE once the constructor has run, and the update method sets ACTIVE
    instead of computing a state.

    Three classes are inspected, in whatever order the smali walk reaches them:

      * the abstract subscription-package base class, recognised by the
        foreground broadcast action plus a reference to the state enum. It
        yields the constructor's signature, the field it stores the
        state-enum-initialised LiveData in, and the update method (the only
        public final (String) -> void, which checks the lifecycle is STARTED).
      * the update coroutine, recognised by its log text. It yields the field
        it writes and the LiveData method it writes with (setValue).
      * the state enum, recognised by the analytics constant of its active
        entry, which yields the field that holds that entry.

    Nothing fires until all three agree on the package class, the LiveData
    field and the state enum.
    """

    # The constructor must keep exactly two reference parameters: the hook's
    # replacement and backup are written for that arity.
    CTOR_RE = re.compile(
        r'\.method public constructor <init>(?P<sig>\((?:L[\w/$]+;){2}\)V)'
        + BODY
        + r'sget-object (?P<value>\w+), L(?P<state_class>[\w/$]+);->\w+:L(?P=state_class);'
        + LINES
        + r'invoke-direct \{(?P<live_data>\w+), (?P=value)\}, L[\w/$]+;-><init>\(Ljava/lang/Object;\)V'
        + LINES
        + r'iput-object (?P=live_data), p0, L[\w/$]+;->(?P<field>\w+):L[\w/$]+;')

    UPDATE_RE = re.compile(
        r'\.method public final (?P<method_name>\w+)(?P<sig>\(Ljava/lang/String;\)V)'
        + BODY
        + r'Landroidx/lifecycle/Lifecycle\$State;->STARTED')

    SETTER_RE = re.compile(
        r'iget-object (?P<reg>\w+), (?P=reg), L(?P<package_class>[\w/$]+);->(?P<field>\w+):L(?P<live_data>[\w/$]+);'
        + LINES
        + r'invoke-virtual \{(?P=reg), \w+\}, L(?P=live_data);->(?P<setter>\w+)\(Ljava/lang/Object;\)V')

    ACTIVE_STATE_RE = re.compile(
        ACTIVE_ANALYTICS_CONSTANT
        + BODY
        + r'sput-object \w+, L(?P<state_class>[\w/$]+);->(?P<active_field>\w+):L(?P=state_class);')

    def __init__(self, args):
        super().__init__(args)
        self.is_once = True
        self.is_found = False
        self.package = None   # from the base class
        self.writer = None    # from the update coroutine
        self.active = None    # from the state enum

    def class_filter(self, class_data: str) -> bool:
        if ACTIVE_ANALYTICS_CONSTANT in class_data:
            return True
        if UPDATE_LOG_TAG in class_data and UPDATE_LOG_TEXT in class_data:
            return True
        return FOREGROUND_ACTION in class_data and STATE_ENUM_PATH in class_data

    def extract_artifacts(self, artifacts: dict, class_data: str) -> None:
        if ACTIVE_ANALYTICS_CONSTANT in class_data:
            self._extract_active_state(class_data)
        elif UPDATE_LOG_TAG in class_data and UPDATE_LOG_TEXT in class_data:
            self._extract_writer(class_data)
        else:
            self._extract_package(class_data)
        self._emit(artifacts)

    def _extract_package(self, class_data: str) -> None:
        class_match = re.match(r'\.class .*?L(?P<name>[\w/$]+);', class_data)
        ctors = list(self.CTOR_RE.finditer(class_data))
        updates = list(self.UPDATE_RE.finditer(class_data))
        if class_match is None or len(ctors) != 1 or len(updates) != 1:
            return
        self.package = {
            'class': class_match.group('name'),
            'ctor_sig': ctors[0].group('sig'),
            'field': ctors[0].group('field'),
            'state_class': ctors[0].group('state_class'),
            'update_name': updates[0].group('method_name'),
            'update_sig': updates[0].group('sig'),
        }

    def _extract_writer(self, class_data: str) -> None:
        matches = list(self.SETTER_RE.finditer(class_data))
        if len(matches) != 1:
            return
        self.writer = matches[0].groupdict()

    def _extract_active_state(self, class_data: str) -> None:
        matches = list(self.ACTIVE_STATE_RE.finditer(class_data))
        if len(matches) != 1:
            return
        self.active = matches[0].groupdict()

    def _emit(self, artifacts: dict) -> None:
        if None in (self.package, self.writer, self.active):
            return
        package, writer, active = self.package, self.writer, self.active
        # All three must describe the same objects, otherwise the shape changed.
        if (writer['package_class'] != package['class'] or writer['field'] != package['field']
                or active['state_class'] != package['state_class']):
            return
        artifacts['PREMIUM_FEATURE_PACKAGE_CLASS_NAME'] = package['class'].replace('/', '.')
        artifacts['PREMIUM_FEATURE_PACKAGE_CTOR_SIG'] = package['ctor_sig']
        artifacts['PREMIUM_FEATURE_PACKAGE_UPDATE_METHOD_NAME'] = package['update_name']
        artifacts['PREMIUM_FEATURE_PACKAGE_UPDATE_METHOD_SIG'] = package['update_sig']
        artifacts['PREMIUM_FEATURE_PACKAGE_STATE_FIELD'] = package['field']
        artifacts['PREMIUM_FEATURE_PACKAGE_STATE_SETTER'] = writer['setter']
        artifacts['PREMIUM_FEATURE_STATE_CLASS_NAME'] = active['state_class'].replace('/', '.')
        artifacts['PREMIUM_FEATURE_STATE_ACTIVE_FIELD'] = active['active_field']
        self.is_found = True
