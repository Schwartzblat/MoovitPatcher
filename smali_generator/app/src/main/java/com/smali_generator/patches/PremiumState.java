package com.smali_generator.patches;

import android.util.Log;

import com.arthooks.ArtHooks;
import com.smali_generator.Hook;

import java.lang.reflect.Executable;
import java.lang.reflect.Method;

/**
 * Forces Moovit's top-level "is Moovit Premium active" answer to true.
 *
 * The target is the app's synchronous premium predicate. Its body is
 *
 *     subscriptionManager.isSubscribed() &amp;&amp; remoteConfig.getBoolean("is_moovit_premium_enabled")
 *
 * so it carries a second gate on top of the subscription state already handled by
 * SubscriptionManager: a server-side kill switch that turns Moovit Premium off
 * wholesale (it is also reported as the "premium_test" A/B variable). While that
 * flag is off the app behaves as non-premium no matter what the subscription
 * check says.
 *
 * Everything that asks "is this a premium user" the cheap synchronous way reads
 * this method: the premium theme overlay applied by the app's activities, the
 * premium dashboard artwork, and the initial value of the injected isPremium
 * state that the Compose UI collects.
 *
 * Polarity: true means premium is active, so the replacement returns true.
 *
 * The target is a STATIC method, so the replacement takes no leading thiz; its
 * single parameter is the android.content.Context argument.
 */
public class PremiumState implements Hook {
    private static final String TARGET =
            "{{PREMIUM_STATE_CLASS_NAME}}.{{PREMIUM_STATE_METHOD_NAME}}{{PREMIUM_STATE_METHOD_SIG}}";

    static boolean is_premium_active(Object context) {
        return true;
    }

    public void load() {
        try {
            if (!ArtHooks.is_available()) {
                Log.e("PATCH", "PremiumState: ArtHooks unavailable, " + TARGET + " NOT hooked");
                return;
            }
            Class<?> cls = Class.forName("{{PREMIUM_STATE_CLASS_NAME}}");
            Executable original = ArtHooks.find_function(cls,
                    "{{PREMIUM_STATE_METHOD_NAME}}", "{{PREMIUM_STATE_METHOD_SIG}}");
            if (original == null) {
                Log.e("PATCH", "PremiumState: target not found: " + TARGET);
                return;
            }
            Method replacement = PremiumState.class
                    .getDeclaredMethod("is_premium_active", Object.class);
            if (ArtHooks.hook_function(original, replacement)) {
                Log.i("PATCH", "PremiumState: hooked " + TARGET);
            } else {
                Log.e("PATCH", "PremiumState: hook_function refused " + TARGET);
            }
        } catch (Exception e) {
            Log.e("PATCH", "PremiumState: " + TARGET + ": " + e);
        }
    }

    public void unload() {
        Log.i("PATCH", "PremiumState: Patch unloaded");
    }
}
