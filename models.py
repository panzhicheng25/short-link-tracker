import sqlite3
import os
from config import DATABASE

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS links (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code  TEXT UNIQUE NOT NULL,
            title       TEXT DEFAULT '',
            original_url TEXT NOT NULL,
            total_clicks INTEGER DEFAULT 0,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS clicks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            link_id     INTEGER NOT NULL,
            ip_address  TEXT DEFAULT '',
            country     TEXT DEFAULT '',
            region      TEXT DEFAULT '',
            city        TEXT DEFAULT '',
            user_agent  TEXT DEFAULT '',
            browser     TEXT DEFAULT '',
            os          TEXT DEFAULT '',
            device      TEXT DEFAULT '',
            referrer    TEXT DEFAULT '',
            clicked_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (link_id) REFERENCES links(id)
        );
        CREATE INDEX IF NOT EXISTS idx_clicks_link_id ON clicks(link_id);
        CREATE INDEX IF NOT EXISTS idx_clicks_clicked_at ON clicks(clicked_at);
    """)
    conn.commit()
    conn.close()

# ========== 链接操作 ==========

def create_link(short_code, original_url, title=""):
    conn = get_db()
    conn.execute("INSERT INTO links (short_code, original_url, title) VALUES (?, ?, ?)",
                 (short_code, original_url, title))
    conn.commit()
    link_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return link_id

def get_link_by_code(short_code):
    conn = get_db()
    row = conn.execute("SELECT * FROM links WHERE short_code = ?", (short_code,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_links():
    conn = get_db()
    rows = conn.execute("SELECT * FROM links ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_link_by_id(link_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM links WHERE id = ?", (link_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def delete_link(link_id):
    conn = get_db()
    conn.execute("DELETE FROM clicks WHERE link_id = ?", (link_id,))
    conn.execute("DELETE FROM links WHERE id = ?", (link_id,))
    conn.commit()
    conn.close()

def increment_clicks(link_id):
    conn = get_db()
    conn.execute("UPDATE links SET total_clicks = total_clicks + 1 WHERE id = ?", (link_id,))
    conn.commit()
    conn.close()

# ========== 点击操作 ==========

def record_click(link_id, ip_address, country, region, city,
                 user_agent, browser, os_name, device, referrer):
    conn = get_db()
    conn.execute("""
        INSERT INTO clicks (link_id, ip_address, country, region, city,
                           user_agent, browser, os, device, referrer)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (link_id, ip_address, country, region, city,
          user_agent, browser, os_name, device, referrer))
    conn.commit()
    conn.close()

def get_clicks_by_link(link_id, limit=200):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM clicks WHERE link_id = ? ORDER BY clicked_at DESC LIMIT ?",
        (link_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_click_stats(link_id):
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) as c FROM clicks WHERE link_id = ?", (link_id,)).fetchone()["c"]
    countries = conn.execute("""
        SELECT country, COUNT(*) as c FROM clicks WHERE link_id = ? AND country != ''
        GROUP BY country ORDER BY c DESC""", (link_id,)).fetchall()
    devices = conn.execute("""
        SELECT device, COUNT(*) as c FROM clicks WHERE link_id = ? AND device != ''
        GROUP BY device ORDER BY c DESC""", (link_id,)).fetchall()
    browsers = conn.execute("""
        SELECT browser, COUNT(*) as c FROM clicks WHERE link_id = ? AND browser != ''
        GROUP BY browser ORDER BY c DESC""", (link_id,)).fetchall()
    referrers = conn.execute("""
        SELECT referrer, COUNT(*) as c FROM clicks WHERE link_id = ? AND referrer != ''
        GROUP BY referrer ORDER BY c DESC""", (link_id,)).fetchall()
    conn.close()
    return {
        "total": total,
        "countries": [dict(r) for r in countries],
        "devices": [dict(r) for r in devices],
        "browsers": [dict(r) for r in browsers],
        "referrers": [dict(r) for r in referrers],
    }

def get_overview_stats():
    conn = get_db()
    total_links = conn.execute("SELECT COUNT(*) as c FROM links").fetchone()["c"]
    total_clicks = conn.execute("SELECT SUM(total_clicks) as c FROM links").fetchone()["c"] or 0
    today_clicks = conn.execute("""
        SELECT COUNT(*) as c FROM clicks WHERE date(clicked_at) = date('now', 'localtime')
    """).fetchone()["c"]
    daily = conn.execute("""
        SELECT date(clicked_at) as day, COUNT(*) as c FROM clicks
        WHERE clicked_at >= date('now', '-7 days', 'localtime')
        GROUP BY day ORDER BY day""").fetchall()
    top_links = conn.execute("""
        SELECT l.id, l.short_code, l.title, l.total_clicks FROM links l
        ORDER BY l.total_clicks DESC LIMIT 10""").fetchall()
    countries = conn.execute("""
        SELECT country, COUNT(*) as c FROM clicks WHERE country != ''
        GROUP BY country ORDER BY c DESC LIMIT 20""").fetchall()
    conn.close()
    return {
        "total_links": total_links,
        "total_clicks": total_clicks,
        "today_clicks": today_clicks,
        "daily_trend": [dict(r) for r in daily],
        "top_links": [dict(r) for r in top_links],
        "countries": [dict(r) for r in countries],
    }

# ========== 批量创建 ==========

def batch_create_links(urls):
    """批量创建短链，urls是一个纯链接字符串列表"""
    import time
    results = []
    conn = get_db()
    for url in urls:
        url = url.strip()
        if not url:
            continue
        temp_id = int(time.time() * 1000000) % 1000000000
        # 从utils导入encode
        from utils.short_code import encode
        short_code = encode(temp_id)
        try:
            conn.execute(
                "INSERT INTO links (short_code, original_url, title) VALUES (?, ?, ?)",
                (short_code, url, '')
            )
            lid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            results.append({"id": lid, "short_code": short_code, "title": "", "original_url": url, "total_clicks": 0})
        except:
            # 碰撞则重试
            short_code = encode(temp_id + 999999)
            conn.execute(
                "INSERT INTO links (short_code, original_url, title) VALUES (?, ?, ?)",
                (short_code, url, '')
            )
            lid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            results.append({"id": lid, "short_code": short_code, "title": "", "original_url": url, "total_clicks": 0})
        time.sleep(0.001)  # 避免毫秒碰撞
    conn.commit()
    conn.close()
    return results

def batch_generate_links(links_data):
    """批量生成短链，links_data=[{title, original_url}, ...]，带剧名"""
    import time
    results = []
    conn = get_db()
    for item in links_data:
        original_url = item.get("original_url", "").strip()
        title = item.get("title", "").strip()
        if not original_url:
            continue
        temp_id = int(time.time() * 1000000) % 1000000000
        from utils.short_code import encode
        short_code = encode(temp_id)
        try:
            conn.execute(
                "INSERT INTO links (short_code, original_url, title) VALUES (?, ?, ?)",
                (short_code, original_url, title)
            )
            lid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            results.append({"id": lid, "short_code": short_code, "title": title,
                           "original_url": original_url, "total_clicks": 0})
        except:
            short_code = encode(temp_id + 999999)
            conn.execute(
                "INSERT INTO links (short_code, original_url, title) VALUES (?, ?, ?)",
                (short_code, original_url, title)
            )
            lid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            results.append({"id": lid, "short_code": short_code, "title": title,
                           "original_url": original_url, "total_clicks": 0})
        time.sleep(0.001)
    conn.commit()
    conn.close()
    return results


# ========== 列表增强 ==========

def get_all_links_with_last_click():
    """获取所有链接及其最近点击时间"""
    conn = get_db()
    rows = conn.execute("""
        SELECT l.*, 
               (SELECT MAX(clicked_at) FROM clicks c WHERE c.link_id = l.id) as last_click_at
        FROM links l ORDER BY l.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ========== 导出函数 ==========

def export_clicks_by_link(link_id):
    """导出某链接的所有点击明细"""
    conn = get_db()
    link = conn.execute("SELECT * FROM links WHERE id = ?", (link_id,)).fetchone()
    clicks = conn.execute("""
        SELECT clicked_at, country, region, city, device, browser, os, referrer
        FROM clicks WHERE link_id = ? ORDER BY clicked_at DESC
    """, (link_id,)).fetchall()
    conn.close()
    return {
        "link": dict(link) if link else {},
        "clicks": [dict(r) for r in clicks]
    }


def export_clicks_by_time(start_date, end_date):
    """导出时间范围内的所有点击"""
    conn = get_db()
    rows = conn.execute("""
        SELECT l.short_code, l.title, l.original_url,
               c.clicked_at, c.country, c.region, c.city,
               c.device, c.browser, c.os, c.referrer
        FROM clicks c
        JOIN links l ON c.link_id = l.id
        WHERE date(c.clicked_at) BETWEEN ? AND ?
        ORDER BY c.clicked_at DESC
    """, (start_date, end_date)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
