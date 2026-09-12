package com.smali_generator.patches;

import android.util.Log;

import com.arthooks.ArtHooks;
import com.smali_generator.Hook;

import java.lang.reflect.Executable;
import java.lang.reflect.Field;
import java.lang.reflect.Method;

/**
 * Reports every Moovit Plus subscription package as owned.
 *
 * Each premium feature -- ad free, AI search, trip on map, traffic on map, safe
 * ride, share ride, trip plan sort / advanced route / advanced time picker, trip
 * insights, itinerary insights, trip notifications, green ride, compare on map,
 * default tab -- has a subscription-package object that caches one enum state:
 * INACTIVE, OFFER, PENDING_ACTIVATION or ACTIVE. The target is the cached-state
 * getter, i.e. the entitlement value every gate reads.
 *
 * Why this is needed on top of SubscriptionManager: the cached value is computed
 * asynchronously and starts out INACTIVE. It is only recalculated after the
 * CONFIGURATION app-data part has loaded and the package's coroutine has run, and
 * only while the process lifecycle is at least STARTED. Until then the feature
 * gate sees INACTIVE, which it treats as "not offered in this metro" and hides
 * the feature outright -- not even a paywall. Answering with the ACTIVE constant
 * makes the entitlement unconditional and immediate, and lets the app's own gate
 * logic grant access instead of the gate having to be rewritten downstream.
 *
 * The ACTIVE constant is resolved reflectively from the field name the finder
 * captured, so no enum name is written down here.
 *
 * The target is an INSTANCE method, so the replacement is static with a leading
 * Object thiz. It returns Object; the enum instance handed back is of the exact
 * type the caller expects.
 */
public class PremiumFeaturePackages implements Hook {
    private static final String TARGET =
            "{{PREMIUM_FEATURE_PACKAGE_CLASS_NAME}}.{{PREMIUM_FEATURE_PACKAGE_METHOD_NAME}}{{PREMIUM_FEATURE_PACKAGE_METHOD_SIG}}";

    /** The "owned" enum constant, published before the hook goes live. */
    private static volatile Object active_state = null;

    static Object get_state(Object thiz) {
        Object state = active_state;
        if (state == null) {
            // Cannot happen: load() refuses to hook unless the constant resolved.
            Log.e("PATCH", "PremiumFeaturePackages: no active state for " + TARGET);
        }
        return state;
    }

    public void load() {
        try {
            if (!ArtHooks.is_available()) {
                Log.e("PATCH", "PremiumFeaturePackages: ArtHooks unavailable, " + TARGET + " NOT hooked");
                return;
            }

            Class<?> state_class = Class.forName("{{PREMIUM_FEATURE_STATE_CLASS_NAME}}");
            Field active_field = state_class
                    .getDeclaredField("{{PREMIUM_FEATURE_STATE_ACTIVE_FIELD}}");
            active_field.setAccessible(true);
            Object active = active_field.get(null);
            if (active == null) {
                Log.e("PATCH", "PremiumFeaturePackages: active state constant is null on "
                        + "{{PREMIUM_FEATURE_STATE_CLASS_NAME}}, " + TARGET + " NOT hooked");
                return;
            }

            Class<?> package_class = Class.forName("{{PREMIUM_FEATURE_PACKAGE_CLASS_NAME}}");
            Executable original = ArtHooks.find_function(package_class,
                    "{{PREMIUM_FEATURE_PACKAGE_METHOD_NAME}}", "{{PREMIUM_FEATURE_PACKAGE_METHOD_SIG}}");
            if (original == null) {
                Log.e("PATCH", "PremiumFeaturePackages: target not found: " + TARGET);
                return;
            }

            Method replacement = PremiumFeaturePackages.class
                    .getDeclaredMethod("get_state", Object.class);

            // Publish the state the replacement reads before the hook goes live.
            active_state = active;

            if (ArtHooks.hook_function(original, replacement)) {
                Log.i("PATCH", "PremiumFeaturePackages: hooked " + TARGET
                        + " -> {{PREMIUM_FEATURE_STATE_ACTIVE_FIELD}}");
            } else {
                active_state = null;
                Log.e("PATCH", "PremiumFeaturePackages: hook_function refused " + TARGET);
            }
        } catch (Exception e) {
            Log.e("PATCH", "PremiumFeaturePackages: " + TARGET + ": " + e);
        }
    }

    public void unload() {
        Log.i("PATCH", "PremiumFeaturePackages: Patch unloaded");
    }
}
