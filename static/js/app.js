// Crypto Trading Bot Dashboard JavaScript

let refreshInterval;
let isInitialized = false;

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setupEventListeners();
    startAutoRefresh();
});

function initializeDashboard() {
    updateStatus();
    loadAllData();
    isInitialized = true;
}

function setupEventListeners() {
    // Start bot button
    document.getElementById('start-btn').addEventListener('click', function() {
        startBot();
    });

    // Stop bot button
    document.getElementById('stop-btn').addEventListener('click', function() {
        stopBot();
    });

    // Test connection button
    document.getElementById('test-btn').addEventListener('click', function() {
        testConnection();
    });
}

function startAutoRefresh() {
    // Refresh data every 30 seconds
    refreshInterval = setInterval(function() {
        if (isInitialized) {
            updateStatus();
            loadAllData();
        }
    }, 30000);
}

function updateStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            updateStatusIndicator(data);
        })
        .catch(error => {
            console.error('Error updating status:', error);
            showToast('Error updating status', 'error');
        });
}

function updateStatusIndicator(data) {
    const statusText = document.getElementById('status-text');
    const statusIndicator = document.querySelector('#status-indicator i');
    
    if (data.bot_running) {
        statusText.textContent = 'Running';
        statusIndicator.className = 'fas fa-circle text-success';
        statusIndicator.style.animation = 'pulse 2s infinite';
    } else {
        statusText.textContent = 'Stopped';
        statusIndicator.className = 'fas fa-circle text-danger';
        statusIndicator.style.animation = 'none';
    }
}

function loadAllData() {
    loadPortfolio();
    loadBalance();
    loadPositions();
    loadTrades();
    loadPerformance();
}

function loadPortfolio() {
    fetch('/api/portfolio')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('portfolio-content').innerHTML = 
                    `<p class="text-muted">${data.error}</p>`;
                return;
            }
            
            const html = `
                <div class="row">
                    <div class="col-6">
                        <strong>Total P&L:</strong><br>
                        <span class="${data.total_pnl >= 0 ? 'profit' : 'loss'}">
                            $${data.total_pnl?.toFixed(2) || '0.00'}
                        </span>
                    </div>
                    <div class="col-6">
                        <strong>Open Positions:</strong><br>
                        <span>${data.open_positions || 0}</span>
                    </div>
                </div>
                <div class="row mt-2">
                    <div class="col-6">
                        <strong>Total Trades:</strong><br>
                        <span>${data.total_trades || 0}</span>
                    </div>
                    <div class="col-6">
                        <strong>Daily Trades:</strong><br>
                        <span>${data.daily_trades || 0}</span>
                    </div>
                </div>
                <div class="row mt-2">
                    <div class="col-12">
                        <strong>Daily Loss:</strong><br>
                        <span class="${data.daily_loss > 0 ? 'loss' : 'neutral'}">
                            $${data.daily_loss?.toFixed(2) || '0.00'}
                        </span>
                    </div>
                </div>
            `;
            
            document.getElementById('portfolio-content').innerHTML = html;
        })
        .catch(error => {
            console.error('Error loading portfolio:', error);
            document.getElementById('portfolio-content').innerHTML = 
                '<p class="text-muted">Error loading portfolio data</p>';
        });
}

function loadBalance() {
    fetch('/api/balance')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('balance-content').innerHTML = 
                    `<p class="text-muted">${data.error}</p>`;
                return;
            }
            
            let html = '<div class="row">';
            let totalUSD = 0;
            
            for (const [currency, amount] of Object.entries(data)) {
                if (amount > 0) {
                    const usdValue = currency === 'USD' ? amount : 0; // Simplified
                    totalUSD += usdValue;
                    html += `
                        <div class="col-6 mb-2">
                            <strong>${currency}:</strong><br>
                            <span>${amount.toFixed(6)}</span>
                        </div>
                    `;
                }
            }
            
            html += '</div>';
            html += `<div class="row mt-2"><div class="col-12"><strong>Total Value:</strong> $${totalUSD.toFixed(2)}</div></div>`;
            
            document.getElementById('balance-content').innerHTML = html;
        })
        .catch(error => {
            console.error('Error loading balance:', error);
            document.getElementById('balance-content').innerHTML = 
                '<p class="text-muted">Error loading balance data</p>';
        });
}

function loadPositions() {
    fetch('/api/positions')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('positions-content').innerHTML = 
                    `<p class="text-muted">${data.error}</p>`;
                return;
            }
            
            if (data.length === 0) {
                document.getElementById('positions-content').innerHTML = 
                    '<p class="text-muted">No active positions</p>';
                return;
            }
            
            let html = '';
            data.forEach(position => {
                html += `
                    <div class="position-card">
                        <div class="row">
                            <div class="col-md-6">
                                <strong>${position.symbol}</strong><br>
                                <span class="badge bg-${position.type === 'BUY' ? 'success' : 'danger'}">${position.type}</span>
                            </div>
                            <div class="col-md-6">
                                <strong>Amount:</strong> ${position.amount.toFixed(6)}<br>
                                <strong>Entry:</strong> $${position.entry_price.toFixed(2)}
                            </div>
                        </div>
                        <div class="row mt-2">
                            <div class="col-md-6">
                                <strong>Stop Loss:</strong> $${position.stop_loss.toFixed(2)}
                            </div>
                            <div class="col-md-6">
                                <strong>Take Profit:</strong> $${position.take_profit.toFixed(2)}
                            </div>
                        </div>
                    </div>
                `;
            });
            
            document.getElementById('positions-content').innerHTML = html;
        })
        .catch(error => {
            console.error('Error loading positions:', error);
            document.getElementById('positions-content').innerHTML = 
                '<p class="text-muted">Error loading positions data</p>';
        });
}

function loadTrades() {
    fetch('/api/trades')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('trades-content').innerHTML = 
                    `<p class="text-muted">${data.error}</p>`;
                return;
            }
            
            if (data.length === 0) {
                document.getElementById('trades-content').innerHTML = 
                    '<p class="text-muted">No trades yet</p>';
                return;
            }
            
            let html = '';
            data.forEach(trade => {
                const pnlClass = trade.pnl >= 0 ? 'profit' : 'loss';
                const pnlText = trade.pnl ? `$${trade.pnl.toFixed(2)}` : 'N/A';
                
                html += `
                    <div class="trade-row ${pnlClass}">
                        <div class="row">
                            <div class="col-md-3">
                                <strong>${trade.symbol}</strong><br>
                                <span class="badge bg-${trade.type === 'BUY' ? 'success' : 'danger'}">${trade.type}</span>
                            </div>
                            <div class="col-md-3">
                                <strong>Amount:</strong><br>
                                ${trade.amount.toFixed(6)}
                            </div>
                            <div class="col-md-3">
                                <strong>Entry Price:</strong><br>
                                $${trade.entry_price.toFixed(2)}
                            </div>
                            <div class="col-md-3">
                                <strong>Status:</strong><br>
                                <span class="badge bg-${trade.status === 'CLOSED' ? 'secondary' : 'warning'}">${trade.status}</span>
                            </div>
                        </div>
                        ${trade.pnl ? `<div class="row mt-1"><div class="col-12"><strong>P&L:</strong> <span class="${pnlClass}">${pnlText}</span></div></div>` : ''}
                    </div>
                `;
            });
            
            document.getElementById('trades-content').innerHTML = html;
        })
        .catch(error => {
            console.error('Error loading trades:', error);
            document.getElementById('trades-content').innerHTML = 
                '<p class="text-muted">Error loading trades data</p>';
        });
}

function loadPerformance() {
    fetch('/api/performance')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                return;
            }
            
            // Update status cards
            document.getElementById('total-pnl').textContent = `$${data.total_pnl?.toFixed(2) || '0.00'}`;
            document.getElementById('win-rate').textContent = `${data.win_rate?.toFixed(1) || '0'}%`;
            document.getElementById('total-trades').textContent = data.total_trades || 0;
            document.getElementById('open-positions').textContent = data.open_positions || 0;
            
            // Update colors
            const pnlElement = document.getElementById('total-pnl');
            pnlElement.className = data.total_pnl >= 0 ? 'profit' : 'loss';
        })
        .catch(error => {
            console.error('Error loading performance:', error);
        });
}

function startBot() {
    fetch('/api/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showToast(data.error, 'error');
        } else {
            showToast('Bot started successfully', 'success');
            updateStatus();
        }
    })
    .catch(error => {
        console.error('Error starting bot:', error);
        showToast('Error starting bot', 'error');
    });
}

function stopBot() {
    fetch('/api/stop', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showToast(data.error, 'error');
        } else {
            showToast('Bot stopped successfully', 'success');
            updateStatus();
        }
    })
    .catch(error => {
        console.error('Error stopping bot:', error);
        showToast('Error stopping bot', 'error');
    });
}

function testConnection() {
    fetch('/api/test')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showToast(data.error, 'error');
            } else {
                showToast('Connection test passed', 'success');
            }
        })
        .catch(error => {
            console.error('Error testing connection:', error);
            showToast('Error testing connection', 'error');
        });
}

function refreshData() {
    loadAllData();
    showToast('Data refreshed', 'info');
}

function showConfig() {
    fetch('/api/config')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showToast(data.error, 'error');
                return;
            }
            
            const html = `
                <form id="config-form">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Investment Amount ($)</label>
                                <input type="number" class="form-control" name="investment_amount" value="${data.investment_amount}">
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Max Position Size (%)</label>
                                <input type="number" class="form-control" name="max_position_size" value="${data.max_position_size * 100}">
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Stop Loss (%)</label>
                                <input type="number" class="form-control" name="stop_loss_percentage" value="${data.stop_loss_percentage}">
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Take Profit (%)</label>
                                <input type="number" class="form-control" name="take_profit_percentage" value="${data.take_profit_percentage}">
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Max Daily Trades</label>
                                <input type="number" class="form-control" name="max_daily_trades" value="${data.max_daily_trades}">
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Max Daily Loss ($)</label>
                                <input type="number" class="form-control" name="max_daily_loss" value="${data.max_daily_loss}">
                            </div>
                        </div>
                    </div>
                </form>
            `;
            
            document.getElementById('config-content').innerHTML = html;
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('configModal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error loading config:', error);
            showToast('Error loading configuration', 'error');
        });
}

function saveConfig() {
    const form = document.getElementById('config-form');
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = parseFloat(value);
    }
    
    fetch('/api/config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showToast(data.error, 'error');
        } else {
            showToast('Configuration saved successfully', 'success');
            bootstrap.Modal.getInstance(document.getElementById('configModal')).hide();
        }
    })
    .catch(error => {
        console.error('Error saving config:', error);
        showToast('Error saving configuration', 'error');
    });
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastBody = document.getElementById('toast-body');
    
    toastBody.textContent = message;
    toast.className = `toast ${type === 'error' ? 'bg-danger text-white' : type === 'success' ? 'bg-success text-white' : 'bg-info text-white'}`;
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});
