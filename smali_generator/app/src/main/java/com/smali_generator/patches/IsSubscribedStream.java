package com.smali_generator.patches;

import android.util.Log;

import com.arthooks.ArtHooks;
import com.smali_generator.Hook;

import java.lang.reflect.Constructor;
import java.lang.reflect.Executable;
import java.lang.reflect.Method;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Makes the entitlements-based "is subscribed" stream say yes.
 *
 * Since 5.201.6 Moovit's subscription library publishes the owned entitlements
 * as one wrapper object holding a List, and IsSubscribedStreamUseCase maps it to
 * "the list is non-empty". The "Remove ads with Moovit+" promo cell, the Moovit+
 * tab and one more view model observe that Boolean rather than asking
 * SubscriptionBridgeImpl, so SubscriptionManager alone leaves them showing the
 * upsell.
 *
 * The target is the use case's FlowCollector emit(value, continuation). The
 * replacement calls the original with a wrapper holding a one-element list, so
 * the original maps it to true and emits that downstream with its own
 * continuation handling. The wrapper never travels further than that method.
 *
 * Older releases have no such stream: the finder cannot fire, the class name
 * below stays a template, and load() says so instead of hooking.
 */
public class IsSubscribedStream implements Hook {
    private static final String CLASS_NAME = "{{IS_SUBSCRIBED_STREAM_CLASS_NAME}}";
    private static final String TARGET = CLASS_NAME
            + ".{{IS_SUBSCRIBED_STREAM_METHOD_NAME}}{{IS_SUBSCRIBED_STREAM_METHOD_SIG}}";

    /** A wrapper holding a non-empty list, published before the hook goes live. */
    private static volatile Object subscribed_value = null;

    private static final AtomicBoolean logged_first_emit = new AtomicBoolean(false);

    static Object emit(Object thiz, Object value, Object continuation) {
        if (!logged_first_emit.getAndSet(true)) {
            Log.i("PATCH", "IsSubscribedStream: reporting subscribed");
        }
        return emit_backup(thiz, subscribed_value, continuation);
    }

    // static native, no body: ArtHooks points it at the original emit.
    static native Object emit_backup(Object thiz, Object value, Object continuation);

    public void load() {
        if (CLASS_NAME.startsWith("{{")) {
            Log.i("PATCH", "IsSubscribedStream: this Moovit has no entitlements stream, nothing to hook");
            return;
        }
        try {
            if (!ArtHooks.is_available()) {
                Log.e("PATCH", "IsSubscribedStream: ArtHooks unavailable, " + TARGET + " NOT hooked");
                return;
            }
            Class<?> value_class = Class.forName("{{IS_SUBSCRIBED_STREAM_VALUE_CLASS_NAME}}");
            Constructor<?> value_ctor = value_class.getDeclaredConstructor(List.class);
            value_ctor.setAccessible(true);
            Object value = value_ctor.newInstance(Collections.singletonList("PATCH"));

            Class<?> cls = Class.forName(CLASS_NAME);
            Executable original = ArtHooks.find_function(cls,
                    "{{IS_SUBSCRIBED_STREAM_METHOD_NAME}}", "{{IS_SUBSCRIBED_STREAM_METHOD_SIG}}");
            if (original == null) {
                Log.e("PATCH", "IsSubscribedStream: target not found: " + TARGET);
                return;
            }
            Method replacement = IsSubscribedStream.class
                    .getDeclaredMethod("emit", Object.class, Object.class, Object.class);
            Method backup = IsSubscribedStream.class
                    .getDeclaredMethod("emit_backup", Object.class, Object.class, Object.class);

            subscribed_value = value;
            if (ArtHooks.hook_function(original, replacement, backup)) {
                Log.i("PATCH", "IsSubscribedStream: hooked " + TARGET);
            } else {
                Log.e("PATCH", "IsSubscribedStream: hook_function refused " + TARGET);
            }
        } catch (Throwable t) {
            Log.e("PATCH", "IsSubscribedStream: " + TARGET + ": " + t);
        }
    }

    public void unload() {
        Log.i("PATCH", "IsSubscribedStream: Patch unloaded");
    }
}
