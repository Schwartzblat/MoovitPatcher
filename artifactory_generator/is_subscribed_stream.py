import re

from stitch.artifactory_generator.SimpleArtifactoryFinder import SimpleArtifactoryFinder, CLASS_NAME_RE

# The Kotlin continuation of the map{} inside IsSubscribedStreamUseCase.invoke.
# R8 renamed the use case itself, but not this source-derived inner name.
STREAM_ANCHOR = 'IsSubscribedStreamUseCase$invoke$$inlined$map$'

# Inside one method body; smali puts .line directives between instructions.
BODY = r'(?:(?!\.end method)[\s\S])*?'
LINES = r'\s+(?:\.line \d+\s+)*'


class IsSubscribedStream(SimpleArtifactoryFinder):
    """Locates the "is subscribed" stream built on Moovit's entitlements.

    Since 5.201.6 the subscription library publishes the owned entitlements as
    a stream of one wrapper object holding a List. IsSubscribedStreamUseCase
    maps it to "the list is non-empty", and the newer screens observe that
    Boolean instead of asking SubscriptionBridgeImpl: the "Remove ads with
    Moovit+" promo cell, the Moovit+ tab and one more view model. The mapping
    is the emit method of the use case's FlowCollector, which casts the value
    to the wrapper, reads its List and asks isEmpty().

    The hook hands that method a wrapper holding a non-empty list, so the
    stream says subscribed. Older releases have no such stream; there this
    finder never fires and the hook logs that it is absent.

    Anchors:
      class  -- a reference to the use case's map continuation (see
                STREAM_ANCHOR); the continuation class itself names it too but
                maps nothing
      method -- the only public final (Object, Continuation) -> Object whose
                body casts its value, reads a List field of it and asks
                isEmpty(); it also yields the wrapper class
    """

    EMIT_RE = re.compile(
        r'\.method public final (?P<method_name>\w+)(?P<sig>\(Ljava/lang/Object;L[\w/$]+;\)Ljava/lang/Object;)'
        + BODY
        + r'check-cast (?P<reg>\w+), L(?P<value_class>[\w/$]+);'
        + LINES
        + r'iget-object (?P<list>\w+), (?P=reg), L(?P=value_class);->\w+:Ljava/util/List;'
        + LINES
        + r'invoke-interface \{(?P=list)\}, Ljava/util/Collection;->isEmpty\(\)Z')

    def __init__(self, args):
        super().__init__(args)
        self.is_once = True
        self.is_found = False

    def class_filter(self, class_data: str) -> bool:
        return STREAM_ANCHOR in class_data

    def extract_artifacts(self, artifacts: dict, class_data: str) -> None:
        matches = list(self.EMIT_RE.finditer(class_data))
        if len(matches) != 1:
            return
        class_match = CLASS_NAME_RE.match(class_data)
        if class_match is None:
            return
        groups = matches[0].groupdict()
        artifacts['IS_SUBSCRIBED_STREAM_CLASS_NAME'] = class_match.group('name').replace('/', '.')
        artifacts['IS_SUBSCRIBED_STREAM_METHOD_NAME'] = groups['method_name']
        artifacts['IS_SUBSCRIBED_STREAM_METHOD_SIG'] = groups['sig']
        artifacts['IS_SUBSCRIBED_STREAM_VALUE_CLASS_NAME'] = groups['value_class'].replace('/', '.')
        self.is_found = True
