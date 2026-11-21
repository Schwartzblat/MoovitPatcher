package com.smali_generator.patches;

import android.util.Log;

import com.arthooks.ArtHooks;
import com.smali_generator.Hook;

import java.lang.reflect.Executable;
import java.lang.reflect.Method;

/**
 * Disables Moovit's hard "block paywall".
 *
 * MoovitAppActivity asks this predicate on every launch; when it answers true it
 * throws away the activity the user asked for, starts
 * com.moovit.app.plus.paywall.BlockPaywallActivity instead and finish()es
 * itself, so the whole app sits behind the Moovit Plus purchase screen. The same
 * predicate is also used to suppress onboarding and other popups while the block
 * is up.
 *
 * Polarity: true means "the block paywall is active", so the replacement returns
 * false -- the state the app is in for every user who is not in that
 * user-acquisition experiment.
 *
 * The target is a STATIC method, so the replacement takes no leading thiz; its
 * single parameter is the activity argument.
 *
 * Moovit removed the block paywall in 5.201.6. On those releases the finder
 * cannot fire, the class name below stays a template, and load() says the
 * feature is absent instead of trying to hook it.
 */
public class BlockPaywall implements Hook {
    private static final String CLASS_NAME = "{{PAYWALL_BLOCK_CLASS_NAME}}";
    private static final String TARGET =
            CLASS_NAME + ".{{PAYWALL_BLOCK_METHOD_NAME}}{{PAYWALL_BLOCK_METHOD_SIG}}";

    static boolean is_block_paywall_active(Object activity) {
        return false;
    }

    public void load() {
        if (CLASS_NAME.startsWith("{{")) {
            Log.i("PATCH", "BlockPaywall: this Moovit has no block paywall, nothing to hook");
            return;
        }
        try {
            if (!ArtHooks.is_available()) {
                Log.e("PATCH", "BlockPaywall: ArtHooks unavailable, " + TARGET + " NOT hooked");
                return;
            }
            Class<?> cls = Class.forName(CLASS_NAME);
            Executable original = ArtHooks.find_function(cls,
                    "{{PAYWALL_BLOCK_METHOD_NAME}}", "{{PAYWALL_BLOCK_METHOD_SIG}}");
            if (original == null) {
                Log.e("PATCH", "BlockPaywall: target not found: " + TARGET);
                return;
            }
            Method replacement = BlockPaywall.class
                    .getDeclaredMethod("is_block_paywall_active", Object.class);
            if (ArtHooks.hook_function(original, replacement)) {
                Log.i("PATCH", "BlockPaywall: hooked " + TARGET);
            } else {
                Log.e("PATCH", "BlockPaywall: hook_function refused " + TARGET);
            }
        } catch (Exception e) {
            Log.e("PATCH", "BlockPaywall: " + TARGET + ": " + e);
        }
    }

    public void unload() {
        Log.i("PATCH", "BlockPaywall: Patch unloaded");
    }
}
