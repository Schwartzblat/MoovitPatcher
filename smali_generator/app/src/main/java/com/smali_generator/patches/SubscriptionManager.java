package com.smali_generator.patches;

import android.util.Log;

import com.smali_generator.Hook;

import java.lang.reflect.Method;

import lab.galaxy.yahfa.HookMain;


public class SubscriptionManager implements Hook {
    static boolean is_subscribed(Object self) {
        return true;
    }

    public void load() {
        Log.i("PATCH", "SubscriptionManager: Patch loaded");
        try {
            Class<?> subscription_manager_class = Class.forName("{{SUBSCRIPTION_MANAGER_CLASS_NAME}}");
            Method is_subscribed_hook = SubscriptionManager.class.getDeclaredMethod("is_subscribed", Object.class);
            Method original_is_subscribed = subscription_manager_class.getDeclaredMethod("{{SUBSCRIPTION_MANAGER_METHOD_NAME}}");
            HookMain.hook(original_is_subscribed, is_subscribed_hook);
        } catch (Exception e) {
            Log.e("PATCH", "SubscriptionManager: " + e.toString());
        }

    }

    public void unload() {
        Log.i("PATCH", "ActivityHook: Patch unloaded");
    }
}
