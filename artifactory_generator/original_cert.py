import hashlib
import zipfile

from androguard.core.apk import APK
from loguru import logger

logger.disable('androguard')


def _certificates(apk):
    for certs in (apk.get_certificates_der_v3(), apk.get_certificates_der_v2()):
        if certs:
            return list(certs)
    return [c.dump() for c in apk.get_certificates_v1()]


def _candidates(path, z):
    """Yield one androguard APK per candidate, reading a member only when it is tried."""
    names = z.namelist()
    inner = sorted((n for n in names if n.lower().endswith('.apk')), key=lambda n: (n != 'base.apk', n))
    if 'AndroidManifest.xml' in names or not inner:
        yield APK(path, skip_analysis=True)
    else:
        for n in inner:
            yield APK(z.read(n), raw=True, skip_analysis=True)


def original_cert_sha1(path):
    """SHA-1 (uppercase hex) of the single signer of an APK or APK bundle, or None."""
    try:
        with zipfile.ZipFile(path) as z:
            for apk in _candidates(path, z):
                certs = _certificates(apk)
                if certs:
                    distinct = set(certs)
                    if len(distinct) != 1:
                        return None
                    return hashlib.sha1(distinct.pop()).hexdigest().upper()
    except Exception:
        return None
    return None
