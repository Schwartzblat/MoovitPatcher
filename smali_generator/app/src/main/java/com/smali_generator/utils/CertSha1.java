package com.smali_generator.utils;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Locale;

/** Pure certificate SHA-1 rules; no android.* references so it runs on the JVM. */
public final class CertSha1 {
    private static final String HEADER = "X-Android-Cert";
    private static final char[] HEX = "0123456789ABCDEF".toCharArray();

    private CertSha1() {}

    public static String hex(byte[] der) {
        try {
            byte[] d = MessageDigest.getInstance("SHA-1").digest(der);
            char[] out = new char[d.length * 2];
            for (int i = 0; i < d.length; i++) {
                out[i * 2] = HEX[(d[i] >> 4) & 0xF];
                out[i * 2 + 1] = HEX[d[i] & 0xF];
            }
            return new String(out);
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException(e);
        }
    }

    public static boolean isSha1Hex(String s) {
        if (s == null || s.length() != 40) return false;
        for (int i = 0; i < 40; i++) {
            if (Character.digit(s.charAt(i), 16) < 0 || s.charAt(i) > 'f') return false;
        }
        return true;
    }

    public static boolean differs(String original, String installed) {
        return isSha1Hex(original) && isSha1Hex(installed) && !original.equalsIgnoreCase(installed);
    }

    public static String swapped(String header, String value, String installed, String original) {
        if (value == null || installed == null || original == null) return value;
        if (header == null || !HEADER.equalsIgnoreCase(header)) return value;
        String v = value.trim();
        if (!isSha1Hex(v) || !v.equalsIgnoreCase(installed)) return value;
        boolean hasUpper = !v.equals(v.toLowerCase(Locale.ROOT));
        return hasUpper ? original : original.toLowerCase(Locale.ROOT);
    }
}
