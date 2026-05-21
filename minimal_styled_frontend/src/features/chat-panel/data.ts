export interface ChatMessage {
  role: 'ai' | 'user';
  text: string;
}

export const DEMO_CHAT: ChatMessage[] = [
  {
    role: 'ai',
    text: 'Chào bạn. Mình đã đọc lá số của bạn — Âm Nữ tuổi Tân Mùi, Mệnh có Tử Vi tọa Ngọ, đắc địa. Bạn muốn hỏi điều gì hôm nay?',
  },
  {
    role: 'user',
    text: 'Năm nay sự nghiệp tôi có nên nhảy việc không?',
  },
  {
    role: 'ai',
    text: 'Theo lá số, năm nay cung Quan Lộc của bạn có Thiên Phủ – Liêm Trinh chiếu, là sao chủ về tiền tài và sự ổn định. Tuy nhiên Đại Hạn đang đi qua Tam Hợp Thân — đây thường là giai đoạn dịch chuyển.\n\nNếu nhảy việc, nên ưu tiên môi trường có quy củ, người lãnh đạo nữ hoặc ngành dịch vụ tài chính. Tránh ra quyết định lớn vào tháng 4 – 5 âm lịch.',
  },
  {
    role: 'user',
    text: 'Tháng nào trong năm hợp nhất để chuyển?',
  },
  {
    role: 'ai',
    text: 'Tháng 7 và tháng 9 âm lịch là cát lợi nhất. Tháng 7 có Lộc Tồn chiếu Mệnh, tháng 9 có Hóa Khoa — thuận cho ký kết, phỏng vấn, đàm phán.',
  },
];

export const QUICK_PROMPTS: string[] = [
  'Năm nay sự nghiệp của tôi ra sao?',
  'Tháng nào tốt để khởi sự?',
  'Tình duyên năm tới có chuyển biến gì?',
  'Tôi hợp ngành nghề nào?',
];

export const PLACEHOLDER_REPLY =
  'Theo lá số, cung tương ứng có Thiên Phủ – Thái Âm chiếu. Đây là điều thuận lợi nếu bạn giữ kiên nhẫn.';
