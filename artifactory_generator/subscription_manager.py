import re
from stitch.artifactory_generator.SimpleArtifactoryFinder import SimpleArtifactoryFinder, CLASS_NAME_RE


class SubscriptionManager(SimpleArtifactoryFinder):
    """Locates Moovit's synchronous "does the user own a subscription?" check.

    The holder persists the owned SKUs under the SharedPreferences key
    "subscribed_skus", and the check is a no-argument boolean that answers
    whether that set is non-empty. Up to 5.201.1 it lived in a subscriptions
    manager that ORed in a Boolean remote flag first; since 5.201.6 it is
    SubscriptionBridgeImpl's, which only reads the set.

    Anchors:
      class  -- the persisted preference key "subscribed_skus" (a request class
                names it too, but has no ()Z, so it never matches)
      method -- the only public final ()Z whose body asks the SKU collection
                isEmpty()
    """

    IS_SUBSCRIBED_RE = re.compile(
        r'\.method public final (?P<method_name>\w+)(?P<sig>\(\)Z)'
        r'(?:(?!\.end method)[\s\S])*?Ljava/util/Collection;->isEmpty\(\)Z')

    def __init__(self, args):
        super().__init__(args)
        self.is_once = True
        self.is_found = False

    def class_filter(self, class_data: str) -> bool:
        return '"subscribed_skus"' in class_data

    def extract_artifacts(self, artifacts: dict, class_data: str) -> None:
        matches = list(self.IS_SUBSCRIBED_RE.finditer(class_data))
        if len(matches) != 1:
            return
        artifacts['SUBSCRIPTION_MANAGER_CLASS_NAME'] = CLASS_NAME_RE.match(class_data).groupdict().get('name').replace(
            '/', '.')
        artifacts['SUBSCRIPTION_MANAGER_METHOD_NAME'] = matches[0].groupdict().get('method_name')
        artifacts['SUBSCRIPTION_MANAGER_METHOD_SIG'] = matches[0].groupdict().get('sig')
        self.is_found = True
