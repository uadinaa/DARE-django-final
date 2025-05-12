<template>
  <div class="chat-bot container mt-4">
    <div class="card bg-dark text-light">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">Чат-бот</h5>
        <span class="badge" :class="connectionStatusClass">{{ connectionStatus }}</span>
      </div>
      
      <div class="card-body">
        <div class="chat-messages" ref="messagesContainer">
          <div v-for="(message, index) in messages" :key="index" 
               :class="['message', message.type === 'user' ? 'message-user' : 'message-bot']">
            {{ message.text }}
          </div>
        </div>
      </div>

      <div class="card-footer">
        <form @submit.prevent="sendMessage" class="d-flex gap-2">
          <input 
            type="text" 
            v-model="newMessage" 
            class="form-control form-control-dark"
            placeholder="Введите сообщение..."
            :disabled="!isConnected"
          >
          <button 
            type="submit" 
            class="btn btn-success"
            :disabled="!isConnected || !newMessage.trim()"
          >
            Отправить
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';

const messages = ref([]);
const newMessage = ref('');
const isConnected = ref(false);
const connectionStatus = ref('Отключено');
const connectionStatusClass = ref('bg-danger');
const ws = ref(null);
const threadId = ref(null);
const messagesContainer = ref(null);

const connectWebSocket = () => {
  ws.value = new WebSocket('ws://127.0.0.1:8000/ws/assistant/create/');
  
  ws.value.onopen = () => {
    isConnected.value = true;
    connectionStatus.value = 'Подключено';
    connectionStatusClass.value = 'bg-success';
  };

  ws.value.onclose = () => {
    isConnected.value = false;
    connectionStatus.value = 'Отключено';
    connectionStatusClass.value = 'bg-danger';
  };

  ws.value.onmessage = (event) => {
    const data = JSON.parse(event.data);
    messages.value.push({
      type: 'bot',
      text: data.message
    });
    
    if (data.thread_id) {
      threadId.value = data.thread_id;
      ws.value.close();
      connectUpdateWebSocket();
    }
    
    scrollToBottom();
  };
};

const connectUpdateWebSocket = () => {
  ws.value = new WebSocket('ws://127.0.0.1:8000/ws/assistant/update/');
  
  ws.value.onopen = () => {
    isConnected.value = true;
    connectionStatus.value = 'Подключено';
    connectionStatusClass.value = 'bg-success';
  };

  ws.value.onclose = () => {
    isConnected.value = false;
    connectionStatus.value = 'Отключено';
    connectionStatusClass.value = 'bg-danger';
  };

  ws.value.onmessage = (event) => {
    const data = JSON.parse(event.data);
    messages.value.push({
      type: 'bot',
      text: data.response
    });
    scrollToBottom();
  };
};

const sendMessage = () => {
  if (!newMessage.value.trim() || !isConnected.value) return;

  const message = newMessage.value;
  messages.value.push({
    type: 'user',
    text: message
  });

  const payload = {
    message: message
  };

  if (threadId.value) {
    payload.thread_id = threadId.value;
  }

  ws.value.send(JSON.stringify(payload));
  newMessage.value = '';
  scrollToBottom();
};

const scrollToBottom = async () => {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

onMounted(() => {
  connectWebSocket();
});

onUnmounted(() => {
  if (ws.value) {
    ws.value.close();
  }
});
</script>

<style scoped>
.chat-messages {
  height: 400px;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  padding: 0.75rem;
  border-radius: 8px;
  max-width: 80%;
}

.message-user {
  background-color: var(--bs-success);
  align-self: flex-end;
}

.message-bot {
  background-color: var(--bs-secondary);
  align-self: flex-start;
}

.badge {
  font-size: 0.8rem;
  padding: 0.5rem;
}
</style> 