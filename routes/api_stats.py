from flask import Blueprint, jsonify, request, Response
from models import get_click_stats, get_overview_stats, export_clicks_by_time
from io import BytesIO
from openpyxl import Workbook

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/api/stats/overview', methods=['GET'])
def overview():
    return jsonify(get_overview_stats())

@stats_bp.route('/api/stats/<int:link_id>', methods=['GET'])
def link_stats(link_id):
    return jsonify(get_click_stats(link_id))

@stats_bp.route('/api/stats/export', methods=['GET'])
def export_stats():
    """按时间范围导出所有点击数据为 Excel"""
    start = request.args.get('start', '')
    end = request.args.get('end', '')
    if not start or not end:
        return jsonify({"error": "start and end date required"}), 400

    rows = export_clicks_by_time(start, end)

    wb = Workbook()
    ws = wb.active
    ws.title = "点击数据"
    ws.append(['短码', '剧名', '原始链接', '点击时间', '国家', '省份/州',
               '城市', '设备', '浏览器', '操作系统', '来源'])
    for r in rows:
        ws.append([
            r.get('short_code', ''), r.get('title', ''), r.get('original_url', ''),
            r.get('clicked_at', ''), r.get('country', ''), r.get('region', ''),
            r.get('city', ''), r.get('device', ''), r.get('browser', ''),
            r.get('os', ''), r.get('referrer', '')
        ])

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return Response(output.getvalue(),
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    headers={'Content-Disposition': f'attachment; filename=export_{start}_{end}.xlsx'})
