import streamlit.components.v1 as components


def render_timer_and_anticheat(duration_seconds: int):
    html = f"""
    <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:16px;padding:16px 20px;display:flex;align-items:center;justify-content:space-between;border:2px solid #0f3460;font-family:sans-serif;flex-wrap:wrap;gap:10px;">
        <div style="text-align:center;min-width:80px;">
            <div style="color:#a0aec0;font-size:11px;margin-bottom:4px;text-transform:uppercase;letter-spacing:1px;">Time Left</div>
            <div id="cat-timer" style="font-size:32px;font-weight:800;color:#63b3ed;font-family:monospace;">--:--</div>
        </div>
        <div style="text-align:center;min-width:80px;">
            <div style="color:#a0aec0;font-size:11px;margin-bottom:4px;text-transform:uppercase;letter-spacing:1px;">Status</div>
            <div id="cat-status" style="font-size:13px;font-weight:700;color:#68d391;background:rgba(104,211,145,0.1);padding:5px 14px;border-radius:20px;">Active</div>
        </div>
        <div style="text-align:center;min-width:80px;">
            <div style="color:#a0aec0;font-size:11px;margin-bottom:4px;text-transform:uppercase;letter-spacing:1px;">Tab Switches</div>
            <div id="cat-violations" style="font-size:32px;font-weight:800;color:#fc8181;">0</div>
        </div>
        <div style="text-align:center;min-width:80px;">
            <div style="color:#a0aec0;font-size:11px;margin-bottom:4px;text-transform:uppercase;letter-spacing:1px;">Integrity</div>
            <div id="cat-integrity" style="font-size:13px;font-weight:700;color:#68d391;background:rgba(104,211,145,0.1);padding:5px 14px;border-radius:20px;">100%</div>
        </div>
    </div>
    <div id="cat-warning" style="display:none;background:linear-gradient(135deg,#fc8181,#f56565);color:white;padding:12px 20px;border-radius:10px;margin-top:8px;font-weight:700;font-size:15px;text-align:center;font-family:sans-serif;">
        TAB SWITCH DETECTED — This violation has been recorded!
    </div>
    <script>
        var catTimeLeft = {duration_seconds};
        var catViolations = 0;
        function catUpdateTimer() {{
            var mins = Math.floor(catTimeLeft / 60);
            var secs = catTimeLeft % 60;
            var el = document.getElementById('cat-timer');
            if (el) {{
                el.textContent = mins + ':' + (secs < 10 ? '0' : '') + secs;
                if (catTimeLeft <= 60) el.style.color = '#fc8181';
            }}
            if (catTimeLeft <= 0) {{
                if (el) el.textContent = '0:00';
                clearInterval(catInterval);
            }}
            catTimeLeft--;
        }}
        catUpdateTimer();
        var catInterval = setInterval(catUpdateTimer, 1000);
        document.addEventListener('visibilitychange', function() {{
            if (document.hidden) {{
                catViolations++;
                var vEl = document.getElementById('cat-violations');
                if (vEl) vEl.textContent = catViolations;
                var integrity = Math.max(0, 100 - (catViolations * 15));
                var iEl = document.getElementById('cat-integrity');
                if (iEl) {{
                    iEl.textContent = integrity + '%';
                    if (integrity < 70) {{ iEl.style.color = '#fc8181'; iEl.style.background = 'rgba(252,129,129,0.1)'; }}
                    else if (integrity < 85) {{ iEl.style.color = '#f6ad55'; iEl.style.background = 'rgba(246,173,85,0.1)'; }}
                }}
                var sEl = document.getElementById('cat-status');
                if (sEl) {{ sEl.textContent = 'Violation!'; sEl.style.color = '#fc8181'; sEl.style.background = 'rgba(252,129,129,0.1)'; }}
                var wEl = document.getElementById('cat-warning');
                if (wEl) wEl.style.display = 'block';
                setTimeout(function() {{
                    if (wEl) wEl.style.display = 'none';
                    if (sEl) {{ sEl.textContent = 'Active'; sEl.style.color = '#68d391'; sEl.style.background = 'rgba(104,211,145,0.1)'; }}
                }}, 3000);
            }}
        }});
    </script>
    """
    components.html(html, height=110)