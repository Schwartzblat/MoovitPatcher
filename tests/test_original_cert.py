import os
import zipfile
from pathlib import Path

import pytest

from artifactory_generator.original_cert import original_cert_sha1

FIXTURES = Path(__file__).parent / 'fixtures'
FIXTURE_SHA1 = '059AC602869BAE045D90B454E97635A0104CB5FD'
MOOVIT_BASE = '/opt/patched/com.tranzmate/5.201.6.1811/unzipped/base.apk'


def test_reads_a_v2_v3_signed_apk():
    assert original_cert_sha1(str(FIXTURES / 'signed.apk')) == FIXTURE_SHA1


def test_falls_back_to_the_v1_signature():
    assert original_cert_sha1(str(FIXTURES / 'signed-v1-only.apk')) == FIXTURE_SHA1


def test_two_signers_give_none():
    assert original_cert_sha1(str(FIXTURES / 'signed-twice.apk')) is None


def test_unsigned_or_missing_gives_none(tmp_path):
    unsigned = tmp_path / 'unsigned.apk'
    with zipfile.ZipFile(unsigned, 'w') as z:
        z.writestr('x.txt', 'fixture')
    text = tmp_path / 'note.txt'
    text.write_text('not a zip')
    assert original_cert_sha1(str(unsigned)) is None
    assert original_cert_sha1(str(text)) is None
    assert original_cert_sha1(str(tmp_path / 'missing.apk')) is None


@pytest.mark.parametrize('suffix', ['xapk', 'apkm'])
def test_reads_inside_an_xapk_whatever_the_entry_order(tmp_path, suffix):
    apk = (FIXTURES / 'signed.apk').read_bytes()
    other = (FIXTURES / 'signed-twice.apk').read_bytes()
    bundle = tmp_path / f'app.{suffix}'
    with zipfile.ZipFile(bundle, 'w') as z:
        z.writestr('manifest.json', '{}')
        z.writestr('config.en.apk', other)
        z.writestr('base.apk', apk)
    assert original_cert_sha1(str(bundle)) == FIXTURE_SHA1


@pytest.mark.parametrize('inner', ['signed-twice.apk', 'signed.apk'])
def test_an_apk_with_an_embedded_apk_is_judged_by_its_own_signer(tmp_path, inner):
    apk = tmp_path / 'outer.apk'
    with zipfile.ZipFile(apk, 'w') as z:
        z.writestr('AndroidManifest.xml', 'manifest')
        z.writestr('assets/inner.apk', (FIXTURES / inner).read_bytes())
    assert original_cert_sha1(str(apk)) is None


@pytest.mark.skipif(not os.path.exists(MOOVIT_BASE), reason='Moovit corpus APK is absent')
def test_moovit_original():
    assert original_cert_sha1(MOOVIT_BASE) == 'C56ABF7C6890113ED6654E381E2A1797DA3E7F6A'
