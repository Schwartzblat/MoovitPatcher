package com.smali_generator.patches;

import android.util.Log;

import com.arthooks.ArtHooks;
import com.smali_generator.Hook;

import java.lang.reflect.Executable;
import java.lang.reflect.Method;

/**
 * Neutralises com.moovit.app.ads.MoovitAdView's "build and request the banner"
 * entry point.
 *
 * The original constructs a Google mobile-ads banner AdView, starts the ad
 * request, attaches it to the view's FrameLayout and reports the AD analytics
 * event. Doing nothing instead means the view keeps an empty container: no ad is
 * requested and the "go ad free" button, which is only revealed by the ad
 * listener created here, stays hidden.
 *
 * Instance method -> static replacement with a leading Object thiz; the four
 * original arguments (MoovitApplication, MoovitBaseComponentActivity, AdSource,
 * String adUnitId) are all references, so Object keeps the frame layout intact.
 */
public class AppAdViewShow implements Hook {
    private static final String TARGET =
            "{{APPAD_VIEW_SHOW_CLASS_NAME}}.{{APPAD_VIEW_SHOW_METHOD_NAME}}{{APPAD_VIEW_SHOW_METHOD_SIG}}";

    static void show_banner(Object thiz, Object application, Object activity, Object ad_source, Object ad_unit_id) {
    }

    public void load() {
        try {
            if (!ArtHooks.is_available()) {
                Log.e("PATCH", "AppAdViewShow: ArtHooks unavailable, " + TARGET + " NOT hooked");
                return;
            }
            Class<?> ad_view_class = Class.forName("{{APPAD_VIEW_SHOW_CLASS_NAME}}");
            Method replacement = AppAdViewShow.class.getDeclaredMethod(
                    "show_banner", Object.class, Object.class, Object.class, Object.class, Object.class);
            Executable original = ArtHooks.find_function(
                    ad_view_class, "{{APPAD_VIEW_SHOW_METHOD_NAME}}", "{{APPAD_VIEW_SHOW_METHOD_SIG}}");
            if (original == null) {
                Log.e("PATCH", "AppAdViewShow: target not found: " + TARGET);
                return;
            }
            if (ArtHooks.hook_function(original, replacement)) {
                Log.i("PATCH", "AppAdViewShow: hooked " + TARGET);
            } else {
                Log.e("PATCH", "AppAdViewShow: hook_function refused " + TARGET);
            }
        } catch (Exception e) {
            Log.e("PATCH", "AppAdViewShow: " + TARGET + ": " + e.toString());
        }
    }

    public void unload() {
        Log.i("PATCH", "AppAdViewShow: Patch unloaded");
    }
}
