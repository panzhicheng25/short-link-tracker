from flask import Blueprint, redirect, request, jsonify
from models import get_link_by_code, record_click, increment_clicks
from utils.geoip import get_geo
from utils.ua_parser import parse as parse_ua

redirect_bp = Blueprint('redirect', __name__)

@redirect_bp.route('/s/<short_code>')
def redirect_link(short_code):
    link = get_link_by_code(short_code)
    if not link:
        return jsonify({"error": "Link not found"}), 404

    # 获取客户端信息
    ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr) or ''
    ip = ip.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent', '')
    referrer = request.headers.get('Referer', '')

    # 解析地理信息
    geo = get_geo(ip)

    # 解析UA
    ua_info = parse_ua(user_agent)

    # 记录点击
    record_click(
        link_id=link['id'],
        ip_address=ip,
        country=geo['country'],
        region=geo['region'],
        city=geo['city'],
        user_agent=user_agent,
        browser=ua_info['browser'],
        os_name=ua_info['os'],
        device=ua_info['device'],
        referrer=referrer
    )

    # 更新总点击数
    increment_clicks(link['id'])

    # 302 跳转到原始链接
    return redirect(link['original_url'], code=302)
