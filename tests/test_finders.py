"""Finders against hand-written smali shaped like real Moovit releases.

Each fixture is a minimal class with the shape a finder anchors on, in the
form the old releases (5.199 / 5.201.1) and the new ones (5.201.6 - 5.205)
write it. Obfuscated names differ between fixtures on purpose: they are
outputs of the finders, never inputs.

The smali goes through stitch's own generate_artifactory, so these tests walk
the files exactly as a real patch does.
"""
from pathlib import Path

from stitch.artifactory_generator.generate_artifactory import generate_artifactory
from stitch.common import EXTRACTED_PATH

from artifactory_generator.app_ad_unit_id_resolver import AppAdUnitIdResolver
from artifactory_generator.app_ad_view_show import AppAdViewShow
from artifactory_generator.app_map_ads_layer import AppMapAdsLayer
from artifactory_generator.block_paywall import BlockPaywall
from artifactory_generator.is_subscribed_stream import IsSubscribedStream
from artifactory_generator.premium_feature_packages import PremiumFeaturePackages
from artifactory_generator.subscription_manager import SubscriptionManager


def find(tmp_path: Path, finder, classes: dict) -> dict:
    """Writes {class path: smali} under an extracted tree and runs one finder."""
    for name, smali in classes.items():
        path = tmp_path / EXTRACTED_PATH / 'smali' / (name + '.smali')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(smali, encoding='utf8')
    return generate_artifactory(tmp_path, [finder])


# --- SubscriptionManager ----------------------------------------------------

OLD_SUBSCRIPTION_MANAGER = '''.class public final Lq1z;
.super Ljava/lang/Object;

.method public constructor <init>(Landroid/content/Context;)V
    .locals 3
    const-string v2, "subscribed_skus"
    return-void
.end method

.method public final a()Ljava/util/Set;
    .locals 3
    const-string v0, "subscriptions_manager"
    return-object p0
.end method

.method public final b()Z
    .locals 2
    .line 1
    sget-object v0, Lri0;->a:Lw2f;
    iget-object v0, v0, Lxde;->b:Ljava/lang/Object;
    check-cast v0, Ljava/lang/Boolean;
    invoke-virtual {v0}, Ljava/lang/Boolean;->booleanValue()Z
    move-result v0
    const/4 v1, 0x1
    if-eqz v0, :cond_0
    return v1
    :cond_0
    invoke-virtual {p0}, Lq1z;->a()Ljava/util/Set;
    move-result-object p0
    check-cast p0, Ljava/util/Collection;
    invoke-interface {p0}, Ljava/util/Collection;->isEmpty()Z
    move-result p0
    xor-int/2addr p0, v1
    return p0
.end method
'''

# 5.201.6+: the check moved into SubscriptionBridgeImpl, which has no Boolean
# remote flag any more, only the persisted SKU set.
SUBSCRIPTION_BRIDGE = '''.class public final Lcom/moovit/app/bridge/e;
.super Ljava/lang/Object;

.method public constructor <init>(Landroid/content/Context;Lta4;Lcom/moovit/lib/subscription/entitlements/a;)V
    .locals 5
    const-string v0, "subscriptions_manager"
    const-string v4, "subscribed_skus"
    invoke-static {p1}, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;
    const-string v2, "SubscriptionBridgeImpl"
    return-void
.end method

.method public final a()Z
    .locals 1
    .line 1
    iget-object v0, p0, Lcom/moovit/app/bridge/e;->c:Lceh;
    iget-object p0, p0, Lcom/moovit/app/bridge/e;->b:Landroid/content/SharedPreferences;
    invoke-virtual {v0, p0}, Lceh;->l(Landroid/content/SharedPreferences;)Ljava/util/Set;
    move-result-object p0
    check-cast p0, Ljava/util/Collection;
    invoke-interface {p0}, Ljava/util/Collection;->isEmpty()Z
    move-result p0
    xor-int/lit8 p0, p0, 0x1
    return p0
.end method
'''

# A request class that also names the preference, with no ()Z at all.
SUBSCRIBED_SKUS_REQUEST = '''.class public final Lctk;
.super Ljava/lang/Object;

.method public final a(Lcom/moovit/request/RequestContext;)V
    .locals 4
    const-string v3, "subscribed_skus"
    return-void
.end method
'''


def test_subscription_manager_finds_the_old_manager(tmp_path):
    artifacts = find(tmp_path, SubscriptionManager(None), {'q1z': OLD_SUBSCRIPTION_MANAGER})
    assert artifacts == {
        'SUBSCRIPTION_MANAGER_CLASS_NAME': 'q1z',
        'SUBSCRIPTION_MANAGER_METHOD_NAME': 'b',
        'SUBSCRIPTION_MANAGER_METHOD_SIG': '()Z',
    }


def test_subscription_manager_finds_the_subscription_bridge(tmp_path):
    artifacts = find(tmp_path, SubscriptionManager(None), {
        'ctk': SUBSCRIBED_SKUS_REQUEST,
        'com/moovit/app/bridge/e': SUBSCRIPTION_BRIDGE,
    })
    assert artifacts == {
        'SUBSCRIPTION_MANAGER_CLASS_NAME': 'com.moovit.app.bridge.e',
        'SUBSCRIPTION_MANAGER_METHOD_NAME': 'a',
        'SUBSCRIPTION_MANAGER_METHOD_SIG': '()Z',
    }


# --- IsSubscribedStream -----------------------------------------------------

STREAM_CONTINUATION = 'com/moovit/domain/subscription/IsSubscribedStreamUseCase$invoke$$inlined$map$1$2$1'

# 5.201.6+: the collector inside IsSubscribedStreamUseCase that maps the
# entitlements to "is the list non-empty" and emits that downstream.
IS_SUBSCRIBED_COLLECTOR = f'''.class public final Lcom/moovit/domain/subscription/b;
.super Ljava/lang/Object;

# interfaces
.implements Lv97;

.field public final synthetic a:Lv97;

.method public final emit(Ljava/lang/Object;Lx04;)Ljava/lang/Object;
    .locals 6
    instance-of v0, p2, L{STREAM_CONTINUATION};
    new-instance v0, L{STREAM_CONTINUATION};
    invoke-static {{p2}}, Lkotlin/b;->b(Ljava/lang/Object;)V
    .line 3
    check-cast p1, Lu96;
    .line 4
    iget-object p1, p1, Lu96;->a:Ljava/util/List;
    .line 5
    invoke-interface {{p1}}, Ljava/util/Collection;->isEmpty()Z
    move-result p1
    xor-int/2addr p1, v3
    invoke-static {{p1}}, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;
    move-result-object p1
    iget-object p0, p0, Lcom/moovit/domain/subscription/b;->a:Lv97;
    invoke-interface {{p0, p1, v0}}, Lv97;->emit(Ljava/lang/Object;Lx04;)Ljava/lang/Object;
    move-result-object p0
    return-object p0
.end method
'''

# The continuation class itself names the anchor but maps nothing.
IS_SUBSCRIBED_CONTINUATION = f'''.class public final L{STREAM_CONTINUATION};
.super Lkotlin/coroutines/jvm/internal/ContinuationImpl;

.field public label:I

.method public final invokeSuspend(Ljava/lang/Object;)Ljava/lang/Object;
    .locals 1
    iput-object p1, p0, L{STREAM_CONTINUATION};->result:Ljava/lang/Object;
    return-object p0
.end method
'''

# SyncPurchasesUseCase makes the same isEmpty() check, without the anchor.
SYNC_PURCHASES = '''.class public final Lcom/moovit/domain/subscription/d;
.super Ljava/lang/Object;

.method public final a(Lkotlin/coroutines/jvm/internal/ContinuationImpl;)Ljava/lang/Object;
    .locals 4
    check-cast p1, Lu96;
    iget-object p0, p1, Lu96;->a:Ljava/util/List;
    invoke-interface {p0}, Ljava/util/Collection;->isEmpty()Z
    move-result p0
    return-object p0
.end method
'''


def test_is_subscribed_stream_finds_the_entitlements_mapper(tmp_path):
    artifacts = find(tmp_path, IsSubscribedStream(None), {
        STREAM_CONTINUATION: IS_SUBSCRIBED_CONTINUATION,
        'com/moovit/domain/subscription/d': SYNC_PURCHASES,
        'com/moovit/domain/subscription/b': IS_SUBSCRIBED_COLLECTOR,
    })
    assert artifacts == {
        'IS_SUBSCRIBED_STREAM_CLASS_NAME': 'com.moovit.domain.subscription.b',
        'IS_SUBSCRIBED_STREAM_METHOD_NAME': 'emit',
        'IS_SUBSCRIBED_STREAM_METHOD_SIG': '(Ljava/lang/Object;Lx04;)Ljava/lang/Object;',
        'IS_SUBSCRIBED_STREAM_VALUE_CLASS_NAME': 'u96',
    }


def test_is_subscribed_stream_ignores_the_same_check_elsewhere(tmp_path):
    artifacts = find(tmp_path, IsSubscribedStream(None), {
        'com/moovit/domain/subscription/d': SYNC_PURCHASES,
    })
    assert artifacts == {}


# --- PremiumFeaturePackages -------------------------------------------------

PKG = 'com/moovit/app/subscription/premium/packages'
STATE = PKG + '/SubscriptionPackageState'


def package_base(live_data: str, update_name: str, getter: bool) -> str:
    """The abstract SubscriptionPackage. Old releases still had the b() getter."""
    getter_smali = f'''
.method public final b()L{STATE};
    .locals 0
    iget-object p0, p0, L{PKG}/a;->f:L{live_data};
    invoke-virtual {{p0}}, Lhd9;->d()Ljava/lang/Object;
    move-result-object p0
    check-cast p0, L{STATE};
    if-nez p0, :cond_0
    sget-object p0, L{STATE};->INACTIVE:L{STATE};
    :cond_0
    return-object p0
.end method
''' if getter else ''
    return f'''.class public abstract L{PKG}/a;
.super Ljava/lang/Object;

.field public final f:L{live_data};

.method public constructor <init>(Lcom/moovit/MoovitApplication;L{PKG}/SubscriptionPackageType;)V
    .locals 5
    const-string v0, "CONFIGURATION"
    new-instance v3, L{live_data};
    .line 12
    sget-object v4, L{STATE};->INACTIVE:L{STATE};
    .line 13
    invoke-direct {{v3, v4}}, Llsa;-><init>(Ljava/lang/Object;)V
    .line 14
    iput-object v3, p0, L{PKG}/a;->f:L{live_data};
    new-instance v3, Landroid/content/IntentFilter;
    const-string v4, "com.moovit.app.action.foreground"
    return-void
.end method

.method public abstract a(Lkotlin/coroutines/jvm/internal/ContinuationImpl;)Ljava/lang/Enum;
.end method
{getter_smali}
.method public final {update_name}(Ljava/lang/String;)V
    .locals 3
    sget-object v0, Lmaf;->i:Lmaf;
    sget-object v1, Landroidx/lifecycle/Lifecycle$State;->STARTED:Landroidx/lifecycle/Lifecycle$State;
    invoke-static {{v0, v1}}, Lj4i;->C(Landroidx/lifecycle/LifecycleOwner;Landroidx/lifecycle/Lifecycle$State;)Z
    return-void
.end method
'''


def update_state_async(live_data: str, field: str = 'f') -> str:
    """SubscriptionPackage$updateStateAsync$2, the only writer of the state LiveData."""
    return f'''.class final L{PKG}/SubscriptionPackage$updateStateAsync$2;
.super Lkotlin/coroutines/jvm/internal/SuspendLambda;

.method public final invokeSuspend(Ljava/lang/Object;)Ljava/lang/Object;
    .locals 5
    invoke-virtual {{p1, p0}}, L{PKG}/a;->a(Lkotlin/coroutines/jvm/internal/ContinuationImpl;)Ljava/lang/Enum;
    const-string v4, "type="
    const-string v0, ", initiator="
    const-string v0, ", state="
    const-string v2, "SubscriptionPackage"
    invoke-static {{v2, v0, v1}}, Lnfo;->s(Ljava/lang/String;Ljava/lang/String;[Ljava/lang/Object;)V
    iget-object p0, p0, L{PKG}/SubscriptionPackage$updateStateAsync$2;->this$0:L{PKG}/a;
    .line 40
    iget-object p0, p0, L{PKG}/a;->{field}:L{live_data};
    .line 41
    invoke-virtual {{p0, p1}}, L{live_data};->k(Ljava/lang/Object;)V
    sget-object p0, Lkotlin/Unit;->a:Lkotlin/Unit;
    return-object p0
.end method
'''


STATE_ENUM = f'''.class public final enum L{STATE};
.super Ljava/lang/Enum;

.method static constructor <clinit>()V
    .locals 4
    const-string v2, "package_state_offer"
    sput-object v0, L{STATE};->OFFER:L{STATE};
    const-string v2, "package_state_active"
    invoke-direct {{v0, v1, v3, v2}}, L{STATE};-><init>(Ljava/lang/String;ILjava/lang/String;)V
    sput-object v0, L{STATE};->ACTIVE:L{STATE};
    return-void
.end method
'''


def premium_classes(live_data: str, update_name: str, getter: bool, setter_field: str = 'f') -> dict:
    return {
        PKG + '/a': package_base(live_data, update_name, getter),
        PKG + '/SubscriptionPackage$updateStateAsync$2': update_state_async(live_data, setter_field),
        STATE: STATE_ENUM,
    }


def expected_premium(live_data_setter: str, update_name: str) -> dict:
    return {
        'PREMIUM_FEATURE_PACKAGE_CLASS_NAME': 'com.moovit.app.subscription.premium.packages.a',
        'PREMIUM_FEATURE_PACKAGE_CTOR_SIG':
            '(Lcom/moovit/MoovitApplication;Lcom/moovit/app/subscription/premium/packages/SubscriptionPackageType;)V',
        'PREMIUM_FEATURE_PACKAGE_UPDATE_METHOD_NAME': update_name,
        'PREMIUM_FEATURE_PACKAGE_UPDATE_METHOD_SIG': '(Ljava/lang/String;)V',
        'PREMIUM_FEATURE_PACKAGE_STATE_FIELD': 'f',
        'PREMIUM_FEATURE_PACKAGE_STATE_SETTER': live_data_setter,
        'PREMIUM_FEATURE_STATE_CLASS_NAME': 'com.moovit.app.subscription.premium.packages.SubscriptionPackageState',
        'PREMIUM_FEATURE_STATE_ACTIVE_FIELD': 'ACTIVE',
    }


def test_premium_feature_packages_without_the_state_getter(tmp_path):
    # 5.201.6+: the getter was inlined into its callers
    artifacts = find(tmp_path, PremiumFeaturePackages(None), premium_classes('v7d', 'b', getter=False))
    assert artifacts == expected_premium('k', 'b')


def test_premium_feature_packages_with_the_old_state_getter(tmp_path):
    artifacts = find(tmp_path, PremiumFeaturePackages(None), premium_classes('rlb', 'd', getter=True))
    assert artifacts == expected_premium('k', 'd')


def test_premium_feature_packages_needs_the_writer_to_set_the_same_field(tmp_path):
    artifacts = find(tmp_path, PremiumFeaturePackages(None),
                     premium_classes('v7d', 'b', getter=False, setter_field='g'))
    assert artifacts == {}


# --- BlockPaywall -----------------------------------------------------------

def block_paywall_holder(activity: str) -> str:
    return f'''.class public final Lmj1;
.super Ljava/lang/Object;

.method public static final a(L{activity};)Z
    .locals 3
    const-string v0, "block_paywall"
    const-string v1, "user_acquisition"
    check-cast v0, Ljava/lang/Boolean;
    invoke-virtual {{v0}}, Ljava/lang/Boolean;->booleanValue()Z
    move-result v0
    return v0
.end method
'''


def test_block_paywall_with_a_moovit_activity(tmp_path):
    artifacts = find(tmp_path, BlockPaywall(None), {'mj1': block_paywall_holder('com/moovit/MoovitActivity')})
    assert artifacts['PAYWALL_BLOCK_METHOD_SIG'] == '(Lcom/moovit/MoovitActivity;)Z'


def test_block_paywall_with_a_moovit_component_activity(tmp_path):
    # 5.201.1
    artifacts = find(tmp_path, BlockPaywall(None),
                     {'mj1': block_paywall_holder('com/moovit/core/components/MoovitComponentActivity')})
    assert artifacts == {
        'PAYWALL_BLOCK_CLASS_NAME': 'mj1',
        'PAYWALL_BLOCK_METHOD_NAME': 'a',
        'PAYWALL_BLOCK_METHOD_SIG': '(Lcom/moovit/core/components/MoovitComponentActivity;)Z',
    }


# --- AppAdUnitIdResolver ----------------------------------------------------

OLD_ADS_MANAGER = '''.class public final Lws9;
.super Ljava/lang/Object;

.method public final f(Lcom/moovit/app/ads/AdSource;)Ljava/lang/String;
    .locals 2
    const-string v0, "is_ads_free_version"
    const-string v1, "is_interstitial_ads_free_version"
    const-string p0, ""
    return-object p0
.end method

.method public final g(Lcom/moovit/app/ads/AdSource;)Ljava/lang/String;
    .locals 1
    invoke-virtual {p0, p1}, Lws9;->f(Lcom/moovit/app/ads/AdSource;)Ljava/lang/String;
    move-result-object p0
    return-object p0
.end method
'''

# 5.201.1+: "is_ads_free_version" moved into its own ()Z, which the resolver calls
NEW_ADS_MANAGER = '''.class public final Lloc;
.super Ljava/lang/Object;

.method public final g(Lcom/moovit/app/ads/AdSource;)Ljava/lang/String;
    .locals 2
    invoke-virtual {p0}, Lloc;->q()Z
    move-result v0
    const-string v1, "is_interstitial_ads_free_version"
    const-string p1, "na"
    const-string p0, ""
    return-object p0
.end method

.method public final h(Lcom/moovit/app/ads/AdSource;)Ljava/lang/String;
    .locals 1
    invoke-virtual {p0, p1}, Lloc;->g(Lcom/moovit/app/ads/AdSource;)Ljava/lang/String;
    move-result-object p0
    return-object p0
.end method

.method public final q()Z
    .locals 1
    const-string v0, "is_ads_free_version"
    const/4 p0, 0x1
    return p0
.end method

.method public final x(Lcom/moovit/core/components/MoovitComponentActivity;Lcom/moovit/app/ads/AdSource;)V
    .locals 15
    const-string v14, "is_interstitial_ads_free_version"
    return-void
.end method
'''


def test_ad_unit_id_resolver_reading_the_ads_free_flag_itself(tmp_path):
    artifacts = find(tmp_path, AppAdUnitIdResolver(None), {'ws9': OLD_ADS_MANAGER})
    assert artifacts['APPAD_ADUNIT_METHOD_NAME'] == 'f'


def test_ad_unit_id_resolver_calling_out_for_the_ads_free_flag(tmp_path):
    artifacts = find(tmp_path, AppAdUnitIdResolver(None), {'loc': NEW_ADS_MANAGER})
    assert artifacts == {
        'APPAD_ADUNIT_CLASS_NAME': 'loc',
        'APPAD_ADUNIT_METHOD_NAME': 'g',
        'APPAD_ADUNIT_METHOD_SIG': '(Lcom/moovit/app/ads/AdSource;)Ljava/lang/String;',
    }


# --- AppAdViewShow ----------------------------------------------------------

def moovit_ad_view(activity: str) -> str:
    return f'''.class public Lcom/moovit/app/ads/MoovitAdView;
.super Landroidx/constraintlayout/widget/ConstraintLayout;

.method public final onAttachedToWindow()V
    .locals 0
    return-void
.end method

.method public final v(Lcom/moovit/MoovitApplication;L{activity};Lcom/moovit/app/ads/AdSource;Ljava/lang/String;)V
    .locals 8
    return-void
.end method

.method public final w()V
    .locals 0
    return-void
.end method
'''


def test_ad_view_show_with_a_moovit_activity(tmp_path):
    artifacts = find(tmp_path, AppAdViewShow(None),
                     {'com/moovit/app/ads/MoovitAdView': moovit_ad_view('com/moovit/MoovitBaseComponentActivity')})
    assert artifacts['APPAD_VIEW_SHOW_METHOD_NAME'] == 'v'


def test_ad_view_show_with_an_androidx_activity(tmp_path):
    # 5.201.1+
    artifacts = find(tmp_path, AppAdViewShow(None),
                     {'com/moovit/app/ads/MoovitAdView': moovit_ad_view('androidx/activity/ComponentActivity')})
    assert artifacts == {
        'APPAD_VIEW_SHOW_CLASS_NAME': 'com.moovit.app.ads.MoovitAdView',
        'APPAD_VIEW_SHOW_METHOD_NAME': 'v',
        'APPAD_VIEW_SHOW_METHOD_SIG': '(Lcom/moovit/MoovitApplication;Landroidx/activity/ComponentActivity;'
                                      'Lcom/moovit/app/ads/AdSource;Ljava/lang/String;)V',
    }


# --- AppMapAdsLayer ---------------------------------------------------------

def map_ads_layer_manager(ads_free_check: str) -> str:
    return f'''.class public final Lvbb;
.super Ljava/lang/Object;

.method public constructor <init>(Landroid/content/Context;Luq3;Lcom/moovit/map/MapFragment;)V
    .locals 2
    new-instance v0, Lcom/moovit/app/map/layers/MapAdsLayerManager$mapAdsBroadcastReceiver$1;
    invoke-direct {{v0, p0}}, Lcom/moovit/app/map/layers/MapAdsLayerManager$mapAdsBroadcastReceiver$1;-><init>(Lvbb;)V
    return-void
.end method

.method public final a()V
    .locals 6
    iget-object v0, p0, Lvbb;->b:Lcom/moovit/map/MapFragment;
    invoke-virtual {{v0}}, Lcom/moovit/map/MapFragment;->T1()Z
{ads_free_check}
    return-void
.end method

.method public final onStart(Landroidx/lifecycle/LifecycleOwner;)V
    .locals 2
    iget-object p1, p0, Lvbb;->b:Lcom/moovit/map/MapFragment;
    return-void
.end method
'''


def test_map_ads_layer_reading_the_ads_free_flag_itself(tmp_path):
    artifacts = find(tmp_path, AppMapAdsLayer(None),
                     {'vbb': map_ads_layer_manager('    const-string v1, "is_ads_free_version"')})
    assert artifacts['APPAD_MAPADS_METHOD_NAME'] == 'a'


def test_map_ads_layer_calling_out_for_the_ads_free_flag(tmp_path):
    # 5.201.1+
    artifacts = find(tmp_path, AppMapAdsLayer(None),
                     {'vbb': map_ads_layer_manager('    invoke-virtual {v1}, Lloc;->q()Z')})
    assert artifacts == {
        'APPAD_MAPADS_CLASS_NAME': 'vbb',
        'APPAD_MAPADS_METHOD_NAME': 'a',
        'APPAD_MAPADS_METHOD_SIG': '()V',
    }
