"""Streamlit dashboard dedicated to strength/weakness workflow reports."""
from __future__ import annotations

import argparse
from collections.abc import Sequence
import json
from pathlib import Path
from statistics import median
import subprocess
import sys

# Streamlit executes this file by path, including outside the repository cwd.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from src.agent.workflow.strength_weakness.ontology import GROUP_LABELS, get_capability_definition
from src.cli.strength_weakness_report import (
    Report, common_profiles, complete_total, diversity, number, overlap,
    parse_report_yaml, profile_label, read_report, reviewed_weaknesses, strength_labels,
)

LEVELS = {'Năng lực cụ thể': 'id', 'Họ năng lực': 'category', 'Nhóm năng lực': 'group'}
KINDS = {'han_che_truc_tiep': 'Hạn chế trực tiếp', 'qua_da': 'Điểm mạnh quá đà', 'xung_dot': 'Xung đột'}
TOKEN_FIELDS = {
    'input_tokens': 'Input token', 'output_tokens': 'Output token',
    'thinking_tokens': 'Thinking token', 'total_tokens': 'Tổng token',
    'cache_read_tokens': 'Cache đọc', 'cache_write_tokens': 'Cache ghi',
    'requests': 'Requests', 'tool_calls': 'Tool calls',
}


def _fmt(value: float | None, *, seconds: bool = False) -> str:
    if value is None:
        return '—'
    return f'{value:,.1f} s' if seconds else f'{value:,.0f}'


def _label(value: str, level: str, themes: dict) -> str:
    if level == 'id':
        return get_capability_definition(value).label
    if level == 'group':
        return GROUP_LABELS.get(value, value)
    if level == 'weakness':
        return themes.get(value, value)
    return value


def _performance(reports: list[Report], cohort: list) -> pd.DataFrame:
    records = []
    for report in reports:
        rows = [report.successful[key] for key in cohort]
        duration = complete_total(rows, 'duration_seconds')
        durations = [number(r.get('metrics'), 'duration_seconds') for r in rows]
        records.append({
            'Model / report': report.label, 'Hồ sơ chung': len(rows),
            'Giây/người (TB)': duration / len(rows) if duration is not None else None,
            'Giây/người (median)': median(durations) if durations and all(v is not None for v in durations) else None,
            'Batch toàn bộ (giây)': number(report.document.get('metrics'), 'duration_seconds'),
            **{label: complete_total(rows, field) for field, label in TOKEN_FIELDS.items()},
        })
    return pd.DataFrame(records)


def _diversity_table(reports: list[Report], cohort: list, level: str, annotations: dict) -> tuple[pd.DataFrame, dict]:
    records, details = [], {}
    for i, report in enumerate(reports):
        reviewed = reviewed_weaknesses(report, annotations) if level == 'weakness' else None
        if level == 'weakness' and reviewed is None:
            records.append({'Model / report': report.label, 'Nhãn đã review': False})
            continue
        lists = [reviewed[key] if reviewed is not None else strength_labels(report.successful[key], level) for key in cohort]
        metrics = diversity(lists)
        details[i] = (metrics, lists)
        records.append({
            'Model / report': report.label, 'Hồ sơ': len(cohort),
            'Tổng nhận định': metrics['findings'], 'Nhãn khác nhau ↑': metrics['unique'],
            'Nhãn/người ↑': metrics['within'], 'Jaccard giữa người ↓': metrics['jaccard'],
            'Nhãn khác nhau (2 ý) ↑': metrics['equal_two_unique'],
            'Nhãn/người (2 ý) ↑': metrics['equal_two_within'],
            'Jaccard (2 ý) ↓': metrics['equal_two_jaccard'],
            'Đủ ≥2 ý': metrics['equal_two_eligible'],
            'Tỷ trọng top 3 nhãn ↓': metrics['top_three_share'],
            'Cặp có dữ liệu': metrics['pairs'],
            'Cặp cùng tập nhãn': metrics['identical_pairs'],
        })
    return pd.DataFrame(records), details


def _profile_card(report: Report, key: tuple, annotations: dict) -> None:
    st.subheader(report.model)
    st.caption(report.source)
    row = report.rows.get(key)
    if row is None:
        st.info('Report này không có hồ sơ đã chọn.')
        return
    columns = st.columns(4)
    for column, (field, label) in zip(columns, [
        ('duration_seconds', 'Thời gian'), ('input_tokens', 'Input'),
        ('output_tokens', 'Output'), ('thinking_tokens', 'Thinking'),
    ]):
        column.metric(label, _fmt(number(row.get('metrics'), field), seconds=field == 'duration_seconds'))
    with st.expander('Toàn bộ metric của hồ sơ'):
        st.table([{'Metric': label, 'Giá trị': _fmt(number(row.get('metrics'), field))} for field, label in TOKEN_FIELDS.items()])
    if 'output' not in row:
        st.error(str(row.get('error', 'Chưa có kết quả.')))
        return
    output = row['output']
    st.markdown('#### Tổng quan')
    st.write(output['tong_quan'])
    groups = {get_capability_definition(f['nang_luc_id']).group for f in output['diem_manh']}
    reviewed = reviewed_weaknesses(report, annotations)
    st.caption(f"{len(output['diem_manh'])} điểm mạnh · {len(groups)} nhóm năng lực · {len(output['diem_yeu'])} điểm yếu"
               + (f' · {len(set(reviewed[key]))} chủ đề điểm yếu' if reviewed is not None else ''))
    st.markdown('#### Điểm mạnh')
    if not output['diem_manh']:
        st.info('Chưa có đủ căn cứ để chọn điểm mạnh.')
    for index, finding in enumerate(output['diem_manh'], 1):
        capability = get_capability_definition(finding['nang_luc_id'])
        with st.container(border=True):
            st.markdown(f"**{index}. {capability.label}**")
            st.caption(f'{GROUP_LABELS[capability.group]} › {capability.category}')
            st.write(finding['mo_ta'])
            with st.expander('Luận giải điểm mạnh'):
                st.write(finding['giai_thich'])
    st.markdown('#### Điểm yếu')
    if not output['diem_yeu']:
        st.info('Chưa có đủ căn cứ để chọn điểm yếu.')
    for index, finding in enumerate(output['diem_yeu']):
        with st.container(border=True):
            st.markdown(f"**{index + 1}. {finding['ten'].replace('_', ' ')}**")
            st.caption(KINDS.get(finding['loai'], finding['loai']))
            if reviewed is not None:
                st.caption('Chủ đề review: ' + annotations['themes'][reviewed[key][index]])
            st.write(finding['mo_ta'])
            with st.expander('Luận giải điểm yếu'):
                st.write(finding['giai_thich'])


def _diversity_view(reports: list[Report], cohort: list, annotations: dict) -> None:
    st.subheader('Đa dạng trong một người và giữa nhiều người')
    level_name = st.radio('Phân tích theo', [*LEVELS, 'Chủ đề điểm yếu'], horizontal=True)
    level = LEVELS.get(level_name, 'weakness')
    st.caption('↑ cao hơn: nhiều nhãn hơn. ↓ thấp hơn: ít lặp lại hơn. Số liệu chỉ dùng các hồ sơ thành công chung giữa các report đã chọn.')
    table, details = _diversity_table(reports, cohort, level, annotations)
    st.dataframe(table, hide_index=True, use_container_width=True, column_config={
        'Jaccard giữa người ↓': st.column_config.NumberColumn(format='percent'),
        'Jaccard (2 ý) ↓': st.column_config.NumberColumn(format='percent'),
        'Tỷ trọng top 3 nhãn ↓': st.column_config.NumberColumn(format='percent'),
    })
    st.download_button('Tải bảng đa dạng CSV', table.to_csv(index=False).encode('utf-8-sig'), 'diversity.csv', 'text/csv')
    if level == 'weakness':
        st.info('Chủ đề điểm yếu được gán thủ công trong lần review trước và chỉ dùng khi hash report khớp. Khác tên chưa chứng minh khác ý; cùng chủ đề rộng chưa chứng minh trùng ý.')
        if len(details) != len(reports):
            st.warning('Một số report chưa có bộ nhãn review khớp: các metric điểm yếu của những report đó để trống.')
    if not details:
        return
    chart_columns = ['Nhãn khác nhau (2 ý) ↑', 'Nhãn/người (2 ý) ↑', 'Jaccard (2 ý) ↓']
    selected_metric = st.selectbox('Biểu đồ so sánh đã chuẩn hóa', chart_columns)
    chart = table[['Model / report', selected_metric]].dropna().set_index('Model / report')
    if not chart.empty:
        st.bar_chart(chart, horizontal=True)
    detail_index = st.selectbox('Xem chi tiết report', list(details), format_func=lambda i: reports[i].label)
    metrics, lists = details[detail_index]
    if metrics['equal_two_eligible'] != len(cohort):
        st.warning('Có hồ sơ dưới 2 nhận định: không tính chuẩn hóa 2 ý cho cohort này.')
    frequencies = pd.DataFrame([
        {'Nhãn': _label(label, level, annotations.get('themes', {})), 'Số người': n, 'Tỷ lệ': n / len(cohort)}
        for label, n in sorted(metrics['frequencies'].items(), key=lambda p: (-p[1], p[0]))
    ])
    st.markdown('#### Nhãn nào xuất hiện lặp lại?')
    if not frequencies.empty:
        st.bar_chart(frequencies.set_index('Nhãn')['Số người'], horizontal=True)
        st.dataframe(frequencies, hide_index=True, use_container_width=True,
                     column_config={'Tỷ lệ': st.column_config.NumberColumn(format='percent')})
    st.markdown('#### Từng người có bao nhiêu ý khác nhau?')
    st.dataframe(pd.DataFrame([
        {'Hồ sơ': profile_label(key), 'Số nhận định': len(labels), 'Nhãn khác nhau': len(set(labels)),
         'Nhãn': ' · '.join(_label(x, level, annotations.get('themes', {})) for x in sorted(set(labels)))}
        for key, labels in zip(cohort, lists)
    ]), hide_index=True, use_container_width=True)
    st.markdown('#### Mức trùng lặp giữa từng cặp người')
    labels = [profile_label(key) for key in cohort]
    matrix = pd.DataFrame([[overlap(set(a), set(b)) for b in lists] for a in lists], index=labels, columns=labels)
    heatmap = pd.DataFrame([
        {'Người A': labels[i], 'Người B': labels[j], 'Jaccard': value}
        for i, a in enumerate(lists) for j, b in enumerate(lists)
        if (value := overlap(set(a), set(b))) is not None
    ])
    if not heatmap.empty:
        st.vega_lite_chart(heatmap, {
            'mark': 'rect', 'height': max(260, 22 * len(cohort)),
            'encoding': {
                'x': {'field': 'Người A', 'type': 'nominal', 'sort': labels, 'axis': {'labelLimit': 140}},
                'y': {'field': 'Người B', 'type': 'nominal', 'sort': labels, 'axis': {'labelLimit': 200}},
                'color': {'field': 'Jaccard', 'type': 'quantitative', 'scale': {'domain': [0, 1], 'scheme': 'blues'}},
                'tooltip': [{'field': 'Người A'}, {'field': 'Người B'}, {'field': 'Jaccard', 'format': '.1%'}],
            },
        }, use_container_width=True)
    with st.expander('Bảng số liệu từng cặp'):
        st.dataframe(matrix, use_container_width=True)
    st.caption('Ma trận Jaccard gốc: 0 = không chung nhãn, 1 = cùng tập nhãn; ô trống = cả hai không có nhận định. Đường chéo không tính trong trung bình.')


def streamlit_main(argv: Sequence[str] | None = None, *, report_dir: Path | None = None,
                   annotation_path: Path | None = None) -> None:
    args = list(sys.argv[1:] if argv is None else argv)
    st.set_page_config(page_title='Điểm mạnh & điểm yếu · TuviLM', page_icon='☯', layout='wide')
    cached_read = st.cache_data(show_spinner=False)(read_report)
    st.title('Điểm mạnh & điểm yếu')
    st.caption('Đọc hồ sơ, đối chiếu model và đo mức đa dạng trên cùng tập người.')
    if len(args) > 1:
        st.error('Chỉ nhận một đường dẫn report sau dấu -- của Streamlit.')
        return
    directory = report_dir if report_dir is not None else ROOT / 'reports'
    paths = sorted(directory.glob('strength_weakness*.yaml')) + sorted(directory.glob('strength_weakness*.yml'))
    initial = Path(args[0]).resolve() if args else None
    paths = list(dict.fromkeys([*([initial] if initial else []), *(p.resolve() for p in paths)]))
    st.sidebar.header('Report so sánh')
    uploads = st.sidebar.file_uploader('Thêm report YAML', type=['yaml', 'yml'], accept_multiple_files=True)
    sources = []
    for path in paths:
        try:
            sources.append((str(path), path.name, path.read_bytes()))
        except OSError as exc:
            st.sidebar.error(f'{path.name}: {exc}')
    for i, upload in enumerate(uploads or []):
        sources.append((f'upload:{i}:{upload.name}', f'Upload {i+1}: {upload.name}', upload.getvalue()))
    if not sources:
        st.info('Chọn các report strength_weakness trong sidebar để bắt đầu. Có thể tải nhiều file cùng lúc.')
        return
    reports = []
    for _source_id, name, data in sources:
        try:
            reports.append(cached_read(data, name))
        except ValueError as exc:
            st.sidebar.error(f'{name}: {exc}')
    if not reports:
        return
    selected = st.sidebar.multiselect('Chọn model / lần chạy', range(len(reports)),
        default=[0] if initial and not uploads else list(range(len(reports))),
        format_func=lambda i: f'{i+1}. {reports[i].label}')
    reports = [reports[i] for i in selected]
    if not reports:
        st.info('Chọn ít nhất một report.')
        return
    annotation_file = annotation_path or ROOT / 'data/strength_weakness_review_annotations.json'
    try:
        annotations = json.loads(annotation_file.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        annotations = {}
        st.sidebar.caption(f'Chưa tải được nhãn review điểm yếu: {exc}')
    cohort = common_profiles(reports)
    all_keys = list(dict.fromkeys(key for r in reports for key in r.rows))
    st.sidebar.metric('Hồ sơ chung thành công', len(cohort))
    st.sidebar.caption('Đối chiếu bằng tên + ngày sinh + giờ sinh + giới tính; giữ riêng người trùng tên.')
    coverage = pd.DataFrame([{
        'Model / report': r.label, 'Đã ghi': len(r.rows), 'Thành công': len(r.successful),
        'Lỗi / chưa xong': len(r.rows) - len(r.successful),
        'Thành công ngoài tập chung': len(r.successful) - len(cohort),
        'Hoàn tất': str(r.document.get('completed_at', 'Đang chạy / không rõ')),
    } for r in reports])
    with st.expander(f'{len(reports)} report · {len(cohort)} hồ sơ chung · tình trạng dữ liệu'):
        st.dataframe(coverage, hide_index=True, use_container_width=True)
        st.caption('Report đang chạy chỉ phản ánh hồ sơ đã ghi vào checkpoint. Thiếu metric hiển thị —, không coi là 0.')
    if any(len(r.successful) != len(cohort) for r in reports):
        st.warning('Các report chưa có cùng tập hồ sơ thành công. So sánh metric chỉ dùng phần giao; số hồ sơ bị loại được hiển thị ở tình trạng dữ liệu.')
    profile_tab, comparison_tab, diversity_tab = st.tabs(['Hồ sơ từng người', 'Token & thời gian', 'So sánh độ đa dạng'])
    with profile_tab:
        if all_keys:
            key = st.selectbox('Chọn người', all_keys, format_func=profile_label)
            st.subheader(profile_label(key))
            for start in range(0, len(reports), 2):
                for column, report in zip(st.columns(min(2, len(reports) - start)), reports[start:start+2]):
                    with column:
                        _profile_card(report, key, annotations)
        else:
            st.info('Report chưa có kết quả hồ sơ.')
    with comparison_tab:
        if not cohort:
            st.info('Chưa có hồ sơ thành công chung để so sánh.')
        else:
            st.subheader(f'Token & thời gian · cùng {len(cohort)} người')
            performance = _performance(reports, cohort)
            comparison = performance.set_index('Model / report').T
            comparison.index.name = 'Metric'
            st.dataframe(comparison, use_container_width=True)
            duration_chart = performance[['Model / report', 'Giây/người (TB)']].dropna().set_index('Model / report')
            if not duration_chart.empty:
                st.bar_chart(duration_chart, horizontal=True)
            st.download_button('Tải metric CSV', performance.to_csv(index=False).encode('utf-8-sig'), 'performance.csv', 'text/csv')
            st.caption('Token là tổng trên tập chung. Thinking đã nằm trong output, không cộng lần nữa. Batch toàn bộ là thời gian thực của cả lần chạy, có thể gồm hồ sơ ngoài tập chung.')
            latency = pd.DataFrame([{'Hồ sơ': profile_label(key), **{r.label: number(r.successful[key].get('metrics'), 'duration_seconds') for r in reports}} for key in cohort]).set_index('Hồ sơ')
            st.markdown('#### Latency của từng hồ sơ (giây)')
            st.line_chart(latency)
            st.dataframe(latency, use_container_width=True)
            st.caption('Latency gồm chuẩn bị, gọi model và retry. Các batch chạy riêng; cache, provider và reasoning có thể khác nhau.')
    with diversity_tab:
        if cohort:
            _diversity_view(reports, cohort, annotations)
        else:
            st.info('Chưa có hồ sơ thành công chung để đo độ đa dạng.')
        with st.expander('Cách đọc các chỉ số'):
            st.markdown('''
- **Trong một người:** số nhãn khác nhau trung bình/người. Xem ở mức nhóm để biết các ý có trải rộng nhiều miền năng lực không.
- **Giữa nhiều người:** Jaccard = số nhãn chung / số nhãn trong hợp. Lấy trung bình trên mọi cặp người; thấp hơn nghĩa là ít trùng tập nhãn hơn.
- **Chuẩn hóa 2 ý:** kỳ vọng chính xác khi chọn ngẫu nhiên 2 nhận định gốc/người, không hoàn lại. Kiểm soát lợi thế do model viết dài; không gọi lại model. Chỉ tính khi mọi người có ít nhất 2 ý.
- **Nhãn khác nhau:** độ phong phú trên cả tập người. **Tỷ trọng top 3:** phần nhận định thuộc 3 nhãn phổ biến nhất; biểu đồ tần suất đếm số người có nhãn đó.
- Cặp cả hai rỗng bị loại khỏi Jaccard gốc. Dưới 2 người không có metric giữa người. Mỗi mức ID / họ / nhóm cho một góc nhìn, cùng nhóm chưa có nghĩa là đồng nghĩa.
- Đây là so sánh mô tả trên các lần chạy đã lưu. Đa dạng hơn chưa chứng minh luận giải chính xác hơn; không tạo điểm chất lượng tổng hợp.
''')
def build_streamlit_command(
    report_path: Path | None,
    *,
    port: int | None = None,
    address: str | None = None,
    headless: bool = False,
    executable: str | None = None,
) -> list[str]:
    """Build the subprocess command used by the report-view CLI."""
    command = [
        executable or sys.executable,
        "-m",
        "streamlit",
        "run",
    ]
    if port is not None:
        command.extend(("--server.port", str(port)))
    if address is not None:
        command.extend(("--server.address", address))
    if headless:
        command.extend(("--server.headless", "true"))
    command.append(str(Path(__file__).resolve()))
    if report_path is not None:
        command.extend(("--", str(report_path.resolve())))
    return command


def build_cli_parser(*, prog: str | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=prog,
        description="Compare strength_weakness reports, profiles, usage and diversity in Streamlit.",
    )
    parser.add_argument(
        "report",
        type=Path,
        nargs="?",
        help="Strength/weakness YAML path. Omit to compare reports/ files or upload reports.",
    )
    parser.add_argument("--port", type=int, help="Streamlit server port.")
    parser.add_argument("--address", help="Streamlit server address.")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run Streamlit without opening a browser.",
    )
    return parser


def cli_main(
    argv: Sequence[str] | None = None,
    *,
    prog: str | None = None,
) -> int:
    parser = build_cli_parser(prog=prog)
    args = parser.parse_args(argv)
    if args.report is not None and not args.report.is_file():
        parser.error(f"report file does not exist: {args.report}")
    if args.port is not None and not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")

    command = build_streamlit_command(
        args.report,
        port=args.port,
        address=args.address,
        headless=args.headless,
    )
    try:
        return subprocess.call(command)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    streamlit_main()
