package com.smali_generator;

import android.content.ContentProvider;
import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.net.Uri;
import android.util.Log;

import androidx.annotation.NonNull;

import java.util.concurrent.atomic.AtomicBoolean;
import com.smali_generator.patches.SubscriptionManager;
import com.smali_generator.patches.PremiumState;
import com.smali_generator.patches.PremiumFeaturePackages;
import com.smali_generator.patches.BlockPaywall;
import com.smali_generator.patches.AppAdUnitIdResolver;
import com.smali_generator.patches.AppAdSourceAgeGate;
import com.smali_generator.patches.AppAdViewShow;
import com.smali_generator.patches.AppBannerAdLoad;
import com.smali_generator.patches.AppMapAdsLayer;
import com.smali_generator.patches.BindServiceHook;
import com.smali_generator.patches.CertHeaderHook;
import com.smali_generator.patches.MapsTokenHook;
import com.smali_generator.utils.AppCert;


@SuppressWarnings("unused")
public class InitProviderMoovit extends ContentProvider {

    @Override
    public boolean onCreate() {
        Log.i("PATCH", "InitProviderMoovit: onCreate called");
        on_load(getContext());
        return true;
    }

    @Override public Cursor query(@NonNull Uri u, String[] p, String s, String[] a, String o) { return null; }
    @Override public String getType(@NonNull Uri u) { return null; }
    @Override public Uri insert(@NonNull Uri u, ContentValues v) { return null; }
    @Override public int delete(@NonNull Uri u, String s, String[] a) { return 0; }
    @Override public int update(@NonNull Uri u, ContentValues v, String s, String[] a) { return 0; }

    static Hook[] hooks = {
            // owns bindService; MapsTokenHook registers a handler with it
            new BindServiceHook(),
            // premium / subscription state
            new SubscriptionManager(),
            new PremiumState(),
            new PremiumFeaturePackages(),
            // paywall / feature gates
            new BlockPaywall(),
            // ad loaders (com.moovit.ads)
            // app ad layer (com.moovit.app.ads)
            new AppAdUnitIdResolver(),
            new AppAdSourceAgeGate(),
            new AppAdViewShow(),
            new AppBannerAdLoad(),
            new AppMapAdsLayer(),
            // Google APIs with the original certificate: X-Android-Cert, and the
            // Maps SDK's token service answered in-process
            new CertHeaderHook(),
            new MapsTokenHook(),
    };

    static AtomicBoolean is_loaded = new AtomicBoolean(false);

    public static void on_load(Context context) {
        if (is_loaded.getAndSet(true)) {
            return;
        }
        try {
            AppCert.init(context);
        } catch (Throwable t) {
            Log.e("PATCH", "AppCert init failed: Google API fix off", t);
        }

        Log.i("PATCH", "Patch loaded, running " + hooks.length + " hook(s)");
        // Per-hook isolation: one hook that dies must not stop the rest. Throwable,
        // not Exception -- a missing native lib raises UnsatisfiedLinkError, which
        // would otherwise escape onCreate and take the host app down at startup.
        for (Hook hook : hooks) {
            String name = hook.getClass().getSimpleName();
            try {
                hook.load();
            } catch (Throwable t) {
                Log.e("PATCH", name + ": load() threw, continuing with remaining hooks: " + t);
            }
        }
    }
}