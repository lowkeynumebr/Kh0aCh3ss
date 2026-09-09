import json
import random
import subprocess
import os
from flask import Flask, request, jsonify, render_template_string
from curl_cffi import requests as crequests

app = Flask(__name__)

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
<title>Cờ Vua AI & Render Terminal</title>
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

/* Tabs style */
.tabs { display: flex; gap: 4px; margin-bottom: 10px; }
.tab-btn { flex: 1; padding: 8px; background: #334155; border: none; border-radius: 6px; color: #cbd5e1; cursor: pointer; font-size: 0.8rem; font-weight: bold; }
.tab-btn.active { background: #0284c7; color: #fff; }
.tab-content { display: none; }
.tab-content.active { display: block; }

/* AI vs AI configs */
.ai-vs-ai-panel { background: #0f172a; border: 1px dashed #334155; padding: 8px; border-radius: 6px; margin-top: 8px; display: none; }
.ai-vs-ai-panel h3 { font-size: 0.8rem; color: #38bdf8; margin-bottom: 6px; }

/* Terminal style */
.terminal-box { height: 280px; overflow-y: auto; background: #000; border-radius: 6px; border: 1px solid #334155; padding: 8px; font-family: 'Courier New', Courier, monospace; font-size: 0.75rem; color: #22c55e; white-space: pre-wrap; word-break: break-all; margin-bottom: 6px; }
.terminal-input-row { display: flex; gap: 6px; }
.terminal-input-row input { flex: 1; background: #020617; }
</style>
</head>
<body>

<div class="container">
    <h1>Cờ Vua AI & Render Terminal</h1>
    
    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('game')">🎮 Ván Cờ AI</button>
        <button class="tab-btn" onclick="switchTab('terminal')">💻 Render Terminal</button>
    </div>

    <!-- TAB 1: CỜ VUA -->
    <div id="tab-game" class="tab-content active">
        <div class="card"><div id="board"></div></div>
        <div class="card">
            <div class="form-group">
                <label>Tên Provider (Nhà cung cấp - Không dấu)</label>
                <input type="text" id="providerName" value="OpenAI">
            </div>
            <div class="form-group">
                <label>API Endpoint</label>
                <input type="text" id="apiEndpoint" value="https://api.openai.com/v1">
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

            <!-- PHẦN QUÉT VÀ CHỌN MODEL TỪ DANH SÁCH LƯU TRỮ -->
            <div class="form-group" style="background: #0f172a; padding: 8px; border-radius: 6px; border: 1px solid #334155; margin-top: 6px;">
                <label style="color: #38bdf8; font-weight: bold; margin-bottom: 4px;">🎯 Kho Model Đã Quét (Lưu vĩnh viễn)</label>
                <div class="row" style="margin-bottom: 6px;">
                    <input type="text" id="modelSearch" placeholder="🔍 Tìm kiếm model trong kho..." oninput="filterModelList()" style="flex: 2;">
                    <button class="btn-success" onclick="fetchModels()" style="flex: 1; margin-top:0;">Quét & Cộng Dồn</button>
                </div>
                <div class="row">
                    <select id="savedModelSelect" onchange="onSelectedModelChange()" style="flex: 3;">
                        <option value="">-- Chưa có model nào, hãy bấm Quét --</option>
                    </select>
                    <button class="btn-danger" onclick="clearSavedModels()" style="flex: 1; margin-top:0; font-size: 0.7rem;">Xóa Kho</button>
                </div>
            </div>

            <div class="row" style="margin-top: 6px;">
                <button onclick="testConnection()" style="background: #0d9488;">Test Connect Model Đang Chọn</button>
            </div>

            <div class="row" style="margin-top: 6px;">
                <div class="form-group" style="flex: 1;">
                    <label>Chế độ ván đấu</label>
                    <select id="gameMode" onchange="toggleAiVsAiPanel()">
                        <option value="player_vs_ai">Người vs AI</option>
                        <option value="ai_vs_ai">🤖 AI vs AI (Tự động)</option>
                    </select>
                </div>
                <div class="form-group" id="playerColorGroup" style="flex: 1;">
                    <label>Bạn cầm quân</label>
                    <select id="playerColor">
                        <option value="w">Trắng</option>
                        <option value="b">Đen</option>
                    </select>
                </div>
            </div>

            <!-- Panel cấu hình riêng cho AI vs AI (2 API độc lập) -->
            <div id="aiVsAiPanel" class="ai-vs-ai-panel">
                <h3>⚙️ Cấu hình AI Đen (Quân Đen)</h3>
                <div class="form-group">
                    <label>Chọn Model Đen từ Kho</label>
                    <select id="blackModelSelect" onchange="onBlackModelChange()">
                        <option value="">-- Chọn Model Đen --</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Endpoint AI Đen</label>
                    <input type="text" id="blackEndpoint" readonly>
                </div>
                <div class="row">
                    <div class="form-group" style="flex: 2;">
                        <label>API Key AI Đen</label>
                        <input type="password" id="blackApiKey" readonly>
                    </div>
                    <div class="form-group" style="flex: 1;">
                        <label>Auth Type</label>
                        <input type="text" id="blackAuthType" readonly style="color: #94a3b8;">
                    </div>
                </div>
            </div>

            <button id="startBtn" onclick="startGame()" style="margin-top: 8px;">Bắt Đầu Ván Mới</button>
            <button id="stopBtn" class="btn-danger" onclick="stopGame()" style="display: none; margin-top: 8px;">Dừng Trận Đấu</button>
            <div class="status-box" id="statusBox">Trạng thái: Sẵn sàng</div>
            <div class="log-header">
                <span>DEBUG LOG</span>
                <div>
                    <button class="btn-secondary" onclick="copyLog('logBox')">Copy</button>
                    <button class="btn-secondary" onclick="$('#logBox').empty()">Xóa</button>
                </div>
            </div>
            <div class="log-box" id="logBox"></div>
        </div>
    </div>

    <!-- TAB 2: TERMINAL RENDER -->
    <div id="tab-terminal" class="tab-content">
        <div class="card">
            <div class="log-header" style="margin-top: 0; margin-bottom: 6px;">
                <span style="color: #38bdf8;">Render Free Tier (0.1 CPU / 512MB RAM)</span>
                <div>
                    <button class="btn-secondary" onclick="copyLog('termOutput')">Copy Log</button>
                    <button class="btn-secondary" onclick="$('#termOutput').html('Terminal Ready.\\n')">Xóa Log</button>
                </div>
            </div>
            <div class="terminal-box" id="termOutput">Terminal Ready. Gõ lệnh bash (vd: pip install ..., df -h, ls -la)...\\n</div>
            <div class="terminal-input-row">
                <input type="text" id="termCmd" placeholder="Nhập lệnh bash..." onkeydown="if(event.key==='Enter') executeTerminalCommand()">
                <button onclick="executeTerminalCommand()" style="width: 80px; margin-top:0;">Gửi</button>
            </div>
        </div>
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

let modelRegistry = JSON.parse(localStorage.getItem('ai_chess_model_registry') || '{}');

function switchTab(tabName) {
    $('.tab-btn').removeClass('active');
    $('.tab-content').removeClass('active');
    if(tabName === 'game') {
        $('.tab-btn:eq(0)').addClass('active');
        $('#tab-game').addClass('active');
        if(board) board.resize();
    } else {
        $('.tab-btn:eq(1)').addClass('active');
        $('#tab-terminal').addClass('active');
    }
}

function toggleAiVsAiPanel() {
    let mode = $('#gameMode').val();
    if(mode === 'ai_vs_ai') {
        $('#aiVsAiPanel').show();
        $('#playerColorGroup').hide();
    } else {
        $('#aiVsAiPanel').hide();
        $('#playerColorGroup').show();
    }
}

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

function copyLog(elementId) { navigator.clipboard.writeText($('#' + elementId).text()).then(() => alert('Đã copy nội dung!')); }
function updateStatus(msg) { $('#statusBox').text('Trạng thái: ' + msg); }
function removeHighlights() { $('#board .square-55d63').removeClass('highlight-square highlight-hint'); }

function renderModelSelects(filterText = '') {
    const $sel = $('#savedModelSelect');
    const $bSel = $('#blackModelSelect');
    
    let currentVal = $sel.val();
    let currentBVal = $bSel.val();

    $sel.empty().append('<option value="">-- Chọn Model Trắng từ kho --</option>');
    $bSel.empty().append('<option value="">-- Chọn Model Đen từ kho --</option>');

    let keys = Object.keys(modelRegistry);
    if(keys.length === 0) {
        $sel.append('<option value="" disabled>Kho trống, hãy bấm Quét model</option>');
        $bSel.append('<option value="" disabled>Kho trống, hãy bấm Quét model</option>');
        return;
    }

    let lowerFilter = filterText.toLowerCase();
    keys.forEach(mId => {
        if(!lowerFilter || mId.toLowerCase().includes(lowerFilter)) {
            let info = modelRegistry[mId];
            let labelText = `${mId} (${info.provider})`;
            $sel.append(`<option value="${mId}">${labelText}</option>`);
            $bSel.append(`<option value="${mId}">${labelText}</option>`);
        }
    });

    if(modelRegistry[currentVal]) $sel.val(currentVal);
    if(modelRegistry[currentBVal]) $bSel.val(currentBVal);
}

function filterModelList() {
    let query = $('#modelSearch').val();
    renderModelSelects(query);
}

function onSelectedModelChange() {
    let mId = $('#savedModelSelect').val();
    if(!mId || !modelRegistry[mId]) return;
    let info = modelRegistry[mId];

    $('#providerName').val(info.provider);
    $('#apiEndpoint').val(info.endpoint);
    $('#apiKey').val(info.apiKey);
    $('#authType').val(info.authType);
}

function onBlackModelChange() {
    let mId = $('#blackModelSelect').val();
    if(!mId || !modelRegistry[mId]) return;
    let info = modelRegistry[mId];

    $('#blackEndpoint').val(info.endpoint);
    $('#blackApiKey').val(info.apiKey);
    $('#blackAuthType').val(info.authType);
}

async function fetchModels() {
    let endpoint = $('#apiEndpoint').val().trim();
    let apiKey = $('#apiKey').val().trim();
    let authType = $('#authType').val();
    let provider = $('#providerName').val().trim() || 'Custom';

    if (!apiKey) { alert('Vui lòng nhập API Key trước khi quét!'); return; }
    if (!endpoint) { alert('Vui lòng nhập API Endpoint!'); return; }
    
    log('SYS', `Đang quét model trực tiếp từ Endpoint: [${endpoint}]...`);

    try {
        const res = await fetch('/api/models', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target_endpoint: endpoint, api_key: apiKey, auth_type: authType, provider: provider })
        });
        const data = await res.json();
        
        if (res.ok && data.models && data.models.length > 0) {
            let countNew = 0;
            data.models.forEach(mId => {
                if(!modelRegistry[mId]) countNew++;
                modelRegistry[mId] = {
                    provider: provider,
                    endpoint: endpoint,
                    apiKey: apiKey,
                    authType: authType
                };
            });

            localStorage.setItem('ai_chess_model_registry', JSON.stringify(modelRegistry));
            renderModelSelects();

            log('SUCCESS', `Quét thành công! Thêm mới ${countNew} model. Tổng kho: ${Object.keys(modelRegistry).length}`);
            alert(`Quét thành công qua [${provider}]!\nĐã cộng dồn vào kho vĩnh viễn.`);
        } else {
            throw new Error(data.error || 'Không tìm thấy model nào.');
        }
    } catch (err) {
        log('ERROR', `Lỗi quét models: ${err.message}`);
        alert('Lỗi: ' + err.message);
    }
}

function clearSavedModels() {
    if(confirm('Bạn có chắc chắn muốn xóa toàn bộ kho model đã lưu vĩnh viễn không?')) {
        modelRegistry = {};
        localStorage.removeItem('ai_chess_model_registry');
        renderModelSelects();
        log('SYS', 'Đã xóa sạch kho model.');
    }
}

async function testConnection() {
    let mId = $('#savedModelSelect').val();
    if(!mId) { alert('Vui lòng chọn 1 model từ kho để Test!'); return; }
    let info = modelRegistry[mId];

    try {
        const res = await fetch('/api/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target_endpoint: info.endpoint, api_key: info.apiKey, auth_type: info.authType, model: mId })
        });
        const data = await res.json();
        if (res.ok) alert(`Kết nối model [${mId}] thành công! Mã: ${data.code}`);
        else alert('Kết nối thất bại: ' + data.error);
    } catch (err) { alert('Lỗi: ' + err.message); }
}

function handleSquareClick(square) {
    let mode = $('#gameMode').val();
    if (mode === 'ai_vs_ai') return;

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
            if (isRunning && !game.game_over()) setTimeout(triggerAiMove, 200);
        } else {
            const piece = game.get(square);
            if (piece && piece.color === playerColor) handleSquareClick(square);
        }
    }
}

function startGame() {
    let mode = $('#gameMode').val();
    let whiteModel = $('#savedModelSelect').val();

    if (!whiteModel) { alert('Vui lòng chọn Model Trắng từ kho model!'); return; }

    if (mode === 'ai_vs_ai') {
        let blackModel = $('#blackModelSelect').val();
        if (!blackModel) { alert('Vui lòng chọn Model Đen từ kho cho AI Đen!'); return; }
    }

    game.reset();
    isRunning = true;
    selectedSquare = null;
    removeHighlights();

    if (mode === 'player_vs_ai') {
        const playerColor = $('#playerColor').val();
        board.orientation(playerColor === 'b' ? 'black' : 'white');
    } else {
        board.orientation('white');
    }

    board.position(game.fen());
    board.resize();
    $('#startBtn').hide();
    $('#stopBtn').show();
    $('#logBox').empty();
    
    log('SYSTEM', `--- Bắt đầu ván đấu (${mode === 'ai_vs_ai' ? 'AI vs AI' : 'Người vs AI'}) ---`);
    updateStatus('Đang trong trận đấu');

    if (mode === 'ai_vs_ai') {
        setTimeout(triggerAiVsAiMove, 400);
    } else {
        const playerColor = $('#playerColor').val();
        if (playerColor === 'b') triggerAiMove();
    }
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

async function executeAiMoveLogic(model, info, isAiVsAi = false) {
    const possibleMoves = game.moves();
    const turn = game.turn();
    const promptText = isAiVsAi 
        ? `Current FEN: ${game.fen()}. Legal moves: ${possibleMoves.join(', ')}. Reply with ONLY the best move in SAN format (e.g. e4, Nf3).`
        : `Current FEN: ${game.fen()}. Legal moves: ${possibleMoves.join(', ')}. Reply with ONLY the best move in SAN format (e.g. e4, Nf3).`;

    const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            model: model,
            messages: [{ role: 'user', content: promptText }],
            temperature: 0.1,
            max_tokens: 15,
            target_endpoint: info.endpoint,
            api_key: info.apiKey,
            auth_type: info.authType
        })
    });
    
    const text = await res.text();
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${text}`);
    
    let data;
    try {
        data = JSON.parse(text);
    } catch(e) {
        throw new Error("Phản hồi JSON không hợp lệ từ API.");
    }

    if (!data.choices || !data.choices[0] || !data.choices[0].message || !data.choices[0].message.content) {
        throw new Error("Cấu trúc phản hồi thiếu trường nội dung (choices[0].message.content).");
    }

    let aiMoveStr = data.choices[0].message.content.trim().replace(/['"`]/g, '');
    let move = game.move(aiMoveStr);
    
    if (!move) {
        let matched = game.moves({verbose:true}).find(m => m.san.toLowerCase() === aiMoveStr.toLowerCase() || m.lan.toLowerCase() === aiMoveStr.toLowerCase());
        if (matched) move = game.move(matched);
        else move = game.move(game.moves()[0]); // Tự động chọn nước đi hợp lệ đầu tiên nếu AI trả về linh tinh
    }
    return move;
}

async function triggerAiMove(retryCount = 0) {
    if (!isRunning || game.game_over()) return;
    let model = $('#savedModelSelect').val();
    let info = modelRegistry[model];
    if(!info) { stopGame(); return; }

    updateStatus(`AI (${model}) đang suy nghĩ...`);
    log('API_REQ', `Model: ${model} | Gửi request... (Thử: ${retryCount + 1})`);
    
    try {
        let move = await executeAiMoveLogic(model, info, false);
        board.position(game.fen());
        log('MOVE', `AI đi: ${move.san}`);
        
        if (game.in_checkmate()) { updateStatus('Chiếu bí!'); stopGame(); }
        else if (game.in_draw()) { updateStatus('Hòa!'); stopGame(); }
        else if (isRunning) { updateStatus('Đến lượt bạn'); }
    } catch (err) {
        log('WARN', `Lỗi mạng/API: ${err.message}`);
        if (retryCount < 2 && isRunning) {
            log('SYSTEM', `Tự động thử lại sau 1.5 giây (${retryCount + 1}/3)...`);
            aiTimeout = setTimeout(() => triggerAiMove(retryCount + 1), 1500);
        } else {
            log('ERROR', 'Thất bại sau nhiều lần thử. Dừng ván đấu.');
            stopGame();
        }
    }
}

async function triggerAiVsAiMove(retryCount = 0) {
    if (!isRunning || game.game_over()) return;
    
    let turn = game.turn();
    let model = turn === 'w' ? $('#savedModelSelect').val() : $('#blackModelSelect').val();
    let info = modelRegistry[model];
    if(!info) { stopGame(); return; }

    updateStatus(`AI ${turn === 'w' ? 'Trắng' : 'Đen'} (${model}) đang suy nghĩ...`);
    log('API_REQ', `AI ${turn === 'w' ? 'Trắng' : 'Đen'} [Model: ${model}] | Gửi request... (Thử: ${retryCount + 1})`);
    
    try {
        let move = await executeAiMoveLogic(model, info, true);
        board.position(game.fen());
        log('MOVE', `AI ${turn === 'w' ? 'Trắng' : 'Đen'} đi: ${move.san}`);
        
        if (game.in_checkmate()) { updateStatus('Chiếu bí!'); stopGame(); }
        else if (game.in_draw()) { updateStatus('Hòa!'); stopGame(); }
        else if (isRunning) {
            aiTimeout = setTimeout(triggerAiVsAiMove, 300);
        }
    } catch (err) {
        log('WARN', `Lỗi AI vs AI: ${err.message}`);
        if (retryCount < 2 && isRunning) {
            log('SYSTEM', 'Tự động thử lại lượt đi sau 1.5 giây...');
            aiTimeout = setTimeout(() => triggerAiVsAiMove(retryCount + 1), 1500);
        } else {
            log('ERROR', 'Thất bại liên tục, tự động bốc nước đi dự phòng để tiếp tục trận đấu.');
            try {
                let fallbackMove = game.move(game.moves()[0]);
                board.position(game.fen());
                log('MOVE', `[DỰ PHÒNG] AI ${turn === 'w' ? 'Trắng' : 'Đen'} đi: ${fallbackMove.san}`);
                if (isRunning) aiTimeout = setTimeout(triggerAiVsAiMove, 300);
            } catch(e) {
                stopGame();
            }
        }
    }
}

async function executeTerminalCommand() {
    const cmd = $('#termCmd').val().trim();
    if (!cmd) return;

    let isDownloadCmd = cmd.includes('pip install') || cmd.includes('apt-get') || cmd.includes('wget') || cmd.includes('curl') || cmd.includes('git clone');
    if (isDownloadCmd) {
        let estimatedMB = (Math.random() * 40 + 10).toFixed(1);
        let confirmAction = confirm(`⚠️ CẢNH BÁO TẢI TỆP/GÓI TRÊN RENDER:\\nBạn chuẩn bị chạy lệnh tải dung lượng khoảng ~${estimatedMB} MB trên gói Free (512MB RAM).\\n\\nBạn có muốn tiếp tục (YES) hay Hủy (NO)?`);
        if (!confirmAction) {
            $('#termOutput').append(`\\n$ ${cmd}\\n[HỦY BỎ] Đã dừng lệnh tải.\\n`);
            $('#termCmd').val('');
            return;
        }
    }

    $('#termOutput').append(`\\n$ ${cmd}\\n[Đang thực thi...]\\n`);
    $('#termCmd').val('');
    const termOut = document.getElementById('termOutput');
    termOut.scrollTop = termOut.scrollHeight;

    try {
        const res = await fetch('/api/terminal', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: cmd })
        });
        const data = await res.json();
        if (res.ok) {
            $('#termOutput').append(data.output + `\\n[Hoàn thành - Exit Code: ${data.exit_code}]\\n`);
        } else {
            $('#termOutput').append(`[LỖI] ${data.error}\\n`);
        }
    } catch (err) {
        $('#termOutput').append(`[LỖI KẾT NỐI] ${err.message}\\n`);
    }
    termOut.scrollTop = termOut.scrollHeight;
}

$(document).ready(function() {
    board = Chessboard('board', { draggable: false, position: 'start', pieceTheme: chessDotComPieceTheme });
    $('#board').on('click', '.square-55d63', function() {
        const square = $(this).attr('data-square');
        if (square) handleSquareClick(square);
    });
    renderModelSelects();
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

def clean_base_url(url):
    url = url.strip().rstrip('/')
    for suffix in ['/chat/completions', '/completions', '/models', '/chat']:
        if url.endswith(suffix):
            url = url[:-len(suffix)].rstrip('/')
    return url

@app.route('/api/models', methods=['POST'])
def api_models():
    try:
        data = request.get_json()
        target_url = data.get('target_endpoint', '').strip()
        api_key = data.get('api_key', '')
        auth_type = data.get('auth_type', 'Bearer')

        base_url = clean_base_url(target_url)
        models_url = f"{base_url}/models"

        headers = build_auth_header(auth_type, api_key)
        headers["User-Agent"] = "claude-cli/1.0.0 (external, cli)"
        
        chosen_proxy = get_next_proxy()
        proxies = {"http": chosen_proxy, "https": chosen_proxy}

        response = crequests.get(models_url, headers=headers, proxies=proxies, impersonate="chrome120", timeout=15, allow_redirects=False)
        if response.status_code == 200:
            res_json = response.json()
            model_list = []
            
            raw_data = res_json.get('data', res_json.get('models', res_json))
            if isinstance(raw_data, list):
                for item in raw_data:
                    if isinstance(item, dict):
                        m_id = item.get('id') or item.get('name') or item.get('model')
                        if m_id: model_list.append(str(m_id))
                    elif isinstance(item, str):
                        model_list.append(item)
            elif isinstance(raw_data, dict):
                for k, v in raw_data.items():
                    if isinstance(v, str): model_list.append(v)
                    elif isinstance(v, dict):
                        m_id = v.get('id') or v.get('name')
                        if m_id: model_list.append(str(m_id))

            if model_list:
                return jsonify({"models": model_list}), 200
            else:
                return jsonify({"error": "Endpoint trả về 200 nhưng không tìm thấy cấu trúc danh sách model."}), 400
        else:
            return jsonify({"error": f"Lỗi HTTP {response.status_code}: {response.text[:200]}"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/test', methods=['POST'])
def api_test():
    try:
        data = request.get_json()
        target_url = data.get('target_endpoint', '').strip()
        api_key = data.get('api_key')
        auth_type = data.get('auth_type', 'Bearer')
        model = data.get('model', 'gpt-4o')

        base_url = clean_base_url(target_url)
        chat_url = f"{base_url}/chat/completions"

        headers = build_auth_header(auth_type, api_key)
        headers["User-Agent"] = "claude-cli/1.0.0 (external, cli)"
        payload = {"model": model, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5}
        chosen_proxy = get_next_proxy()
        proxies = {"http": chosen_proxy, "https": chosen_proxy}

        response = crequests.post(chat_url, headers=headers, json=payload, proxies=proxies, impersonate="chrome120", timeout=15, allow_redirects=False)
        if response.status_code in [200, 400, 404, 422, 403]:
            return jsonify({"status": "ok", "code": response.status_code, "error": response.text[:200]}), 200
        return jsonify({"error": response.text[:200]}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def proxy_chat():
    try:
        payload = request.get_json()
        target_url = payload.pop('target_endpoint', '').strip()
        api_key = payload.pop('api_key', '').strip()
        auth_type = payload.pop('auth_type', 'Bearer')
        payload.pop('provider', None)

        if not target_url:
            return jsonify({"error": "Thiếu API Endpoint"}), 400

        base_url = clean_base_url(target_url)
        chat_url = f"{base_url}/chat/completions"

        headers = build_auth_header(auth_type, api_key)
        headers["User-Agent"] = "claude-cli/1.0.0 (external, cli)"
        chosen_proxy = get_next_proxy()
        proxies = {"http": chosen_proxy, "https": chosen_proxy}

        response = crequests.post(chat_url, headers=headers, json=payload, proxies=proxies, impersonate="chrome120", timeout=25, allow_redirects=False)
        if response.status_code == 200:
            return jsonify(response.json()), 200
        return jsonify({"error": f"Lỗi HTTP {response.status_code}: {response.text[:200]}"}), 500
    except Exception as e:
        return jsonify({"error": f"Lỗi Gateway: {str(e)}"}), 500

@app.route('/api/terminal', methods=['POST'])
def api_terminal():
    try:
        data = request.get_json()
        command = data.get('command', '')

        if not command:
            return jsonify({"error": "Thiếu câu lệnh!"}), 400

        process = subprocess.Popen(
            command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        stdout, stderr = process.communicate(timeout=40)
        exit_code = process.returncode

        full_output = ""
        if stdout: full_output += stdout
        if stderr:
            if full_output: full_output += "\n--- STDERR / WARNINGS ---\n"
            full_output += stderr
        
        if not full_output: full_output = "Lệnh đã chạy xong nhưng không trả về dữ liệu text."

        return jsonify({"output": full_output, "exit_code": exit_code}), 200

    except subprocess.TimeoutExpired:
        return jsonify({"output": "⚠️ Lỗi: Tiến trình chạy quá thời gian giới hạn (>40s).", "exit_code": -1}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
