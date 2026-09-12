package com.smali_generator;

import android.content.ContentProvider;
import android.content.ContentValues;
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


@SuppressWarnings("unused")
public class InitProviderMoovit extends ContentProvider {

    @Override
    public boolean onCreate() {
        Log.i("PATCH", "InitProviderMoovit: onCreate called");
        on_load();
        return true;
    }

    @Override public Cursor query(@NonNull Uri u, String[] p, String s, String[] a, String o) { return null; }
    @Override public String getType(@NonNull Uri u) { return null; }
    @Override public Uri insert(@NonNull Uri u, ContentValues v) { return null; }
    @Override public int delete(@NonNull Uri u, String s, String[] a) { return 0; }
    @Override public int update(@NonNull Uri u, ContentValues v, String s, String[] a) { return 0; }

    static Hook[] hooks = {
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
    };

    static AtomicBoolean is_loaded = new AtomicBoolean(false);

    public static void on_load() {
        if (is_loaded.getAndSet(true)) {
            return;
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