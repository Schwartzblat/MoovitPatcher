import re
from stitch.artifactory_generator.SimpleArtifactoryFinder import SimpleArtifactoryFinder, CLASS_NAME_RE


class AppMapAdsLayer(SimpleArtifactoryFinder):
    """com.moovit.app.map.layers.MapAdsLayerManager's "sync the map ads layer" method.

    The manager owns one sponsored MapItemCollection and one no-argument void
    method that decides whether it should currently be on the map: it reads the
    map-ads feature flag plus the "is_ads_free_version" remote config flag and
    then either registers the collection on the MapFragment or removes it again.
    That method is the only place in the apk that registers this collection, so
    suppressing it keeps the sponsored map items off the map for good.

    Anchors:
      class  -- the instantiation of the manager's own Kotlin inner receiver,
                com/moovit/app/map/layers/MapAdsLayerManager$mapAdsBroadcastReceiver$1,
                whose source-derived name survived R8; only the outer class
                constructs it, which is why the "-><init>(" suffix is part of the
                anchor
      method -- the only ()V in the class, further pinned to the body that
                touches com/moovit/map/MapFragment and reads the
                "is_ads_free_version" flag
    """

    RECEIVER_ANCHOR = (
        'Lcom/moovit/app/map/layers/MapAdsLayerManager$mapAdsBroadcastReceiver$1;-><init>(')

    MAP_ADS_SYNC_RE = re.compile(
        r'\.method public final (?P<method_name>\w+)(?P<sig>\(\)V)'
        r'(?:(?!\.end method)[\s\S])*?Lcom/moovit/map/MapFragment;'
        r'(?:(?!\.end method)[\s\S])*?"is_ads_free_version"')

    def __init__(self, args):
        super().__init__(args)
        self.is_once = True
        self.is_found = False

    def class_filter(self, class_data: str) -> bool:
        return self.RECEIVER_ANCHOR in class_data

    def extract_artifacts(self, artifacts: dict, class_data: str) -> None:
        matches = list(self.MAP_ADS_SYNC_RE.finditer(class_data))
        if len(matches) != 1:
            return
        class_name = CLASS_NAME_RE.match(class_data)
        if class_name is None:
            return
        artifacts['APPAD_MAPADS_CLASS_NAME'] = class_name.groupdict().get('name').replace('/', '.')
        artifacts['APPAD_MAPADS_METHOD_NAME'] = matches[0].groupdict().get('method_name')
        artifacts['APPAD_MAPADS_METHOD_SIG'] = matches[0].groupdict().get('sig')
        self.is_found = True
