package com.smali_generator.patches;

import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.util.Log;

import com.smali_generator.Hook;
import com.smali_generator.utils.AppCert;
import com.smali_generator.utils.MapsTokenService;

import java.util.concurrent.Executor;

/**
 * Answers the Google Maps SDK's bind to Play services' ApiTokenService with a
 * local binder that fetches the token using the original certificate.
 */
public class MapsTokenHook implements Hook {

    private static final String TAG = "PATCH";
    private static final String GMS = "com.google.android.gms";
    private static final String TOKEN_SERVICE = "com.google.android.gms.maps.auth.ApiTokenService";

    private static final BindServiceHook.Handler HANDLER = new BindServiceHook.Handler() {
        @Override
        public BindServiceHook.Decision onBind(Context thiz, Intent intent, ServiceConnection conn,
                                               Executor executor) {
            ComponentName component = intent.getComponent();
            if (conn == null || component == null
                    || !GMS.equals(component.getPackageName())
                    || !TOKEN_SERVICE.equals(component.getClassName())) {
                return BindServiceHook.Decision.PASS;
            }
            // Not thiz.getPackageName(): a package context made by Play services code
            // would report com.google.android.gms.
            String own = AppCert.packageName();
            if (own == null) {
                return BindServiceHook.Decision.PASS;
            }
            BindServiceHook.deliver(conn, executor, component, new MapsTokenService(own));
            Log.i(TAG, "Maps: answering the token service in-process");
            return BindServiceHook.Decision.FAKE;
        }
    };

    @Override
    public void load() {
        if (!AppCert.active()) {
            Log.i(TAG, "Maps: token service left to Play services (Google API fix off)");
            return;
        }
        BindServiceHook.register(HANDLER);
    }

    @Override
    public void unload() {}
}
