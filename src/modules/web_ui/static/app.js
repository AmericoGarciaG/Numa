/**
 * Numa AI Web Client (Nexus Protocol)
 * "Frontend Ligero" Implementation
 */

const API_BASE = '/api';

const app = {
    state: {
        isRecording: false,
        selectedDeviceId: null,
        isPushToTalk: true,
        token: null,
        mediaRecorder: null,
        audioChunks: [],
        user: { email: "test@numa.com", password: "password123" } // Default test creds
    },

    elements: {
        micBtn: document.getElementById('mic-btn'),
        micSelect: document.getElementById('mic-select'),
        statusText: document.getElementById('status-text'),
        subStatus: document.getElementById('sub-status'),
        connectionStatus: document.getElementById('connection-status'),
        resultCard: document.getElementById('result-card'),
        transactionList: document.getElementById('transaction-list'),
        dailyDate: document.getElementById('daily-date'),
        dailyIncomeValidated: document.getElementById('daily-income-validated'),
        dailyIncomeProvisional: document.getElementById('daily-income-provisional'),
        dailyExpenseValidated: document.getElementById('daily-expense-validated'),
        dailyExpenseProvisional: document.getElementById('daily-expense-provisional'),
        pushToTalkToggle: document.getElementById('push-to-talk-toggle'),
        chatContainer: document.getElementById('chat-container'),
        chatMessage: document.getElementById('chat-message'),

        // Card fields
        cardAmount: document.getElementById('card-amount'),
        cardConcept: document.getElementById('card-concept'),
        cardCategory: document.getElementById('card-category'),
        cardMerchant: document.getElementById('card-merchant'),
        cardDate: document.getElementById('card-date')
    },

    init: async function () {
        console.log("🚀 Numa Client Initializing...");

        // 1. Auto-Login
        await this.login();

        // 2. Setup Audio
        // We only request permissions when user clicks first time to be polite,
        // or we can verify support now.
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            this.updateStatus("Error: Navegador no soporta audio", "No Audio API");
            this.elements.micBtn.disabled = true;
        } else {
             // Load devices (might be empty if permission not granted yet)
             this.loadAudioDevices();
             
             // Refresh devices when permissions change or devices plug in
             navigator.mediaDevices.ondevicechange = () => this.loadAudioDevices();
        }

        // 3. Setup Listeners
        if (this.elements.micSelect) {
            this.elements.micSelect.addEventListener('change', (event) => {
                this.state.selectedDeviceId = event.target.value;
            });
        }

        if (this.elements.pushToTalkToggle) {
            this.state.isPushToTalk = this.elements.pushToTalkToggle.checked;
            this.updatePushToTalkUI();
            this.elements.pushToTalkToggle.addEventListener('change', (event) => {
                this.state.isPushToTalk = event.target.checked;
                this.updatePushToTalkUI();
            });
        }

        if (this.elements.micBtn) {
            this.elements.micBtn.addEventListener('click', () => {
                if (this.state.isPushToTalk) {
                    return;
                }
                this.toggleRecording();
            });

            this.elements.micBtn.addEventListener('mousedown', () => {
                if (!this.state.isPushToTalk) {
                    return;
                }
                if (!this.state.isRecording) {
                    this.startRecording();
                }
            });

            this.elements.micBtn.addEventListener('mouseup', () => {
                if (!this.state.isPushToTalk) {
                    return;
                }
                if (this.state.isRecording) {
                    this.stopRecording();
                }
            });

            this.elements.micBtn.addEventListener('mouseleave', () => {
                if (!this.state.isPushToTalk) {
                    return;
                }
                if (this.state.isRecording) {
                    this.stopRecording();
                }
            });

            this.elements.micBtn.addEventListener('touchstart', (event) => {
                if (!this.state.isPushToTalk) {
                    return;
                }
                event.preventDefault();
                if (!this.state.isRecording) {
                    this.startRecording();
                }
            });

            this.elements.micBtn.addEventListener('touchend', (event) => {
                if (!this.state.isPushToTalk) {
                    return;
                }
                event.preventDefault();
                if (this.state.isRecording) {
                    this.stopRecording();
                }
            });

            this.elements.micBtn.addEventListener('touchcancel', (event) => {
                if (!this.state.isPushToTalk) {
                    return;
                }
                event.preventDefault();
                if (this.state.isRecording) {
                    this.stopRecording();
                }
            });
        }

        // 4. Initial Load
        if (this.state.token) {
            this.refreshTransactions();
            this.refreshDailySummary();
        }

        this.showSystemMessage("Hola, soy Numa. ¿Qué gastos registramos hoy?");
    },
    
    loadAudioDevices: async function() {
        try {
             // Need to request permission first to get labels
             // If we don't have permission, labels will be empty strings
             // We can check if we have permission first or just try enumerate
             
             const devices = await navigator.mediaDevices.enumerateDevices();
             const audioInputs = devices.filter(device => device.kind === 'audioinput');
             
             const select = this.elements.micSelect;
             select.innerHTML = '';
             
             if (audioInputs.length === 0) {
                 const option = document.createElement('option');
                 option.text = "No se encontraron micrófonos";
                 select.add(option);
                 return;
             }
             
             const availableIds = audioInputs.map(device => device.deviceId);
             let selectedId = this.state.selectedDeviceId;

             if (!selectedId || !availableIds.includes(selectedId)) {
                 const defaultDevice = audioInputs.find(device => device.deviceId === 'default');
                 if (defaultDevice) {
                     selectedId = defaultDevice.deviceId;
                 } else {
                     selectedId = audioInputs[0].deviceId;
                 }
             }
             
             audioInputs.forEach((device, index) => {
                 const option = document.createElement('option');
                 option.value = device.deviceId;
                 option.text = device.label || `Micrófono ${index + 1}`;
                 select.add(option);
             });
             
             select.value = selectedId;
             this.state.selectedDeviceId = selectedId;
             
        } catch (err) {
            console.warn("Error loading audio devices:", err);
            const select = this.elements.micSelect;
            select.innerHTML = '<option>Error cargando dispositivos</option>';
        }
    },

    login: async function () {
        try {
            this.updateConnection("Autenticando...");

            // Try explicit register first (idempotent-ish in logic, usually fails if exists)
            // Just try login directly. If fails 401, maybe register?
            // For MVP simplicity, we assume the user exists OR we register.

            // NOTE: In a real app we wouldn't hardcode logic.
            // Let's try registering quickly just in case DB was reset
            // Let's try registering quickly just in case DB was reset
            await fetch(`${API_BASE}/users/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: this.state.user.email, password: this.state.user.password, name: "Test User" })
            }).catch(() => { }); // Ignore fail if exists

            // Login
            const response = await fetch(`${API_BASE}/token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `username=${encodeURIComponent(this.state.user.email)}&password=${encodeURIComponent(this.state.user.password)}`
            });

            if (!response.ok) throw new Error("Login failed");

            const data = await response.json();
            this.state.token = data.access_token;
            this.updateConnection("Conectado", "success");
            console.log("✅ Auth Token acquired.");

        } catch (error) {
            console.error("Auth Error:", error);
            this.updateConnection("Desconectado", "error");
            this.updateStatus("Error de Autenticación", "Revisa la consola");
        }
    },

    toggleRecording: async function () {
        if (this.state.isRecording) {
            this.stopRecording();
        } else {
            this.startRecording();
        }
    },

    startRecording: async function () {
        try {
            const selectedMicId = this.state.selectedDeviceId || this.elements.micSelect.value;
            const constraints = { 
                audio: selectedMicId ? { deviceId: { exact: selectedMicId } } : true 
            };
            
            console.log(`[DEBUG] Starting recording with device: ${selectedMicId || 'default'}`);

            const stream = await navigator.mediaDevices.getUserMedia(constraints);

            // Explicitly request WebM/Opus if supported
            const options = { mimeType: 'audio/webm' };
            if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
                options.mimeType = 'audio/webm;codecs=opus';
            }

            this.state.mediaRecorder = new MediaRecorder(stream, options);
            this.state.audioChunks = [];

            this.state.mediaRecorder.addEventListener("dataavailable", event => {
                if (event.data.size > 0) {
                    this.state.audioChunks.push(event.data);
                    console.log(`[DEBUG] Chunk received: ${event.data.size} bytes`);
                }
            });

            this.state.mediaRecorder.addEventListener("stop", () => {
                console.log("[DEBUG] Recorder stopped. Processing Blob...");
                // Pequeño delay de seguridad o verificación directa
                const mimeType = this.state.mediaRecorder.mimeType || 'audio/webm';
                const audioBlob = new Blob(this.state.audioChunks, { type: mimeType });
                
                console.log(`[DEBUG] Final Blob Size: ${audioBlob.size} bytes, Type: ${audioBlob.type}`);
                
                if (audioBlob.size < 100) {
                    console.warn("[WARN] Blob too small. Recording failed?");
                    this.updateStatus("Error: Audio vacío", "Intenta de nuevo");
                    return;
                }
                
                this.sendAudio(audioBlob);
            });

            this.state.mediaRecorder.start();
            this.state.isRecording = true;

            this.elements.micBtn.classList.add('recording');
            this.updateStatus("Escuchando...", "Di tu gasto...");
            this.showSystemMessage("Escuchando...");

        } catch (err) {
            console.error("Mic access denied:", err);
            this.updateStatus("Acceso a Micrófono Denegado", "Permite el acceso para continuar");
        }
    },

    stopRecording: function () {
        if (this.state.mediaRecorder && this.state.isRecording) {
            this.state.mediaRecorder.stop();
            
            // Stop all tracks to release the microphone
            this.state.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            
            this.state.isRecording = false;

            // UI Update
            this.elements.micBtn.classList.remove('recording');
            this.updateStatus("Procesando...", "No cierres la ventana");
        }
    },

    sendAudio: async function (audioBlob) {
        if (!this.state.token) return;

        this.showSystemMessage("Procesando tu audio...");

        setTimeout(() => this.updateSubStatus("Enviando audio..."), 100);
        setTimeout(() => this.updateSubStatus("Transcribiendo (Google V2)..."), 1000); // Fake progress for UX
        setTimeout(() => this.updateSubStatus("Analizando con Gemini AI..."), 2500);

        const formData = new FormData();
        // Naming the file audio.mp3 so server treats it as audio 
        // (even if container is webm, modern ffmpeg/libs handle it)
        formData.append("audio_file", audioBlob, "recording.webm");

        try {
            const response = await fetch(`${API_BASE}/transactions/voice`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.state.token}`
                },
                body: formData
            });

            if (response.status === 201) {
                const data = await response.json();
                const responseType = data.type || 'transaction';
                const message = data.message || null;

                if (responseType === 'transaction') {
                    const transactions = Array.isArray(data.data) ? data.data : [];
                    this.showSuccess(transactions, message);
                    this.refreshTransactions();
                    this.refreshDailySummary();
                } else if (responseType === 'chat') {
                    if (message) {
                        this.showSystemMessage(message);
                    }
                    this.updateStatus("Listo", "Consulta respondida");
                } else {
                    if (message) {
                        this.showSystemMessage(message);
                    }
                }
            } else {
                const err = await response.text();
                throw new Error(err);
            }

        } catch (error) {
            console.error("Transaction Error:", error);
            this.updateStatus("Error en Transacción", "Intenta de nuevo");
            this.elements.micBtn.classList.add('bg-red-600');
            setTimeout(() => this.elements.micBtn.classList.remove('bg-red-600'), 2000);
        }
    },

    showSuccess: function (transactions, backendMessage) {
        const list = Array.isArray(transactions) ? transactions : [transactions];
        const count = list.length;
        const last = list[list.length - 1];
        const totalAmount = list.reduce((sum, tx) => sum + (tx.amount || 0), 0);

        if (count > 1) {
            this.updateStatus("¡Listo!", `${count} transacciones registradas`);
            this.elements.cardConcept.textContent = `${count} transacciones registradas`;
            this.elements.cardAmount.textContent = `$${totalAmount.toFixed(2)}`;
            this.elements.cardCategory.textContent = "Múltiples";
            this.elements.cardMerchant.innerHTML = `<i class="fa-solid fa-store mr-1"></i> Varios`;
        } else {
            const t = last;
            this.updateStatus("¡Listo!", "Transacción registrada");
            this.elements.cardConcept.textContent = t.concept;
            this.elements.cardAmount.textContent = `$${t.amount.toFixed(2)}`;
            this.elements.cardCategory.textContent = t.category || "General";
            this.elements.cardMerchant.innerHTML = `<i class="fa-solid fa-store mr-1"></i> ${t.merchant || "Desconocido"}`;
        }

        const card = this.elements.resultCard;
        card.classList.remove('hidden');
        // Trigger reflow
        void card.offsetWidth;
        card.classList.remove('translate-y-4', 'opacity-0');

        setTimeout(() => {
            this.updateStatus("Presiona para hablar", "Registra otro gasto");
        }, 5000);

        if (backendMessage) {
            this.showSystemMessage(backendMessage);
        } else if (count > 1) {
            this.showSystemMessage(`Registré ${count} movimientos por un total de $${totalAmount.toFixed(2)}.`);
        } else if (last) {
            this.showSystemMessage(`Registré ${last.concept} por $${last.amount.toFixed(2)}.`);
        }
    },

    refreshTransactions: async function () {
        if (!this.state.token) return;

        try {
            const response = await fetch(`${API_BASE}/transactions`, {
                headers: { 'Authorization': `Bearer ${this.state.token}` }
            });
            const data = await response.json();
            this.renderTable(data);
        } catch (error) {
            console.error("Fetch Error:", error);
        }
    },

    refreshDailySummary: async function () {
        if (!this.state.token) return;

        try {
            const response = await fetch(`${API_BASE}/transactions/daily_summary`, {
                headers: { 'Authorization': `Bearer ${this.state.token}` }
            });

            if (!response.ok) {
                return;
            }

            const data = await response.json();
            this.renderDailySummary(data);
        } catch (error) {
            console.error("Daily summary error:", error);
        }
    },

    renderDailySummary: function (summary) {
        if (!summary) return;

        const formatAmount = (value) => {
            const number = typeof value === 'number' ? value : 0;
            return `$${number.toFixed(2)}`;
        };

        if (this.elements.dailyDate && summary.date) {
            try {
                const date = new Date(summary.date);
                this.elements.dailyDate.textContent = date.toLocaleDateString();
            } catch (e) {
                this.elements.dailyDate.textContent = summary.date;
            }
        }

        const validated = summary.validated || {};
        const provisional = summary.provisional || {};

        const incomeValidated = validated.income || {};
        const expenseValidated = validated.expense || {};
        const incomeProvisional = provisional.income || {};
        const expenseProvisional = provisional.expense || {};

        if (this.elements.dailyIncomeValidated) {
            this.elements.dailyIncomeValidated.textContent = formatAmount(
                incomeValidated.total || 0
            );
        }
        if (this.elements.dailyIncomeProvisional) {
            this.elements.dailyIncomeProvisional.textContent = formatAmount(
                incomeProvisional.total || 0
            );
        }
        if (this.elements.dailyExpenseValidated) {
            this.elements.dailyExpenseValidated.textContent = formatAmount(
                expenseValidated.total || 0
            );
        }
        if (this.elements.dailyExpenseProvisional) {
            this.elements.dailyExpenseProvisional.textContent = formatAmount(
                expenseProvisional.total || 0
            );
        }
    },

    renderTable: function (transactions) {
        const tbody = this.elements.transactionList;
        tbody.innerHTML = '';

        if (transactions.length === 0) {
            tbody.innerHTML = `<tr><td class="px-4 py-4 text-center text-slate-400">Sin transacciones recientes</td></tr>`;
            return;
        }

        const sorted = transactions.sort((a, b) => b.id - a.id).slice(0, 10);

        sorted.forEach(t => {
            const row = document.createElement('tr');
            const status = t.status || 'provisional';
            const isProvisional = status === 'provisional';
            const hasMerchant = !!(t.merchant && t.merchant.trim());

            let statusLabel = 'Pendiente';
            let statusClasses = 'bg-amber-100 text-amber-700';
            let merchantText = t.merchant || '—';
            let rowExtraClasses = '';

            if (status === 'verified' || status === 'verified_manual') {
                statusLabel = 'Validado';
                statusClasses = 'bg-emerald-100 text-emerald-700';
            }

            if (isProvisional && !hasMerchant) {
                rowExtraClasses = 'bg-red-50';
                merchantText = 'Falta Comercio';
                statusClasses = 'bg-red-100 text-red-700';
            }

            row.className = `border-b border-slate-50 last:border-0 hover:bg-slate-50 transition-colors ${rowExtraClasses}`;

            const dateStr = new Date(t.created_at).toLocaleDateString();

            row.innerHTML = `
                <td class="px-4 py-3">
                    <div class="font-medium text-slate-800">${t.concept}</div>
                    <div class="mt-0.5 flex items-center gap-2">
                        <span class="text-xs text-slate-400">${merchantText}</span>
                        <span class="text-[10px] px-2 py-0.5 rounded-full ${statusClasses}">${statusLabel}</span>
                    </div>
                </td>
                <td class="px-4 py-3 text-right">
                    <div class="font-bold text-slate-700">$${t.amount.toFixed(2)}</div>
                    <div class="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-500 inline-block mt-0.5">${t.category || '?'}</div>
                </td>
            `;
            tbody.appendChild(row);
        });
    },

    // Helpers
    updatePushToTalkUI: function () {
        const input = this.elements.pushToTalkToggle;
        if (!input) return;
        this.state.isPushToTalk = input.checked;
    },

    showSystemMessage: function (text) {
        const container = this.elements.chatContainer;
        const message = this.elements.chatMessage;
        if (container && message) {
            message.textContent = text;
            container.classList.remove('hidden');
        }
    },

    updateStatus: function (main, sub) {
        this.elements.statusText.textContent = main;
        if (sub) this.elements.subStatus.textContent = sub;
    },

    updateSubStatus: function (sub) {
        this.elements.subStatus.textContent = sub;
    },

    updateConnection: function (text, type) {
        const el = this.elements.connectionStatus;
        el.textContent = text;
        el.className = 'text-xs font-medium px-2 py-1 rounded ';
        if (type === 'success') el.classList.add('bg-green-100', 'text-green-600');
        else if (type === 'error') el.classList.add('bg-red-100', 'text-red-600');
        else el.classList.add('bg-slate-100', 'text-slate-400');
    }
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    app.init();
    // Expose for debug
    window.app = app;
});
