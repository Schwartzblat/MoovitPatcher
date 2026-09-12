package com.smali_generator.patches;

import android.util.Log;

import com.smali_generator.Hook;

import java.lang.reflect.Method;

import com.arthooks.ArtHooks;


public class SubscriptionManager implements Hook {
    private static final String TARGET =
            "{{SUBSCRIPTION_MANAGER_CLASS_NAME}}.{{SUBSCRIPTION_MANAGER_METHOD_NAME}}{{SUBSCRIPTION_MANAGER_METHOD_SIG}}";

    static boolean is_subscribed(Object self) {
        return true;
    }

    public void load() {
        try {
            if (!ArtHooks.is_available()) {
                Log.e("PATCH", "SubscriptionManager: ArtHooks unavailable (wrong --arch?), " + TARGET + " NOT hooked");
                return;
            }
            Class<?> subscription_manager_class = Class.forName("{{SUBSCRIPTION_MANAGER_CLASS_NAME}}");
            Method is_subscribed_hook = SubscriptionManager.class.getDeclaredMethod("is_subscribed", Object.class);
            Method original_is_subscribed = subscription_manager_class.getDeclaredMethod("{{SUBSCRIPTION_MANAGER_METHOD_NAME}}");
            if (ArtHooks.hook_function(original_is_subscribed, is_subscribed_hook)) {
                Log.i("PATCH", "SubscriptionManager: hooked " + TARGET);
            } else {
                Log.e("PATCH", "SubscriptionManager: hook_function refused " + TARGET);
            }
        } catch (Exception e) {
            Log.e("PATCH", "SubscriptionManager: " + TARGET + ": " + e.toString());
        }
    }

    public void unload() {
        Log.i("PATCH", "SubscriptionManager: Patch unloaded");
    }
}
