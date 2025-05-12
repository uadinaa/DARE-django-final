// src/utils/dateFormatter.js (пример)
export function formatPostDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffSeconds = Math.round((now - date) / 1000);
    const diffMinutes = Math.round(diffSeconds / 60);
    const diffHours = Math.round(diffMinutes / 60);
    const diffDays = Math.round(diffHours / 24);
  
    if (diffSeconds < 60) {
      return "сейчас";
    } else if (diffMinutes < 60) {
      return `${diffMinutes} м.`;
    } else if (diffHours < 24) {
      return `${diffHours} ч.`;
    } else if (diffDays <= 365) {
      // Форматирование "ДД МММ." (напр., "28 окт.")
      return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
    } else {
      // Форматирование "ДД МММ. ГГГГ" (напр., "30 апр. 2024")
      return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' });
    }
  }

  export function formatPostDetailDate(dateString) {
    if (!dateString) return '';
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) {
        return "Некорр. дата";
      }
      // "ЧЧ:ММ, ДД МММ. ГГГГ"
      const options = {
        hour: '2-digit',
        minute: '2-digit',
        day: 'numeric',
        month: 'short',
        year: 'numeric',
      };
      let formatted = new Intl.DateTimeFormat('ru-RU', options).format(date);
      // Intl.DateTimeFormat может добавлять " г." после года, уберем если есть
      formatted = formatted.replace(/\s*г\.$/, '');
      return formatted;
    } catch (e) {
      console.error("Error formatting detail date:", e);
      return "Ошибка даты";
    }
  }