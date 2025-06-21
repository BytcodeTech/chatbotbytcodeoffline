document.addEventListener("DOMContentLoaded", () => {
    const chatToggle = document.getElementById('chat-toggle');
    const chatWidget = document.getElementById('chat-widget');
    const messagesContainer = document.getElementById('chat-messages');
    const inputField = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-btn');
    const botSelector = document.getElementById('bot-selector');

    // --- LÓGICA PARA CARGAR BOTS EN EL SELECTOR ---
    async function loadBots() {
        try {
            // Este mensaje DEBE aparecer en tu consola (F12)
            console.log("Intentando cargar bots desde /bots...");
            
            const response = await fetch('/bots');
            
            if (!response.ok) {
                throw new Error(`Error en la petición de red: Estado ${response.status}`);
            }
            
            const bots = await response.json();
            console.log("Bots recibidos del backend:", bots);

            botSelector.innerHTML = ''; // Limpiar opciones

            if (Object.keys(bots).length === 0) {
                throw new Error("El archivo de configuración de bots está vacío o no se encontró.");
            }

            for (const botId in bots) {
                const option = document.createElement('option');
                option.value = botId;
                option.textContent = bots[botId].bot_name;
                botSelector.appendChild(option);
            }
            console.log("Selector de bots poblado exitosamente.");

        } catch (error) {
            console.error("Error crítico al cargar la lista de bots:", error);
            botSelector.innerHTML = '<option value="">Error al cargar</option>';
        }
    }
    
    // Cargar los bots en cuanto el documento esté listo
    loadBots();

    // --- LÓGICA DEL CHAT ---
    chatToggle.addEventListener('click', () => {
        chatWidget.classList.toggle('hidden');
        if (!chatWidget.classList.contains('hidden')) {
            inputField.focus();
        }
    });

    sendButton.addEventListener('click', sendMessage);
    inputField.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendMessage();
        }
    });

    function sendMessage() {
        const userQuery = inputField.value.trim();
        if (userQuery === "") return;

        const selectedBotId = botSelector.value;
        if (!selectedBotId || botSelector.firstChild.value === "") {
            alert("Error: No hay un asistente válido seleccionado.");
            return;
        }

        addMessage(userQuery, 'user');
        inputField.value = "";
        streamMessageFromBot(userQuery, selectedBotId);
    }

    async function streamMessageFromBot(query, botId) {
        const botMessageDiv = addMessage('', 'bot');
        botMessageDiv.innerHTML = '<span class="blinking-cursor"></span>';
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: "web_user_01",
                    query: query,
                    bot_id: botId
                })
            });

            if (!response.ok) { throw new Error('Error del servidor al chatear.'); }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullResponse = "";
            botMessageDiv.innerHTML = "";

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                const textChunk = decoder.decode(value, { stream: true });
                fullResponse += textChunk;
                botMessageDiv.innerHTML = fullResponse.replace(/\n/g, '<br>');
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }

        } catch (error) {
            console.error('Error al contactar al bot:', error);
            botMessageDiv.textContent = 'Lo siento, no puedo responder en este momento.';
        }
    }

    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        messageDiv.textContent = text;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        return messageDiv;
    }
});