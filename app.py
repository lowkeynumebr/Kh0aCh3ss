import json
import random
from flask import Flask, request, jsonify, render_template_string
from curl_cffi import requests as crequests

app = Flask(__name__)

# Danh sách 3 proxy HTTP của bạn
PROXY_LIST = [
    "http://pilcikkg:esenmppky29k@198.23.243.226:6361",
    "http://pilcikkg:esenmppky29k@38.154.185.97:6370",
    "http://pilcikkg:esenmppky29k@191.96.254.138:6185"
]

proxy_index = 0

def get_next_proxy():
    global proxy_index
    proxy = PROXY_LIST[proxy_index]
    proxy_index = (proxy_index + 1) % len(PROXY_LIST)
    return proxy

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cờ Vua AI - Flexible Gateway</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/chessboard-js/1.0.0/chessboard-1.0.0.min.css">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
body { background: #0f172a; color: #f8fafc; min-height: 100vh; display: flex; flex-direction: column; align-items: center; padding: 10px; }
.container { max-width: 480px; width: 100%; display: flex; flex-direction: column; gap: 12px; }
.card { background: #1e293b; border-radius: 12px; padding: 12px; border: 1px solid #334155; }
#board { width: 100%; aspect-ratio: 1/1; margin: 0 auto; }
h1 { font-size: 1.1rem; text-align: center; color: #38bdf8; margin-bottom: 8px; }
.form-group { margin-bottom: 8px; }
label { display: block; font-size: 0.75rem; margin-bottom: 2px; color: #94a3b8; }
input, select, button { width: 100%; padding: 7px 10px; border-radius: 6px; border: 1px solid #334155; background: #0f172a; color: #fff; font-size: 0.8rem; }
.row { display: flex; gap: 6px; }
button { background: #0284c7; font-weight: bold; cursor: pointer; margin-top: 4px; border: none; }
button:hover { opacity: 0.9; }
.btn-success { background: #16a34a !important; }
.btn-danger { background: #dc2626 !important; }
.btn-secondary { background: #475569 !important; font-size: 0.75rem; padding: 5px 8px; margin-top: 4px; }
.status-box { margin-top: 6px; padding: 6px; background: #0f172a; border-radius: 6px; border: 1px solid #334155; font-size: 0.75rem; font-weight: bold; color: #38bdf8; }
.log-header { display: flex; justify-content: space-between; align-items: center; margin-top: 6px; margin-bottom: 2px; }
.log-header span { font-size: 0.75rem; font-weight: bold; color: #94a3b8; }
.log-box { height: 140px; overflow-y: auto; background: #020617; border-radius: 6px; border: 1px solid #334155; padding: 6px; font-family: 'Courier New', Courier, monospace; font-size: 0.7rem; color: #38bdf8; white-space: pre-wrap; word-break: break-all; }
.highlight-square { background-color: rgba(255, 255, 0, 0.4) !important; }
.highlight-hint { background: radial-gradient(circle, rgba(16, 185, 129, 0.7) 28%, transparent 28%) !important; }
</style>
</head>
<body>

<div class="container">
    <h1>Cờ Vua AI - Gateway</h1>
    <div class="card"><div id="board"></div></div>
    <div class="card">
        <div class="form-group">
            <label>API Endpoint (Dán đầy đủ URL chat completions)</label>
            <input type="text" id="apiEndpoint" placeholder="https://api.provider.com/v1/chat/completions" value="https://tabitoken.com/v1/chat/completions">
        </div>
        <div class="row">
            <div class="form-group" style="flex: 2;">
                <label>API Key</label>
                <input type="password" id="apiKey" placeholder="Dán API Key...">
            </div>
            <div class="form-group" style="flex: 1;">
                <label>Auth Type</label>
                <select id="authType">
                    <option value="Bearer">Bearer</option>
                    <option value="x-api-key">x-api-key</option>
                </select>
            </div>
        </div>
        <div class="form-group">
            <label>Tên Model AI (Có thể tự gõ hoặc bấm Lấy danh sách)</label>
            <input type="text" id="modelInput" placeholder="vd: claude-opus-5, gpt-4o, ..." value="claude-opus-5">
        </div>
        <div class="row">
            <button class="btn-success" onclick="fetchModels()" style="flex: 1;">Lấy danh sách Model</button>
            <button onclick="testConnection()" style="flex: 1; background: #0d9488;">Test Connect</button>
        </div>
        <div class="row" style="margin-top: 6px;">
            <div class="form-group" style="flex: 1;">
                <label>Bạn cầm quân</label>
                <select id="playerColor">
                    <option value="w">Trắng</option>
                    <option value="b">Đen</option>
                </select>
            </div>
        </div>
        <button id="startBtn" onclick="startGame()">Bắt Đầu Ván Mới</button>
        <button id="stopBtn" class="btn-danger" onclick="stopGame()" style="display: none;">Dừng Trận Đấu</button>
        <div class="status-box" id="statusBox">Trạng thái: Sẵn sàng</div>
        <div class="log-header">
            <span>DEBUG LOG</span>
            <div>
                <button class="btn-secondary" onclick="copyLog()">Copy</button>
                <button class="btn-secondary" onclick="clearLog()">Xóa</button>
            </div>
        </div>
        <div class="log-box" id="logBox"></div>
    </div>
</div>

<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/chess.js/0.10.3/chess.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/chessboard-js/1.0.0/chessboard-1.0.0.min.js"></script>
<script>
let board = null;
let game = new Chess();
let isRunning = false;
let aiTimeout = null;
let selectedSquare = null;

function chessDotComPieceTheme(piece) {
    const color = piece.charAt(0);
    const type = piece.charAt(1).toLowerCase();
    return `https://images.chesscomfiles.com/chess-themes/pieces/neo/150/${color}${type}.png`;
}

function log(type, msg) {
    const time = new Date().toLocaleTimeString();
    const logBox = $('#logBox');
    logBox.append(`[${time}] [${type}] ${msg}\\n`);
    logBox.scrollTop(logBox[0].scrollHeight);
}

function clearLog() { $('#logBox').empty(); }
function copyLog() { navigator.clipboard.writeText($('#logBox').text()).then(() => alert('Đã copy Log!')); }
function updateStatus(msg) { $('#statusBox').text('Trạng thái: ' + msg); }
function removeHighlights() { $('#board .square-55d63').removeClass('highlight-square highlight-hint'); }

function getRequestConfig() {
    let endpoint = $('#apiEndpoint').val().trim();
    let apiKey = $('#apiKey').val().trim();
    let authType = $('#authType').val();
    let model = $('#modelInput').val().trim();
    return { endpoint, apiKey, authType, model };
}

async function fetchModels() {
    let cfg = getRequestConfig();
    if (!cfg.apiKey || !cfg.endpoint) { alert('Vui lòng nhập API Key và Endpoint!'); return; }
    
    log('SYS', 'Đang quét danh sách model từ server...');

    try {
        const res = await fetch('/api/models', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                target_endpoint: cfg.endpoint,
                api_key: cfg.apiKey,
                auth_type: cfg.authType
            })
        });
        const data = await res.json();
        if (res.ok && data.data) {
            let modelIds = data.data.map(m => m.id);
            log('SUCCESS', `Tìm thấy ${modelIds.length} models: ${modelIds.slice(0, 5).join(', ')}...`);
            // Điền model đầu tiên tìm được vào ô model hoặc hiển thị thông báo
            if (modelIds.length > 0) {
                $('#modelInput').val(modelIds[0]);
                alert(`Đã lấy thành công! Model đầu tiên được tự điền: ${modelIds[0]}`);
            }
        } else {
            throw new Error(data.error || 'Không thể đọc danh sách model');
        }
    } catch (err) {
        log('ERROR', `Lỗi lấy models: ${err.message}`);
        alert('Lỗi: ' + err.message);
    }
}

async function testConnection() {
    let cfg = getRequestConfig();
    if (!cfg.apiKey || !cfg.endpoint) { alert('Nhập đủ API Key và Endpoint!'); return; }
    log('SYS', 'Đang test kết nối qua Proxy Gateway...');

    try {
        const res = await fetch('/api/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                target_endpoint: cfg.endpoint,
                api_key: cfg.apiKey,
                auth_type: cfg.authType,
                model: cfg.model
            })
        });
        const text = await res.text();
        if (res.ok) {
            log('SUCCESS', 'Kết nối thành công qua Proxy!');
            alert('Kết nối thành công!');
        } else {
            log('ERROR', `Test thất bại: ${text}`);
            alert('Kết nối thất bại: ' + text);
        }
    } catch (err) {
        log('ERROR', `Lỗi kết nối: ${err.message}`);
        alert('Lỗi: ' + err.message);
    }
}

function handleSquareClick(square) {
    if (!isRunning || game.game_over()) return;
    const playerColor = $('#playerColor').val();
    if ((game.turn() === 'w' && playerColor !== 'w') || (game.turn() === 'b' && playerColor !== 'b')) return;

    if (selectedSquare === null) {
        const piece = game.get(square);
        if (piece && piece.color === playerColor) {
            selectedSquare = square;
            removeHighlights();
            $('#board .square-' + square).addClass('highlight-square');
            game.moves({ square: square, verbose: true }).forEach(m => $('#board .square-' + m.to).addClass('highlight-hint'));
        }
    } else {
        const move = game.move({ from: selectedSquare, to: square, promotion: 'q' });
        removeHighlights();
        selectedSquare = null;
        if (move !== null) {
            board.position(game.fen());
            log('MOVE', `Bạn đi: ${move.san}`);
            if (isRunning && !game.game_over()) setTimeout(triggerAiMove, 300);
        } else {
            const piece = game.get(square);
            if (piece && piece.color === playerColor) handleSquareClick(square);
        }
    }
}

function startGame() {
    let cfg = getRequestConfig();
    if (!cfg.apiKey) { alert('Vui lòng nhập API Key!'); return; }
    if (!cfg.endpoint) { alert('Vui lòng nhập Endpoint!'); return; }
    if (!cfg.model) { alert('Vui lòng nhập tên Model!'); return; }

    game.reset();
    isRunning = true;
    selectedSquare = null;
    removeHighlights();

    const playerColor = $('#playerColor').val();
    board.orientation(playerColor === 'b' ? 'black' : 'white');
    board.position(game.fen());
    board.resize();

    $('#startBtn').hide();
    $('#stopBtn').show();
    clearLog();
    log('SYSTEM', '--- Bắt đầu ván đấu ---');
    updateStatus('Đang trong trận đấu');

    if (playerColor === 'b') triggerAiMove();
}

function stopGame() {
    isRunning = false;
    if (aiTimeout) clearTimeout(aiTimeout);
    removeHighlights();
    selectedSquare = null;
    $('#startBtn').show();
    $('#stopBtn').hide();
    log('SYSTEM', 'Đã dừng ván đấu');
    updateStatus('Đã dừng');
}

async function triggerAiMove() {
    if (!isRunning || game.game_over()) return;
    let cfg = getRequestConfig();

    updateStatus(`AI (${cfg.model}) đang suy nghĩ...`);
    const possibleMoves = game.moves();
    const promptText = `Trạng thái FEN: "${game.fen()}". Nước hợp lệ: [${possibleMoves.join(', ')}]. Chọn 1 nước đi tốt nhất dạng SAN (vd: e4, Nf3). Chỉ trả lời duy nhất mã nước đi.`;

    log('API_REQ', `Model: ${cfg.model} | Gửi request qua Proxy...`);

    try {
        const payload = {
            model: cfg.model,
            messages: [{ role: 'user', content: promptText }],
            temperature: 0.2,
            target_endpoint: cfg.endpoint,
            api_key: cfg.apiKey,
            auth_type: cfg.authType
        };

        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const text = await res.text();
        if (!res.ok) throw new Error(`HTTP ${res.status}: ${text}`);

        const data = JSON.parse(text);
        let aiMoveStr = data.choices[0].message.content.trim().replace(/['"`]/g, '');
        
        let move = game.move(aiMoveStr);
        if (!move) {
            const match = possibleMoves.find(m => m.toLowerCase() === aiMoveStr.toLowerCase());
            if (match) move = game.move(match);
        }
        if (!move) {
            move = game.move(possibleMoves[Math.floor(Math.random() * possibleMoves.length)]);
        }

        board.position(game.fen());
        log('MOVE', `AI đi: ${move.san}`);
        
        if (game.in_checkmate()) { updateStatus('Chiếu bí!'); stopGame(); }
        else if (game.in_draw()) { updateStatus('Hòa!'); stopGame(); }
        else if (isRunning) { updateStatus('Đến lượt bạn'); }

    } catch (err) {
        log('ERROR', `Lỗi: ${err.message}`);
        stopGame();
    }
}

$(document).ready(function() {
    board = Chessboard('board', { draggable: false, position: 'start', pieceTheme: chessDotComPieceTheme });
    $('#board').on('click', '.square-55d63', function() {
        const square = $(this).attr('data-square');
        if (square) handleSquareClick(square);
    });
    setTimeout(() => board.resize(), 300);
});
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

def build_auth_header(auth_type, api_key):
    if auth_type == 'x-api-key':
        return {"x-api-key": api_key, "Content-Type": "application/json"}
    else:
        bearer = api_key if api_key.startswith('Bearer ') else f"Bearer {api_key}"
        return {"Authorization": bearer, "Content-Type": "application/json"}

@app.route('/api/models', methods=['POST'])
def api_models():
    try:
        data = request.get_json()
        target_url = data.get('target_endpoint', '')
        api_key = data.get('api_key', '')
        auth_type = data.get('auth_type', 'Bearer')

        # Tự động suy ra endpoint /models từ chat endpoint
        if '/chat/completions' in target_url:
            models_url = target_url.replace('/chat/completions', '/models')
        elif target_url.endswith('/'):
            models_url = target_url + 'models'
        else:
            models_url = target_url + '/models'

        headers = build_auth_header(auth_type, api_key)
        headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"

        chosen_proxy = get_next_proxy()
        proxies = {"http": chosen_proxy, "https": chosen_proxy}

        response = crequests.get(models_url, headers=headers, proxies=proxies, impersonate="chrome120", timeout=20)
        
        try:
            response.json()
            return response.text, response.status_code, [('Content-Type', 'application/json')]
        except json.JSONDecodeError:
            snippet = response.text[:200].replace('\n', ' ')
            return jsonify({"error": f"Server không trả về JSON (HTTP {response.status_code}): {snippet}"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/test', methods=['POST'])
def api_test():
    try:
        data = request.get_json()
        target_url = data.get('target_endpoint')
        api_key = data.get('api_key')
        auth_type = data.get('auth_type', 'Bearer')
        model = data.get('model', 'gpt-3.5-turbo')

        headers = build_auth_header(auth_type, api_key)
        headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 5
        }

        chosen_proxy = get_next_proxy()
        proxies = {"http": chosen_proxy, "https": chosen_proxy}

        response = crequests.post(target_url, headers=headers, json=payload, proxies=proxies, impersonate="chrome120", timeout=20)
        if response.status_code in [200, 400, 404, 422]:
            return jsonify({"status": "ok", "code": response.status_code}), 200
        return response.text, response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def proxy_chat():
    try:
        payload = request.get_json()
        target_url = payload.pop('target_endpoint', '').strip()
        api_key = payload.pop('api_key', '').strip()
        auth_type = payload.pop('auth_type', 'Bearer')

        if not target_url:
            return jsonify({"error": "Thiếu API Endpoint"}), 400

        headers = build_auth_header(auth_type, api_key)
        headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"

        chosen_proxy = get_next_proxy()
        proxies = {"http": chosen_proxy, "https": chosen_proxy}

        response = crequests.post(
            target_url,
            headers=headers,
            json=payload,
            proxies=proxies,
            impersonate="chrome120",
            timeout=25
        )

        if response.status_code == 200:
            try:
                response.json()
                return response.text, 200, [('Content-Type', 'application/json')]
            except json.JSONDecodeError:
                snippet = response.text[:300].replace('\n', ' ')
                return jsonify({"error": f"API trả về Non-JSON: {snippet}"}), 500

        return jsonify({"error": f"Lỗi HTTP {response.status_code}: {response.text[:200]}"}), 500

    except Exception as e:
        return jsonify({"error": f"Lỗi Gateway: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
