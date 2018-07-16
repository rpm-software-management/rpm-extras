"""
Tests for brp-mangle-shebangs

Usage:

    $ python3.7 -m venv __venv__
    $ . __venv__/bin/activate
    (__venv__) $ python -m pip install pytest
    (__venv__) $ python -m pytest -v test_brp_mangle_shebangs.py

License: https://fedoraproject.org/wiki/Legal:Fedora_Project_Contributor_Agreement (MIT)
"""

import os
import pathlib
import subprocess
import sys
import pytest


if sys.version_info < (3, 7):
    raise RuntimeError('Python 3.7+ only!')


parametrize = pytest.mark.parametrize


GOOD_SHEBANGS = (
    '/usr/bin/python3',
    '/usr/bin/python3 -s',
    '/usr/bin/python2',
    '/usr/bin/perl',
    '/usr/bin/ruby',
    '/usr/bin/ruby -0',
    '/usr/bin/rm',
    '/home/bob/stuff/usr/bin/python',
    '/usr/libexec/neutrinoval/env --oscillation',
    '/usr/libexec/platform-python',
)

MANGLE_PAIRS_OK = {
    '/usr/bin/env ruby': '/usr/bin/ruby',
    '/usr/bin/env python3': '/usr/bin/python3',
    '/bin/env bash': '/usr/bin/bash',
    '/bin/rm': '/usr/bin/rm',
}

MANGLE_PAIRS_WARN = {
    '/usr/bin/env python': '/usr/bin/python2',
    '/usr/bin/python': '/usr/bin/python2',
    '/bin/python': '/usr/bin/python2',
    '/bin/env python': '/usr/bin/python2',
}


@pytest.fixture(autouse=True)
def rpmroot(tmpdir):
    root = tmpdir.mkdir('root')
    old_rpmb_build_root = os.environ.get('RPM_BUILD_ROOT', None)
    os.environ['RPM_BUILD_ROOT'] = str(root)
    try:
        yield root
    finally:
        if old_rpmb_build_root is None:
            del os.environ['RPM_BUILD_ROOT']
        else:
            os.environ['RPM_BUILD_ROOT'] = old_rpmb_build_root


def create(shebang, *, space=None, name='script'):
    script = pathlib.Path(os.environ['RPM_BUILD_ROOT']) / name
    s = space if space else ''
    shebang = f'#!{s}{shebang}'
    script.write_text(shebang + '\n')
    script.chmod(0o755)
    return script


def mangle(*args):
    result = subprocess.run(['./brp-mangle-shebangs', *args],
                            text=True, capture_output=True)
    print('OUT:', result.stdout)
    print('ERR:', result.stderr)
    return result


@parametrize('shebang', GOOD_SHEBANGS)
def test_good_shebangs_are_left_intact(shebang):
    script = create(shebang)
    content = script.read_text()
    result = mangle()
    assert not result.stdout
    assert not result.stderr
    assert content == script.read_text()


@parametrize('space', ('', ' ', '\t', '   '))
def test_good_shebangs_are_left_intact_even_with_spaces(space):
    script = create(GOOD_SHEBANGS[0], space=space)
    content = script.read_text()
    mangle()

    assert content == script.read_text()


@parametrize('shebang', MANGLE_PAIRS_OK)
def test_shebangs_are_mangled(shebang):
    expected = MANGLE_PAIRS_OK[shebang]
    script = create(shebang)
    result = mangle()

    out = result.stdout.strip()
    assert out == (f'mangling shebang in /script from '
                   f'{shebang} to #!{expected}')
    assert not result.stderr
    line = script.read_text().splitlines()[0].strip()
    assert line == f'#!{expected}'


@parametrize('shebang', MANGLE_PAIRS_WARN)
def test_python_shebangs_are_mangled_warned(shebang):
    expected = MANGLE_PAIRS_WARN[shebang]
    script = create(shebang)
    result = mangle()

    assert not result.stdout
    err = result.stderr.strip()
    assert err == (f'*** WARNING: mangling shebang in /script from '
                   f'#!{shebang} to #!{expected}. This will become '
                   f'an ERROR, fix it manually!')
    line = script.read_text().splitlines()[0].strip()
    assert line == f'#!{expected}'


def test_multiple_files_can_be_mangled():
    good = GOOD_SHEBANGS[0]
    bad0, bad1 = list(MANGLE_PAIRS_OK)[:2]
    create(good, name='a')
    create(bad0, name='b')
    create(bad1, name='c')
    result = mangle()

    out = result.stdout.splitlines()
    assert len(out) == 2
    out = sorted(out)  # order is undefined
    assert 'mangling shebang in /b' in out[0]
    assert 'mangling shebang in /c' in out[1]

    assert not result.stderr


def test_files_can_be_ignored():
    shebang = list(MANGLE_PAIRS_OK)[0]
    create(shebang, name='yes')
    create(shebang, name='please')
    create(shebang, name='nope')
    create(shebang, name='no-way')
    result = mangle('--files=no')

    out = result.stdout
    assert len(out.splitlines()) == 2
    assert 'yes' in out
    assert 'please' in out
    assert 'nope' not in out
    assert 'no-way' not in out

    assert not result.stderr


def test_files_can_be_ignored_with_list(tmpdir):
    shebang = list(MANGLE_PAIRS_OK)[0]
    create(shebang, name='please')
    create(shebang, name='nope')
    create(shebang, name='never')
    lst = tmpdir.join('lst')
    lst.write('n(o)\n[^o]v\n')
    result = mangle(f'--files-from={lst}')

    out = result.stdout
    assert len(out.splitlines()) == 1
    assert 'please' in out
    assert 'nope' not in out
    assert 'never' not in out

    assert not result.stderr


def test_shabngs_can_be_ignored():
    create('/bin/env perl', name='yes')
    create('/bin/env php', name='no')
    result = mangle('--shebangs=ph?p')

    out = result.stdout
    assert len(out.splitlines()) == 1
    assert 'perl' in out
    assert 'php' not in out

    assert not result.stderr


def test_shabngs_can_be_ignored_list(tmpdir):
    lst = tmpdir.join('lst')
    lst.write('p(e|h)\nruby\n')
    create('/bin/env python3', name='yes')
    create('/bin/env perl', name='no1')
    create('/bin/env php', name='no2')
    create('/bin/env ruby', name='no3')
    result = mangle(f'--shebangs-from={lst}')

    out = result.stdout
    assert len(out.splitlines()) == 1
    assert 'python' in out
    assert 'perl' not in out
    assert 'php' not in out
    assert 'ruby' not in out

    assert not result.stderr


def test_no_executable_no_mangling():
    script = create(list(MANGLE_PAIRS_OK)[0])
    script.chmod(0o644)
    content = script.read_text()
    mangle()
    assert content == script.read_text()


@parametrize('has_shebang', (True, False))
def test_empty_no_shebang_removes_executable_bit(has_shebang):
    script = create('')
    if not has_shebang:
        script.write_text('text\n')
    content = script.read_text()
    mangle()
    assert content == script.read_text()
    assert not script.stat().st_mode & os.X_OK


def test_relative_shebang_errors():
    create('relative/path')
    result = mangle()
    assert 'ERROR' in result.stderr
    assert "script has shebang which doesn't start with '/'" in result.stderr
    assert result.returncode > 0
