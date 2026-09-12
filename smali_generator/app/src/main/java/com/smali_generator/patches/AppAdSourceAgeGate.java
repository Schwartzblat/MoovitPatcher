package com.smali_generator.patches;

import android.util.Log;

import com.arthooks.ArtHooks;
import com.smali_generator.Hook;

import java.lang.reflect.Executable;
import java.lang.reflect.Method;

/**
 * Forces Moovit's "is this ad source allowed for a user this old?" helper to say
 * no.
 *
 * The original compares the user age in seconds against the remote config value
 * "&lt;adUnitIdKey&gt;_user_age_seconds" and returns true when the source may be
 * requested. All three call sites treat false as "skip this source": the banner
 * view logs "Ignore show request for not allowed source" and runs its
 * removeAdView path, the interstitial flow records reason "user_age" and the
 * pre-load loop skips the source. false is therefore the no-ads polarity.
 *
 * Static method -> static replacement with NO leading thiz.
 */
public class AppAdSourceAgeGate implements Hook {
    private static final String TARGET =
            "{{APPAD_SOURCE_AGE_CLASS_NAME}}.{{APPAD_SOURCE_AGE_METHOD_NAME}}{{APPAD_SOURCE_AGE_METHOD_SIG}}";

    static boolean is_source_allowed(Object ad_source, long user_age_seconds) {
        return false;
    }

    public void load() {
        try {
            if (!ArtHooks.is_available()) {
                Log.e("PATCH", "AppAdSourceAgeGate: ArtHooks unavailable, " + TARGET + " NOT hooked");
                return;
            }
            Class<?> helper_class = Class.forName("{{APPAD_SOURCE_AGE_CLASS_NAME}}");
            Method replacement = AppAdSourceAgeGate.class.getDeclaredMethod(
                    "is_source_allowed", Object.class, long.class);
            Executable original = ArtHooks.find_function(
                    helper_class, "{{APPAD_SOURCE_AGE_METHOD_NAME}}", "{{APPAD_SOURCE_AGE_METHOD_SIG}}");
            if (original == null) {
                Log.e("PATCH", "AppAdSourceAgeGate: target not found: " + TARGET);
                return;
            }
            if (ArtHooks.hook_function(original, replacement)) {
                Log.i("PATCH", "AppAdSourceAgeGate: hooked " + TARGET);
            } else {
                Log.e("PATCH", "AppAdSourceAgeGate: hook_function refused " + TARGET);
            }
        } catch (Exception e) {
            Log.e("PATCH", "AppAdSourceAgeGate: " + TARGET + ": " + e.toString());
        }
    }

    public void unload() {
        Log.i("PATCH", "AppAdSourceAgeGate: Patch unloaded");
    }
}
