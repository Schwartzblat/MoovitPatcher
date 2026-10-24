package com.smali_generator.utils;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

import java.nio.charset.StandardCharsets;
import java.util.Locale;

public class CertSha1Test {
    private static final String I = "4D622E7E1D779C303365882A46431BC54B0BF7BA";
    private static final String O = "C56ABF7C6890113ED6654E381E2A1797DA3E7F6A";

    @Test public void hexOfAbc() {
        assertEquals("A9993E364706816ABA3E25717850C26C9CD0D89D",
                CertSha1.hex("abc".getBytes(StandardCharsets.UTF_8)));
    }
    @Test public void sha1HexRules() {
        assertTrue(CertSha1.isSha1Hex(I));
        assertTrue(CertSha1.isSha1Hex(I.toLowerCase(Locale.ROOT)));
        assertFalse(CertSha1.isSha1Hex(I.substring(1)));
        assertFalse(CertSha1.isSha1Hex(I + "A"));
        assertFalse(CertSha1.isSha1Hex("G" + I.substring(1)));
        assertFalse(CertSha1.isSha1Hex(""));
        assertFalse(CertSha1.isSha1Hex(null));
    }
    @Test public void differsRules() {
        assertTrue(CertSha1.differs(O, I));
        assertFalse(CertSha1.differs(I, I.toLowerCase(Locale.ROOT)));
        assertFalse(CertSha1.differs(null, I));
        assertFalse(CertSha1.differs(O, null));
        assertFalse(CertSha1.differs("zz", I));
        assertFalse(CertSha1.differs(O, "zz"));
    }
    @Test public void swapsTheInstalledCert() {
        assertEquals(O, CertSha1.swapped("X-Android-Cert", I, I, O));
        assertEquals(O.toLowerCase(Locale.ROOT),
                CertSha1.swapped("x-android-cert", I.toLowerCase(Locale.ROOT), I, O));
        assertEquals(O, CertSha1.swapped("X-Android-Cert", " " + I + " ", I, O));
    }
    @Test public void leavesEverythingElseAlone() {
        assertEquals(I, CertSha1.swapped("X-Android-Package", I, I, O));
        assertEquals("other", CertSha1.swapped("X-Android-Cert", "other", I, O));
        assertEquals(null, CertSha1.swapped("X-Android-Cert", null, I, O));
        assertEquals(I, CertSha1.swapped("X-Android-Cert", I, null, O));
        assertEquals(I, CertSha1.swapped("X-Android-Cert", I, I, null));
    }
}
