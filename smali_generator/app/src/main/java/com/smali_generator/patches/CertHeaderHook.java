package com.smali_generator.patches;

import android.util.Log;

import com.arthooks.ArtHooks;
import com.smali_generator.Hook;
import com.smali_generator.utils.AppCert;
import com.smali_generator.utils.CertSha1;

import java.lang.reflect.Method;
import java.net.URLConnection;
import java.util.Collections;
import java.util.HashSet;
import java.util.Set;

/**
 * Google's libraries send the installed certificate's SHA-1 in X-Android-Cert,
 * and API keys restricted to the original app's certificate reject the
 * re-signed one. Swap the original in at the HttpURLConnection layer, where
 * those libraries set the header.
 */
public class CertHeaderHook implements Hook {

    private static final String TAG = "PATCH";
    private static final String HEADER = "X-Android-Cert";

    private static final Set<String> logged = Collections.synchronizedSet(new HashSet<String>());

    private static String swap(Object thiz, String field, String value) {
        String out = value;
        try {
            out = CertSha1.swapped(field, value, AppCert.installed(), AppCert.original());
            if (out != value && logged.add(String.valueOf(host(thiz)))) {
                Log.i(TAG, "Cert: swapped " + HEADER + " for " + host(thiz));
            }
        } catch (Throwable t) {
            Log.e(TAG, "Cert: " + t);
        }
        return out;
    }

    private static String host(Object thiz) {
        try {
            return ((URLConnection) thiz).getURL().getHost();
        } catch (Throwable t) {
            return null;
        }
    }

    static native void impl_set_backup(Object thiz, String field, String value);

    static native void impl_add_backup(Object thiz, String field, String value);

    static native void https_set_backup(Object thiz, String field, String value);

    static native void https_add_backup(Object thiz, String field, String value);

    static void impl_set(Object thiz, String field, String value) {
        impl_set_backup(thiz, field, swap(thiz, field, value));
    }

    static void impl_add(Object thiz, String field, String value) {
        impl_add_backup(thiz, field, swap(thiz, field, value));
    }

    static void https_set(Object thiz, String field, String value) {
        https_set_backup(thiz, field, swap(thiz, field, value));
    }

    static void https_add(Object thiz, String field, String value) {
        https_add_backup(thiz, field, swap(thiz, field, value));
    }

    private static void hook(Method original, String replacement, Class<?>... params) {
        try {
            boolean ok = ArtHooks.hook_function(original,
                    CertHeaderHook.class.getDeclaredMethod(replacement, params),
                    CertHeaderHook.class.getDeclaredMethod(replacement + "_backup", params));
            Log.i(TAG, "Cert: hooked " + original.getDeclaringClass().getSimpleName() + "." + original.getName() + " = " + ok);
        } catch (Throwable t) {
            Log.e(TAG, "Cert: " + original.getName() + ": " + t);
        }
    }

    private static void hookClass(String className, String set, String add) {
        try {
            Class<?> c = Class.forName(className);
            Class<?>[] params = {Object.class, String.class, String.class};
            hook(c.getDeclaredMethod("setRequestProperty", String.class, String.class), set, params);
            hook(c.getDeclaredMethod("addRequestProperty", String.class, String.class), add, params);
        } catch (Throwable t) {
            Log.e(TAG, "Cert: " + className + ": " + t);
        }
    }

    public void load() {
        try {
            if (!AppCert.active()) {
                Log.i(TAG, "Cert: header swap not installed");
                return;
            }
            hookClass("com.android.okhttp.internal.huc.HttpURLConnectionImpl", "impl_set", "impl_add");
            hookClass("com.android.okhttp.internal.huc.DelegatingHttpsURLConnection", "https_set", "https_add");
        } catch (Throwable t) {
            Log.e(TAG, "Cert: " + t);
        }
    }

    public void unload() {
    }
}
