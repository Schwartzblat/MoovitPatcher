package com.smali_generator.patches;

import android.util.Log;

import com.arthooks.ArtHooks;
import com.smali_generator.Hook;

import java.lang.reflect.Executable;
import java.lang.reflect.Method;

/**
 * Neutralises com.moovit.app.ads.MoovitBannerAdView's "load the banner" entry
 * point.
 *
 * The original resolves the hosting activity, then asks the app ads manager for
 * an ad reference and attaches the returned banner to the view. It is the only
 * place this view starts an ad request from - setAdSource, onSizeChanged,
 * onWindowVisibilityChanged and the ads-updated broadcast receiver all funnel
 * into it - so doing nothing leaves the container empty and requests no ad.
 *
 * Instance method with no arguments -> static replacement taking only the
 * leading Object thiz.
 */
public class AppBannerAdLoad implements Hook {
    private static final String TARGET =
            "{{APPAD_BANNER_LOAD_CLASS_NAME}}.{{APPAD_BANNER_LOAD_METHOD_NAME}}{{APPAD_BANNER_LOAD_METHOD_SIG}}";

    static void load_ad(Object thiz) {
    }

    public void load() {
        try {
            if (!ArtHooks.is_available()) {
                Log.e("PATCH", "AppBannerAdLoad: ArtHooks unavailable, " + TARGET + " NOT hooked");
                return;
            }
            Class<?> banner_view_class = Class.forName("{{APPAD_BANNER_LOAD_CLASS_NAME}}");
            Method replacement = AppBannerAdLoad.class.getDeclaredMethod("load_ad", Object.class);
            Executable original = ArtHooks.find_function(
                    banner_view_class, "{{APPAD_BANNER_LOAD_METHOD_NAME}}", "{{APPAD_BANNER_LOAD_METHOD_SIG}}");
            if (original == null) {
                Log.e("PATCH", "AppBannerAdLoad: target not found: " + TARGET);
                return;
            }
            if (ArtHooks.hook_function(original, replacement)) {
                Log.i("PATCH", "AppBannerAdLoad: hooked " + TARGET);
            } else {
                Log.e("PATCH", "AppBannerAdLoad: hook_function refused " + TARGET);
            }
        } catch (Exception e) {
            Log.e("PATCH", "AppBannerAdLoad: " + TARGET + ": " + e.toString());
        }
    }

    public void unload() {
        Log.i("PATCH", "AppBannerAdLoad: Patch unloaded");
    }
}
