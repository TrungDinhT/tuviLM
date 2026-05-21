export interface ChatMessage {
  role: 'ai' | 'user';
  text: string;
  status?: 'ok' | 'pending' | 'error';
}

export const INITIAL_GREETING: ChatMessage = {
  role: 'ai',
  text: 'Chào bạn. Mình đã đọc lá số của bạn. Bạn muốn hỏi điều gì hôm nay?',
};

export const QUICK_PROMPTS: string[] = [
  'Năm nay sự nghiệp của tôi ra sao?',
  'Tháng nào tốt để khởi sự?',
  'Tình duyên năm tới có chuyển biến gì?',
  'Tôi hợp ngành nghề nào?',
];
