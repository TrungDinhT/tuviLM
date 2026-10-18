from __future__ import annotations

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest
import yaml

from src.cli.strength_weakness_report import (
    common_profiles, complete_total, diversity, read_report, reviewed_weaknesses,
)
from src.cli.view import build_streamlit_command, parse_report_yaml


IDS = ['lap_luan_logic', 'nghien_cuu_chuyen_sau']


def document(model='test-model', *, reverse=False):
    rows = []
    for i, gender in enumerate(['male', 'female']):
        rows.append({
            'profile': {'name': 'Khanh', 'birth_date': '1998-04-04', 'birth_time': 8, 'gender': gender},
            'output': {'tong_quan': f'Overview {gender}',
                'diem_manh': [{'nang_luc_id': x, 'mo_ta': f'Strength {gender}', 'giai_thich': 'Evidence'} for x in IDS],
                'diem_yeu': [{'ten': f'Weakness {gender}', 'loai': 'qua_da', 'mo_ta': 'Description', 'giai_thich': 'Reason'}]},
            'metrics': {'duration_seconds': 10 + i, 'input_tokens': 12345 + i, 'output_tokens': 200, 'thinking_tokens': 100, 'total_tokens': 12545+i},
        })
    return {'workflow': 'strength_weakness', 'model': model, 'results': list(reversed(rows)) if reverse else rows,
            'metrics': {'duration_seconds': 22}, 'summary': {'succeeded': 2, 'failed': 0}}


def report(doc=None):
    return read_report(yaml.safe_dump(doc or document()).encode(), 'test.yaml')


def _run_app(directory, annotation):
    from pathlib import Path
    from src.cli.view import streamlit_main
    streamlit_main((), report_dir=Path(directory), annotation_path=Path(annotation))


def setup_app(tmp_path, docs):
    for i, doc in enumerate(docs):
        (tmp_path / f'strength_weakness_{i}.yaml').write_text(yaml.safe_dump(doc))
    annotation = tmp_path / 'annotations.json'
    annotation.write_text('{}')
    return AppTest.from_function(_run_app, args=(str(tmp_path), str(annotation)), default_timeout=15)


def test_parse_rejects_invalid_yaml_and_wrong_workflow():
    with pytest.raises(ValueError, match='Invalid YAML report'):
        parse_report_yaml('output: [unterminated')
    with pytest.raises(ValueError, match='strength_weakness'):
        read_report(b'workflow: other', 'other.yaml')


def test_streamlit_command_forwards_server_options_and_report_path(tmp_path):
    path = tmp_path / 'report.yaml'
    assert build_streamlit_command(path, port=8765, address='127.0.0.1', headless=True, executable='python-test') == [
        'python-test', '-m', 'streamlit', 'run', '--server.port', '8765', '--server.address', '127.0.0.1',
        '--server.headless', 'true', str(Path('src/cli/view.py').resolve()), '--', str(path.resolve())]


def test_profile_identity_cohort_and_missing_usage():
    first = report()
    second_doc = document(reverse=True)
    second_doc['results'][0]['error'] = 'Failed'
    second = report(second_doc)
    common = common_profiles([first, second])
    assert len(first.rows) == 2  # Same name and birth hour, different people.
    assert common == [next(iter(first.rows))]
    assert 'output' not in next(iter(second.rows.values()))
    assert complete_total([{'metrics': {'input_tokens': 0}}], 'input_tokens') == 0
    for value in [None, -1, float('nan'), float('inf'), True]:
        assert complete_total([{'metrics': {'input_tokens': 5}}, {'metrics': {'input_tokens': value}}], 'input_tokens') is None
    assert complete_total([], 'input_tokens') is None
    assert common_profiles([first, report(document(reverse=True))]) == list(first.rows)


def test_duplicate_profiles_and_invalid_output_are_rejected():
    doc = document()
    doc['results'].append(doc['results'][0])
    with pytest.raises(ValueError, match='trùng định danh'):
        report(doc)
    doc = document()
    doc['results'][0]['output']['diem_manh'][0]['nang_luc_id'] = 'invented'
    with pytest.raises(ValueError, match='output không hợp lệ'):
        report(doc)


def test_exact_two_normalization_and_edge_cases():
    # First person has 3 findings but only 2 labels. Second has 2 unique labels.
    m = diversity([['A', 'A', 'B'], ['B', 'C']])
    assert m['unique'] == 3
    assert m['within'] == 2
    assert m['jaccard'] == pytest.approx(1/3)
    assert m['equal_two_unique'] == pytest.approx(3)
    assert m['equal_two_within'] == pytest.approx(11/6)
    # First: {A} with p=1/3, {A,B} with p=2/3; second {B,C}.
    assert m['equal_two_jaccard'] == pytest.approx(2/9)
    assert diversity([['A'], ['A', 'B']])['equal_two_unique'] is None
    assert diversity([[]])['within'] == 0
    assert diversity([[]])['jaccard'] is None
    assert diversity([[], []])['pairs'] == 0
    assert diversity([])['within'] is None
    assert diversity([['A', 'B']])['equal_two_jaccard'] is None
    assert diversity([['A', 'B'], ['A', 'B']])['equal_two_jaccard'] == 1


def test_weakness_annotations_require_hash_identity_and_titles():
    r = report()
    profiles = [{'profile': row['profile'], 'weaknesses': [{'title': row['output']['diem_yeu'][0]['ten'], 'primary_theme': 'A'}]} for row in r.rows.values()]
    annotations = {'themes': {'A': 'Test theme'}, 'reports': {r.digest: {'model': r.model, 'profiles': profiles}}}
    assert reviewed_weaknesses(r, annotations) == {key: ['A'] for key in r.rows}
    changed = read_report(yaml.safe_dump(document()).encode() + b'\n', r.source)
    assert changed.digest != r.digest
    assert reviewed_weaknesses(changed, annotations) is None
    profiles[0]['weaknesses'][0]['title'] = 'Wrong title'
    assert reviewed_weaknesses(r, annotations) is None


def test_app_renders_comparison_and_selects_distinct_people(tmp_path):
    app = setup_app(tmp_path, [document(), document('second-model', reverse=True)]).run()
    assert not app.exception
    assert app.title[0].value == 'Điểm mạnh & điểm yếu'
    assert len(app.tabs) == 3
    assert any('2' == m.value and m.label == 'Hồ sơ chung thành công' for m in app.metric)
    text = repr([m.value for m in app.markdown])
    assert 'Overview male' in text
    assert 'Overview female' not in text
    app.selectbox[0].select(list(report().rows)[1]).run()
    assert not app.exception
    text = repr([m.value for m in app.markdown])
    assert 'Overview female' in text
    assert 'Overview male' not in text
    app.radio[0].set_value('Chủ đề điểm yếu').run()
    assert not app.exception
    assert any('chưa có bộ nhãn' in x.value for x in app.warning)


def test_app_handles_partial_empty_and_wrong_workflow(tmp_path):
    doc = document('partial')
    doc['results'][0] = {'profile': doc['results'][0]['profile'], 'error': 'Provider failed'}
    doc['results'][1].pop('metrics')
    app = setup_app(tmp_path, [document(), doc]).run()
    assert not app.exception
    assert any('Provider failed' in e.value for e in app.error)
    assert any('chưa có cùng tập' in x.value for x in app.warning)
    app.multiselect[0].set_value([]).run()
    assert not app.exception
    assert any('Chọn ít nhất' in x.value for x in app.info)


def test_app_handles_checkpoint_without_results(tmp_path):
    doc = document()
    doc['results'] = []
    app = setup_app(tmp_path, [doc]).run()
    assert not app.exception
    assert any('chưa có kết quả' in x.value for x in app.info)


def _run_path_app(path):
    from pathlib import Path
    from src.cli.view import streamlit_main
    streamlit_main((path,), report_dir=Path(path).parent)


def test_explicit_path_selects_one_report_and_other_workflow_is_rejected(tmp_path):
    path = tmp_path / 'chosen.yaml'
    path.write_text(yaml.safe_dump(document()))
    (tmp_path / 'strength_weakness_other.yaml').write_text('workflow: other')
    app = AppTest.from_function(_run_path_app, args=(str(path),), default_timeout=15).run()
    assert not app.exception
    assert len(app.multiselect[0].value) == 1
    assert any('strength_weakness' in error.value for error in app.error)
    assert any('Overview male' in element.value for element in app.markdown)
