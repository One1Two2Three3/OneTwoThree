from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)
DATABASE = 'esports_team.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        players = conn.execute('SELECT * FROM players').fetchall()
        conn.close()
        return render_template('index.html', players=players)
    except Exception as e:
        return f"<h3>เกิดข้อผิดพลาด: {str(e)}</h3>"

# API ดึงสถิติเวอร์ชันอัจฉริยะ ป้องกันการดึงคอลัมน์ที่ไม่มีอยู่จริงแล้วหน้าเว็บค้าง
@app.route('/api/player_stats/<int:player_id>')
def get_player_stats(player_id):
    try:
        conn = get_db_connection()
        # ใช้ SELECT * เพื่อดึงคอลัมน์เท่าที่มีอยู่จริงในฐานข้อมูลปัจจุบันมาดู
        stats_row = conn.execute(
            '''SELECT * FROM player_stats 
               WHERE player_id = ? 
               ORDER BY stat_id DESC LIMIT 1''', 
            (player_id,)
        ).fetchone()
        conn.close()

        if stats_row:
            # แปลงข้อมูลเป็นรูปแบบ Dictionary เพื่อความปลอดภัยในการเช็กชื่อคอลัมน์
            stats = dict(stats_row)
            
            # 1. เช็กค่า Kills และ ACS (ถ้ามีในตารางดึงมาโชว์เลย)
            kills = stats.get('kills', 0)
            acs = stats.get('acs', 0)
            
            # 2. เช็กค่า K/D Ratio (ถ้ายังไม่มีคอลัมน์นี้ใน DB Browser ให้ใส่ 0.00 รอไว้ก่อน)
            if 'kd_ratio' in stats and stats['kd_ratio'] is not None:
                kd_ratio = f"{stats['kd_ratio']:.2f}"
            else:
                kd_ratio = "0.00"
                
            # 3. เช็กค่า Headshot % (ถ้ายังไม่มีคอลัมน์นี้ใน DB Browser ให้ใส่ 0.0% รอไว้ก่อน)
            if 'headshot_pct' in stats and stats['headshot_pct'] is not None:
                headshot = f"{stats['headshot_pct']}%"
            else:
                headshot = "0.0%"

            return jsonify({
                'success': True,
                'kills': kills,
                'acs': acs,
                'kd_ratio': kd_ratio,
                'headshot': headshot
            })
            
    except Exception as e:
        print("เกิดข้อผิดพลาดเบื้องหลัง:", e)
    
    return jsonify({
        'success': True,
        'kills': 0, 'acs': 0, 'kd_ratio': '0.00', 'headshot': '0.0%'
    })

if __name__ == '__main__':
    app.run(debug=True)