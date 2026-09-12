package com.smali_generator.patches;

import android.util.Log;

import com.arthooks.ArtHooks;
import com.smali_generator.Hook;

import java.lang.reflect.Executable;
import java.lang.reflect.Method;

/**
 * Forces Moovit's app-level ads manager to report "no ad unit configured" for
 * every com.moovit.app.ads.AdSource.
 *
 * The original method resolves the remote-config ad unit id for a source and
 * already returns the empty string when the ad-free flags are set, when the
 * config value is the "na" sentinel, or while a rewarded ad-free period is
 * active. Every caller treats the empty string as "no ad for this source":
 * banner views call their own removeAdView path, the interstitial flow records
 * reason "no_ad", the list decorators return the plain (ad free) adapter and the
 * "watch a video to remove ads" cell hides itself. Returning "" unconditionally
 * therefore takes the app's own ad-free branch everywhere at once.
 *
 * Instance method -> static replacement with a leading Object thiz.
 */
public class AppAdUnitIdResolver implements Hook {
    private static final String TARGET =
            "{{APPAD_ADUNIT_CLASS_NAME}}.{{APPAD_ADUNIT_METHOD_NAME}}{{APPAD_ADUNIT_METHOD_SIG}}";

    static String get_ad_unit_id(Object thiz, Object ad_source) {
        return "";
    }

    public void load() {
        try {
            if (!ArtHooks.is_available()) {
                Log.e("PATCH", "AppAdUnitIdResolver: ArtHooks unavailable, " + TARGET + " NOT hooked");
                return;
            }
            Class<?> manager_class = Class.forName("{{APPAD_ADUNIT_CLASS_NAME}}");
            Method replacement = AppAdUnitIdResolver.class.getDeclaredMethod(
                    "get_ad_unit_id", Object.class, Object.class);
            Executable original = ArtHooks.find_function(
                    manager_class, "{{APPAD_ADUNIT_METHOD_NAME}}", "{{APPAD_ADUNIT_METHOD_SIG}}");
            if (original == null) {
                Log.e("PATCH", "AppAdUnitIdResolver: target not found: " + TARGET);
                return;
            }
            if (ArtHooks.hook_function(original, replacement)) {
                Log.i("PATCH", "AppAdUnitIdResolver: hooked " + TARGET);
            } else {
                Log.e("PATCH", "AppAdUnitIdResolver: hook_function refused " + TARGET);
            }
        } catch (Exception e) {
            Log.e("PATCH", "AppAdUnitIdResolver: " + TARGET + ": " + e.toString());
        }
    }

    public void unload() {
        Log.i("PATCH", "AppAdUnitIdResolver: Patch unloaded");
    }
}
