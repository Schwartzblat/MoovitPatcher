package com.smali_generator.patches;

import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import com.arthooks.ArtHooks;
import com.smali_generator.Hook;

import java.lang.reflect.Executable;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Reports every Moovit Plus subscription package as owned.
 *
 * Each premium feature -- ad free, AI search, trip on map, traffic on map, safe
 * ride, share ride, trip plan sort / advanced route / advanced time picker, trip
 * insights, itinerary insights, trip notifications, green ride, compare on map,
 * default tab -- has a subscription-package object holding one enum state,
 * INACTIVE, OFFER, PENDING_ACTIVATION or ACTIVE, in a LiveData. The feature gates
 * read that LiveData and grant access only on ACTIVE.
 *
 * Why this is needed on top of SubscriptionManager: the state is computed
 * asynchronously and starts out INACTIVE. It is only recalculated after the
 * CONFIGURATION app-data part has loaded and the package's coroutine has run, and
 * only while the process lifecycle is at least STARTED. Until then the feature
 * gate sees INACTIVE, which it treats as "not offered in this metro" and hides
 * the feature outright -- not even a paywall.
 *
 * Since 5.201.6 the gates read the LiveData directly (the old getter was
 * inlined), so two hooks keep it at ACTIVE:
 *   - the package constructor, which runs the original and then sets ACTIVE, so
 *     the state is ACTIVE from the moment the package exists;
 *   - the update method, the only path to the coroutine that writes the
 *     LiveData, which sets ACTIVE instead of computing a state.
 *
 * LiveData.setValue must run on the main thread, so a set from any other thread
 * is posted there. The ACTIVE constant, the LiveData field and its setter are
 * all resolved reflectively from names the finder captured, so no obfuscated
 * name is written down here.
 */
public class PremiumFeaturePackages implements Hook {
    private static final String PACKAGE = "{{PREMIUM_FEATURE_PACKAGE_CLASS_NAME}}";
    private static final String CTOR = PACKAGE + ".<init>{{PREMIUM_FEATURE_PACKAGE_CTOR_SIG}}";
    private static final String UPDATE = PACKAGE
            + ".{{PREMIUM_FEATURE_PACKAGE_UPDATE_METHOD_NAME}}{{PREMIUM_FEATURE_PACKAGE_UPDATE_METHOD_SIG}}";

    /** Published before either hook goes live. */
    private static volatile Object active_state = null;
    private static volatile Field state_field = null;
    private static volatile Method state_setter = null;

    private static final AtomicBoolean logged_first_set = new AtomicBoolean(false);

    static void construct(Object thiz, Object application, Object type) {
        construct_backup(thiz, application, type);
        set_active(thiz);
    }

    // static native, no body: ArtHooks points it at the original constructor.
    static native void construct_backup(Object thiz, Object application, Object type);

    static void update(Object thiz, String initiator) {
        set_active(thiz);
    }

    private static void set_active(Object subscription_package) {
        try {
            Object live_data = state_field.get(subscription_package);
            if (Looper.myLooper() == Looper.getMainLooper()) {
                set_on_main(live_data);
            } else {
                new Handler(Looper.getMainLooper()).post(() -> set_on_main(live_data));
            }
        } catch (Throwable t) {
            Log.e("PATCH", "PremiumFeaturePackages: cannot set ACTIVE: " + t);
        }
    }

    private static void set_on_main(Object live_data) {
        try {
            state_setter.invoke(live_data, active_state);
            if (!logged_first_set.getAndSet(true)) {
                Log.i("PATCH", "PremiumFeaturePackages: set {{PREMIUM_FEATURE_STATE_ACTIVE_FIELD}}");
            }
        } catch (Throwable t) {
            Log.e("PATCH", "PremiumFeaturePackages: cannot set ACTIVE: " + t);
        }
    }

    public void load() {
        try {
            if (!ArtHooks.is_available()) {
                Log.e("PATCH", "PremiumFeaturePackages: ArtHooks unavailable, " + PACKAGE + " NOT hooked");
                return;
            }

            Class<?> state_class = Class.forName("{{PREMIUM_FEATURE_STATE_CLASS_NAME}}");
            Field active_field = state_class.getDeclaredField("{{PREMIUM_FEATURE_STATE_ACTIVE_FIELD}}");
            active_field.setAccessible(true);
            Object active = active_field.get(null);
            if (active == null) {
                Log.e("PATCH", "PremiumFeaturePackages: active state constant is null on "
                        + "{{PREMIUM_FEATURE_STATE_CLASS_NAME}}, " + PACKAGE + " NOT hooked");
                return;
            }

            Class<?> package_class = Class.forName(PACKAGE);
            Field field = package_class.getDeclaredField("{{PREMIUM_FEATURE_PACKAGE_STATE_FIELD}}");
            field.setAccessible(true);
            // Searches superclasses: the setter is declared on a LiveData base class.
            Executable setter = ArtHooks.find_function(field.getType(),
                    "{{PREMIUM_FEATURE_PACKAGE_STATE_SETTER}}", "(Ljava/lang/Object;)V");
            if (!(setter instanceof Method)) {
                Log.e("PATCH", "PremiumFeaturePackages: LiveData setter not found on "
                        + field.getType().getName() + ", " + PACKAGE + " NOT hooked");
                return;
            }
            setter.setAccessible(true);

            Executable ctor = ArtHooks.find_function(package_class,
                    "<init>", "{{PREMIUM_FEATURE_PACKAGE_CTOR_SIG}}");
            Executable update = ArtHooks.find_function(package_class,
                    "{{PREMIUM_FEATURE_PACKAGE_UPDATE_METHOD_NAME}}", "{{PREMIUM_FEATURE_PACKAGE_UPDATE_METHOD_SIG}}");
            if (ctor == null || update == null) {
                Log.e("PATCH", "PremiumFeaturePackages: target not found: "
                        + (ctor == null ? CTOR : UPDATE));
                return;
            }

            // Publish what the replacements read before the hooks go live.
            active_state = active;
            state_field = field;
            state_setter = (Method) setter;

            Method update_replacement = PremiumFeaturePackages.class
                    .getDeclaredMethod("update", Object.class, String.class);
            if (ArtHooks.hook_function(update, update_replacement)) {
                Log.i("PATCH", "PremiumFeaturePackages: hooked " + UPDATE);
            } else {
                Log.e("PATCH", "PremiumFeaturePackages: hook_function refused " + UPDATE);
            }

            Method ctor_replacement = PremiumFeaturePackages.class
                    .getDeclaredMethod("construct", Object.class, Object.class, Object.class);
            Method ctor_backup = PremiumFeaturePackages.class
                    .getDeclaredMethod("construct_backup", Object.class, Object.class, Object.class);
            if (ArtHooks.hook_function(ctor, ctor_replacement, ctor_backup)) {
                Log.i("PATCH", "PremiumFeaturePackages: hooked " + CTOR);
            } else {
                Log.e("PATCH", "PremiumFeaturePackages: hook_function refused " + CTOR);
            }
        } catch (Throwable t) {
            Log.e("PATCH", "PremiumFeaturePackages: " + PACKAGE + ": " + t);
        }
    }

    public void unload() {
        Log.i("PATCH", "PremiumFeaturePackages: Patch unloaded");
    }
}
