package com.smali_generator.patches;

import android.util.Log;

import com.arthooks.ArtHooks;
import com.smali_generator.Hook;

import java.lang.reflect.Executable;
import java.lang.reflect.Method;

/**
 * Keeps the sponsored map-item layer off the map.
 *
 * com.moovit.app.map.layers.MapAdsLayerManager holds a single sponsored
 * MapItemCollection, created in its constructor, and one no-argument void method
 * that reconciles the map with the current decision: it computes "should map ads
 * be shown" from the map-ads feature flag and the "is_ads_free_version" remote
 * config flag, and then registers the collection on the MapFragment or removes it
 * again, recording the new state in a boolean field.
 *
 * That method both adds and removes, so a no-op could in principle freeze a
 * registered collection in place - but it cannot here: it is the only code in the
 * apk that registers this collection (the collection object itself is reachable
 * from nowhere else), and the "currently registered" field starts false and is
 * only ever written by this same method. Never running it therefore means the
 * collection is never registered in the first place, with nothing left stranded,
 * rather than freezing whatever state is current.
 *
 * The manager's lifecycle callbacks are untouched: they only attach and detach
 * the map-ready listener and the ads-updated broadcast receiver - the two things
 * that call this method - and never touch the collection themselves.
 *
 * Instance method with no arguments -> static replacement taking only the leading
 * Object thiz.
 */
public class AppMapAdsLayer implements Hook {
    private static final String TARGET =
            "{{APPAD_MAPADS_CLASS_NAME}}.{{APPAD_MAPADS_METHOD_NAME}}{{APPAD_MAPADS_METHOD_SIG}}";

    static void sync_map_ads_layer(Object thiz) {
    }

    public void load() {
        try {
            if (!ArtHooks.is_available()) {
                Log.e("PATCH", "AppMapAdsLayer: ArtHooks unavailable, " + TARGET + " NOT hooked");
                return;
            }
            Class<?> layer_manager_class = Class.forName("{{APPAD_MAPADS_CLASS_NAME}}");
            Method replacement = AppMapAdsLayer.class.getDeclaredMethod("sync_map_ads_layer", Object.class);
            Executable original = ArtHooks.find_function(
                    layer_manager_class, "{{APPAD_MAPADS_METHOD_NAME}}", "{{APPAD_MAPADS_METHOD_SIG}}");
            if (original == null) {
                Log.e("PATCH", "AppMapAdsLayer: target not found: " + TARGET);
                return;
            }
            if (ArtHooks.hook_function(original, replacement)) {
                Log.i("PATCH", "AppMapAdsLayer: hooked " + TARGET);
            } else {
                Log.e("PATCH", "AppMapAdsLayer: hook_function refused " + TARGET);
            }
        } catch (Exception e) {
            Log.e("PATCH", "AppMapAdsLayer: " + TARGET + ": " + e.toString());
        }
    }

    public void unload() {
        Log.i("PATCH", "AppMapAdsLayer: Patch unloaded");
    }
}
