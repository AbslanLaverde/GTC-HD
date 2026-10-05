"""Finite Candidate A transfer checks; reuse the unchanged native bounds fixture.

Run from GTC-HD-Lab with --compiler <UCRT64_GXX> --output <fresh-output-dir>.
No expectations are regenerated and no original worktree is modified.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = '7d5aa1e656b9171524d01b1b22917197d8121cb4'
ACCEPTED = '46fa75236fa61d49d8e9424b3b44694b88aa07a9'
HARNESS = '13e19564bd038e3767a58b9f1f1d29b1d5f4f527'
HISTORICAL = {
    '001': 'ba148bedc74892722de93633ce08190dda406bf7',
    '002': 'f0f90ee799969b735ca90b6dd9491219f0b9cc92',
    '003': '76bdb9250befa62fcbf23fcff2ef962fe2f58215',
}
OBSERVER = {'001': 'exp001-observer', '002': 'exp002-obj-observer', '003': 'exp003-composition'}


def git(root, *args):
    return subprocess.check_output(['git', '--no-optional-locks', '-C', str(root), *args], text=True)


def changes(patch):
    return [s for s in patch.splitlines() if s.startswith(('+', '-')) and not s.startswith(('+++', '---'))]


def function(text, signature):
    start = text.index(signature)
    end = text.index('{', start) + 1
    depth = 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end] + '\n'


def main(args):
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    env = os.environ.copy()
    compiler = args.compiler.resolve()
    env['PATH'] = str(compiler.parent) + os.pathsep + env.get('PATH', '')
    env['TMPDIR'] = str(out)
    roots = {'A': ROOT / 'experiments/bsnes-candidate-a-revalidation-baseline'}
    roots.update({key: ROOT / f'experiments/bsnes-exp-{key}-corrected' for key in HISTORICAL})
    commands = []

    def run(name, argv):
        result = subprocess.run(list(map(str, argv)), env=env, capture_output=True, text=True,
                                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        (out / (name + '.log')).write_text(result.stdout + result.stderr, encoding='utf-8')
        commands.append({'name': name, 'argv': list(map(str, argv)), 'exit': result.returncode})
        (out / 'commands.json').write_text(json.dumps(commands, indent=2), encoding='utf-8')
        if result.returncode:
            raise RuntimeError(f'STOP: {name} failed ({result.returncode}); inspect retained log')
        return result.stdout

    source = {}
    corrected = {'bsnes/sfc/ppu/' + n for n in ('ppu.cpp', 'ppu.hpp', 'main.cpp', 'screen.cpp')}
    assert not git(roots['A'], 'status', '--porcelain', '--untracked-files=all')
    assert git(roots['A'], 'rev-parse', 'HEAD').strip() == HARNESS
    for key, root in roots.items():
        if key != 'A':
            # All native differences from the original observer must be exactly A.
            assert set(git(root, 'diff', '--name-only', HISTORICAL[key], '--', 'bsnes').splitlines()) == corrected
            for path in corrected:
                expected = git(root, 'diff', UPSTREAM, ACCEPTED, '--', path)
                actual = git(root, 'diff', HISTORICAL[key], '--', path)
                assert changes(actual) == changes(expected), (key, path)
            # Existing tests are preserved; the new checks live in GTC-HD-Lab.
            assert not git(root, 'diff', HISTORICAL[key], '--', f'tests/exp{key}')
        source[key] = {'branch': git(root, 'branch', '--show-current').strip(),
                       'head_before_commit': git(root, 'rev-parse', 'HEAD').strip(),
                       'correction_delta_exact': True}

    fixture = (roots['A'] / 'tests/native-output-bounds/native-fixture.cpp').read_text()
    models = {}
    for key, root in roots.items():
        model = out / key
        model.mkdir()
        ppu_dir = root / 'bsnes/sfc/ppu'
        for original in ppu_dir.rglob('*'):
            if original.is_file() and original.suffix in ('.hpp', '.cpp'):
                dest = model / original.relative_to(ppu_dir)
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(original.read_text(), encoding='utf-8')
        text = (model / 'ppu.cpp').read_text()
        selected = ''.join(function(text, sig) for sig in ('PPU::PPU()', 'auto PPU::step()',
                           'auto PPU::step(uint clocks)', 'auto PPU::power(bool reset)', 'auto PPU::refresh()'))
        (model / 'selected.inc').write_text(selected, encoding='utf-8')
        text = (model / 'io.cpp').read_text()
        selected = ''.join(function(text, sig) for sig in ('auto PPU::readCGRAM', 'auto PPU::writeCGRAM', 'auto PPU::updateVideoMode'))
        (model / 'selected-io.inc').write_text(selected, encoding='utf-8')
        screen = (model / 'screen.cpp').read_text()
        traced = screen.replace('auto PPU::Screen::below(bool hires) -> uint16 {',
                                'auto PPU::Screen::below(bool hires) -> uint16 { traceBelow();')
        traced = traced.replace('auto PPU::Screen::above() -> uint16 {',
                                'auto PPU::Screen::above() -> uint16 { traceAbove();')
        traced = traced.replace('  ppu.latch.cgramAddress = palette;',
                                '  tracePalette(palette);\n  ppu.latch.cgramAddress = palette;')
        traced, count = re.subn(r'ppu\.lightTable\[ppu\.io\.displayBrightness\]\[([^\]]+)\]',
                                r'traceLookup(ppu.io.displayBrightness, \1)', traced)
        assert count == 2
        (model / 'screen-traced.inc').write_text(traced, encoding='utf-8')
        host = fixture
        if key != 'A':
            host = host.replace('namespace Fixture {', f'#include "{OBSERVER[key]}.cpp"\nnamespace Fixture {{\nnamespace Exp{key} = SuperFamicom::Exp{key};', 1)
            if key == '003':
                host = host.replace('PPU ppu;', 'PPU ppu;\n#include "exp003-hooks.cpp"', 1)
        # Only includes/namespace wiring differ; assertions and native methods do not.
        (model / 'fixture.cpp').write_text(host, encoding='utf-8')
        models[key] = model

    results = {}
    for opt in ('O0', 'O3'):
        for key, model in models.items():
            name = f'{key}-{opt}'
            exe = out / (name + '.exe')
            argv = [compiler, '-std=gnu++17', '-' + opt, '-g', '-Wall', '-Wextra', '-Werror',
                    '-Wno-parentheses', '-Wno-sign-compare', '-fno-access-control', '-I', model,
                    '-isystem', roots[key], '-isystem', roots[key] / 'bsnes',
                    '-DMODEL_U=0', '-DTRACE=1', model / 'fixture.cpp', '-o', exe]
            run(name + '-compile', argv)
            results[name] = json.loads(run(name, [exe, out / name]))
            assert results[name] == results['A-' + opt], (name, results[name])
            print('PASS: ' + name, flush=True)
    streams = {}
    for stream in ('presentation', 'state', 'screen'):
        files = sorted(out.glob(f'*-{stream}.bin'))
        hashes = {hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        assert len(files) == 8 and len(hashes) == 1, stream
        streams[stream] = {'sha256': hashes.pop(), 'bytes': files[0].stat().st_size}
    summary = {'status': 'PASSED', 'native_baseline': ACCEPTED, 'harness': HARNESS,
               'sources': source, 'results': results, 'equal_streams': streams}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--compiler', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    main(parser.parse_args())
