"""Finite corrected-baseline transfer; fixed historical expectations, no retries.

Private inputs and fresh output directory are explicit arguments. The short
bounds fixture and its independent oracle are imported without changing them.
"""
import argparse
from collections import Counter
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'native-output-bounds-runtime'))
from run_validation import build, inspect_result, oracle, SRAM_SIZE

EXPECTED = {
    'rom': 'd70c9c7716ad12c674fc7dd744736aa48d4d7b4237f58066be620fda26024872',
    'sram': 'd0ff1b294b5288d1ae1421eadf5b2d38a8752b76d472ff30bed9028e25b1c5b8',
    'settings': 'e22fba1b0e141499c94a25652c6a2faebea27adb8a11d4ec2e84beda43a8fa6b',
    'historical_600': '92b098cf30a4171f707185b2a32918b8f361edf30ac8ba6aa3f1fead39bae96f',
    'historical_1800': '9bc5ff87fc19e52615cffb334ad9ad75900f4c8f12818972c210479a857b99fb',
    'historical_bg': 'bcc8e15d28c2a7918e65ed03ba467f33a767ea7edb3837b8bbf60c4e95b03964',
    'historical_obj': '7974e49dee1ef8110453938b54201042ba79afb3a1bfa57260ec220c93fc49c8',
    'historical_composition': 'c8084c47f39a9ef17b22f40f804ed30a02628f940c9caa299495f29a52381ee8',
}
BOUNDS_FRAMES = '69416871a6eaf2541a684a352c4a7e13972cb49470ccc8b0f436ca9866fd04de'
BOUNDS_SRAM = '75d6febfa8370ea0969e9ab06312552e60479803d090d44e781531e4f7932acc'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rows(path):
    with path.open() as f:
        return list(csv.DictReader(line for line in f if not line.startswith('#')))


def equal(actual, expected, label):
    if actual != expected:
        offset = next((i for i, (a, b) in enumerate(zip(actual, expected)) if a != b), min(len(actual), len(expected)))
        raise ValueError(f'{label}: first difference at byte {offset}; lengths {len(actual)}/{len(expected)}')


def semantic(key, path, count):
    summary = dict(line.split('=', 1) for line in path.with_suffix('.csv.summary.txt').read_text().splitlines() if line and not line.startswith('#'))
    required = {'requested_start_callback': '500', 'requested_callback_count': '1', 'end_callback_exclusive': '501',
                'window_started': 'true', 'window_completed': 'true', 'observed_callbacks': '1',
                'actual_native_callbacks': str(count), 'dropped_count': '0', 'overflow': 'false',
                'observer_enabled': 'false', 'export_attempted': 'true', 'export_succeeded': 'true',
                'capture_complete': 'true', 'reason': 'window_complete'}
    required.update({
        '001': {'record_count': '23760', 'capacity': '32768'},
        '002': {'record_count': '29772', 'capacity': '131072', 'record_bytes': '104', 'unknown_winners': '0',
                'evaluation_record_count': '28909', 'fetched_tile_record_count': '176', 'final_winner_record_count': '687'},
        '003': {'record_count': '61440', 'capacity': '65536', 'record_bytes': '176', 'unknown_provenance_count': '0',
                'candidate_window_suppressions': '0', 'bg_obj_competitions': '155', 'main_sub_source_disagreements': '47391'},
    }[key])
    for field, wanted in required.items():
        if summary.get(field) != wanted:
            raise ValueError(f'{key} {field}: {summary.get(field)}, expected {wanted}')
    records = [{k: int(v) for k, v in row.items()} for row in rows(path)]
    assert len(records) == int(required['record_count'])
    details = {}
    if key == '001':
        assert {r['bg'] for r in records} == {0, 1, 2}
        assert {r['bg_mode'] for r in records} == {1}
        assert {r['frame'] for r in records} == {500, 501}
        assert all(r['index'] == i for i, r in enumerate(records))
        details['bg_ids'] = [0, 1, 2]
    elif key == '002':
        assert Counter(r['kind'] for r in records) == {1: 28909, 2: 176, 3: 687}
        by_id = {r['id']: r for r in records}
        winners = [r for r in records if r['kind'] == 3]
        for winner in winners:
            fetch = by_id[winner['fetch_id']]
            evaluation = by_id[fetch['evaluation_id']]
            assert winner['source_known'] == 1 and fetch['kind'] == 2 and evaluation['kind'] == 1
            assert evaluation['selected'] and evaluation['id'] < fetch['id'] < winner['id']
            assert winner['oam_index'] == fetch['oam_index'] == evaluation['oam_index']
            for fid, x, color, palette in ((winner['fetch_id'], winner['source_x'], winner['color'], winner['palette_index']),
                                          (winner['previous_fetch_id'], winner['previous_source_x'], winner['previous_color'], winner['previous_palette_index'])):
                if fid:
                    source = by_id[fid]
                    decoded = sum(((source['row_data'] >> (7 - x + 8 * plane)) & 1) << plane for plane in range(4))
                    assert decoded == color and palette == source['palette_base'] + color
        witnesses = [r['id'] for r in winners if r['nontransparent_samples'] > 1 and r['previous_fetch_id'] != 0]
        assert witnesses == [22993, 22994, 23175, 23177, 23178, 23180, 23347, 23349, 23350, 23352, 23507, 23509]
        details.update(known_lineage_winners=len(winners), overlap_witnesses=witnesses)
    else:
        expected_counts = {'main': {0:11969, 2:22015, 4:687, 5:22673, 6:4096}, 'sub': {1:39087, 5:18257, 6:4096}}
        competitions = suppressions = 0
        for screen in ('main', 'sub'):
            counts = Counter(r[screen + '_source'] for r in records)
            assert counts == expected_counts[screen], (screen, counts)
            details[screen + '_counts'] = dict(counts)
            for r in records:
                source = r[screen + '_source']
                if source < 5:
                    assert r[screen + '_known'] == 1 and r[screen + '_token'] != 0
                competitions += source != 6 and any(r[f'{screen}_{i}_after'] for i in range(4)) and bool(r[f'{screen}_4_after'])
                for i in range(5):
                    before, after, outcome = (r[f'{screen}_{i}_{name}'] for name in ('before', 'after', 'outcome'))
                    wanted = 0 if not before else 1 if not after else 4 if source == 6 else 3 if source == i else 2
                    assert outcome == wanted
                    suppressions += outcome == 1
        disagreements = sum(r['main_source'] != r['sub_source'] for r in records)
        assert (competitions, disagreements, suppressions) == (155, 47391, 0)
        details.update(competitions=competitions, source_disagreements=disagreements, window_suppressions=suppressions)
    return {'summary': summary, 'verified_records': len(records), **details}


def main(args):
    out = args.output.resolve()
    inputs = {key: getattr(args, key).read_bytes() for key in EXPECTED}
    for key, data in inputs.items():
        assert sha(data) == EXPECTED[key], f'input identity mismatch: {key}'
    exes = {key: getattr(args, option).resolve() for key, option in [('A','baseline'),('001','exp001'),('002','exp002'),('003','exp003')]}
    hashes = {key: sha(exe.read_bytes()) for key, exe in exes.items()}
    control_frames = {}
    reused_controls = {}
    if bool(args.control_600) != bool(args.control_1800):
        raise ValueError('Supply both previously verified control CSVs or neither')
    if args.control_600:
        for count in (600, 1800):
            path = getattr(args, 'control_' + str(count)).resolve()
            data = path.read_bytes()
            equal(data, inputs['historical_' + str(count)], 'retained corrected control ' + str(count))
            control_frames[count] = data
            reused_controls[str(count)] = {'path': str(path), 'sha256': sha(data)}
    out.mkdir(parents=True, exist_ok=False)
    manifest = build(out / 'fixture')
    expected = oracle()
    (out / 'bounds-expected-before-run.json').write_text(json.dumps(expected, indent=2))
    fixture_dir = Path(__file__).resolve().parents[1] / 'native-output-bounds-runtime'
    bounds_settings = (fixture_dir / 'settings.bml').read_bytes()
    assert sha(bounds_settings) == '66677a7e58d2e41d4e0f6916e2cb9a7a2e96a2363296ff9799b93eb59a9bb999'
    result = {'status': 'RUNNING', 'inputs': EXPECTED, 'binaries': hashes, 'fixture': manifest,
              'reused_control_csvs': reused_controls, 'runs': []}
    env = os.environ.copy()
    env['PATH'] = str(args.dll_dir.resolve()) + os.pathsep + env.get('PATH', '')
    startup = None
    if os.name == 'nt':
        startup = subprocess.STARTUPINFO()
        startup.dwFlags = subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 0

    def save():
        (out / 'summary.json').write_text(json.dumps(result, indent=2), encoding='utf-8')

    def execute(key, name, count, capture=False, bounds=False):
        folder = out / name
        folder.mkdir()
        rom = folder / ('bounds-phase4.sfc' if bounds else 'game.sfc')
        rom.write_bytes((out / 'fixture/bounds-phase4.sfc').read_bytes() if bounds else inputs['rom'])
        rom.with_suffix('.srm').write_bytes(bytes(SRAM_SIZE) if bounds else inputs['sram'])
        config = folder / 'settings.bml'
        config.write_bytes(bounds_settings if bounds else inputs['settings'])
        assert sha(exes[key].read_bytes()) == hashes[key], 'executable changed after preflight'
        command = [str(exes[key]), f'--settings={config}', f'--exp001-frame-hash={folder / "frames.csv"}', f'--exp001-frame-count={count}']
        if capture:
            prefix = {'001':'exp001-observer', '002':'exp002-obj', '003':'exp003-composition'}[key]
            command += [f'--{prefix}-csv={folder / "provenance.csv"}', f'--{prefix}-start-callback=500', f'--{prefix}-callback-count=1']
        command.append(str(rom))
        run = {'name':name, 'directory':str(folder), 'executable_sha256':hashes[key], 'command':command, 'exit_code':None}
        result['runs'].append(run)
        save()
        print('RUN ' + name, flush=True)
        with (folder/'stdout.log').open('wb') as stdout, (folder/'stderr.log').open('wb') as stderr:
            p = subprocess.run(command, cwd=folder, env=env, startupinfo=startup,
                               creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0), stdout=stdout, stderr=stderr,
                               timeout=45 if bounds else 180)
        run['exit_code'] = p.returncode
        assert p.returncode == 0, f'process exit {p.returncode}'
        data = (folder/'frames.csv').read_bytes()
        run['csv_sha256'] = sha(data)
        if bounds:
            problems = inspect_result(run, expected)
            assert not problems, problems
            assert sha(data) == BOUNDS_FRAMES and run['sram_sha256'] == BOUNDS_SRAM
        else:
            ref = inputs['historical_' + str(count)]
            equal(data, ref, name + ' historical frames')
            if key != 'A':
                equal(data, control_frames[count], name + ' corrected baseline frames')
            else:
                control_frames[count] = data
            run['callbacks'] = len(rows(folder/'frames.csv'))
            assert run['callbacks'] == count
            if capture:
                run['semantics'] = semantic(key, folder/'provenance.csv', count)
                provenance = (folder/'provenance.csv').read_bytes()
                ref_key = {'001':'historical_bg', '002':'historical_obj', '003':'historical_composition'}[key]
                equal(provenance, inputs[ref_key], name + ' historical provenance')
                run['provenance_sha256'] = sha(provenance)
                run['provenance_summary_sha256'] = sha((folder/'provenance.csv.summary.txt').read_bytes())
        run['status'] = 'PASSED'
        save()
        print('PASS ' + name + ' frames=' + run['csv_sha256'], flush=True)

    try:
        if not reused_controls:
            execute('A', 'A-600', 600)
            execute('A', 'A-1800', 1800)
            execute('A', 'A-bounds', 16, bounds=True)
        for key, count in [('001',600), ('002',600), ('003',1800)]:
            execute(key, key+'-B', count)
            execute(key, key+'-C', count, capture=True)
            execute(key, key+'-bounds', 16, bounds=True)
    except Exception as error:
        result['status'] = 'STOPPED'
        result['first_failure'] = str(error)
        save()
        raise
    result['status'] = 'ALL_TRANSFERS_PASSED'
    save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for name in [*EXPECTED, 'baseline', 'exp001', 'exp002', 'exp003', 'dll_dir', 'output']:
        parser.add_argument('--'+name.replace('_','-'), type=Path, required=True)
    for count in (600, 1800):
        parser.add_argument('--control-' + str(count), type=Path,
                            help='Reuse a previously verified corrected-control CSV; requires both CSVs and an already satisfied control/bounds prerequisite')
    main(parser.parse_args())
