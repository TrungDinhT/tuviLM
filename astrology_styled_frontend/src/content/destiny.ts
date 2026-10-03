/**
 * Lá Bài Bản Mệnh content — the 39 possible chính tinh configurations of
 * cung Mệnh (1 vô chính diệu + 14 single + 24 song tinh), keyed by the
 * normalised, sorted star key from `menhStarKey()`.
 *
 * The key space is total by construction: a chart's Mệnh chính tinh set is
 * fully determined by (vị trí Tử Vi, vị trí Mệnh), and a sweep of the engine
 * observed all 144 pairs producing exactly these 39 keys. The vô chính diệu
 * fallback below is defence in depth, not a coverage gap — a card must never
 * render blank.
 *
 * Copy rule: archetype is a short tarot-style name; mantra is one sentence
 * in the card's voice. No birth-date arithmetic anywhere in the selection —
 * the key arrives from the chart, nowhere else.
 */

export interface DestinyEntry {
  /** The archetype chip on the main card. */
  readonly archetype: string;
  /** One-sentence mantra, rendered italic. */
  readonly mantra: string;
}

/** Key of the vô chính diệu entry — the normalised key of an empty Mệnh. */
export const VO_CHINH_DIEU_KEY = "vochinhdieu";

const VO_CHINH_DIEU_ENTRY: DestinyEntry = {
  archetype: "Người Tự Định Hình",
  mantra:
    "Mệnh trống không phải khoảng trống — đó là khoảng trời để ta tự định nghĩa mình là ai.",
};

export const DESTINY_ENTRIES: Record<string, DestinyEntry> = {
  [VO_CHINH_DIEU_KEY]: VO_CHINH_DIEU_ENTRY,

  // --- 14 đơn tinh ---------------------------------------------------------

  tuvi: {
    archetype: "Bậc Đế Vương",
    mantra: "Quyền lực lớn nhất là quyền làm chủ chính mình.",
  },
  thienphu: {
    archetype: "Người Giữ Kho",
    mantra: "Đầy kho không bằng vững lòng — ta là chỗ cả nhà dựa vào.",
  },
  thatsat: {
    archetype: "Vị Tướng Tiên Phong",
    mantra: "Ta đi trước, để đường sau lưng ta trở thành đường.",
  },
  phaquan: {
    archetype: "Người Phá Trận",
    mantra: "Phá vỡ không phải kết thúc; đó là cách ta bắt đầu lại từ đầu.",
  },
  thamlang: {
    archetype: "Người Khát Khao",
    mantra: "Khát khao là ngọn lửa — ta học cách giữ lửa, không để lửa giữ ta.",
  },
  thaiduong: {
    archetype: "Người Soi Sáng",
    mantra: "Mặt trời không xin phép ai để tỏa sáng.",
  },
  thaiam: {
    archetype: "Người Giữ Trăng",
    mantra: "Dịu dàng là một sức mạnh không cần chứng minh.",
  },
  vukhuc: {
    archetype: "Người Rèn Kim",
    mantra: "Ta tin vào điều đếm được, và làm cho điều đó đáng tin.",
  },
  liemtrinh: {
    archetype: "Người Giữ Lửa",
    mantra: "Kỷ luật và đam mê trong ta không đánh nhau — chúng cùng cháy.",
  },
  thienco: {
    archetype: "Người Vẽ Cơ",
    mantra: "Nhìn thấy con đường trước khi nó hiện ra là món quà của ta.",
  },
  thienluong: {
    archetype: "Người Che Chở",
    mantra: "Che chở người khác không làm ta nhỏ đi; nó làm ta cao hơn.",
  },
  thientuong: {
    archetype: "Người Mang Ấn",
    mantra: "Lời hứa của ta nặng như ấn triện — đó là lý do người ta tin.",
  },
  thiendong: {
    archetype: "Người Giữ Phúc",
    mantra: "Ta chọn hiền hoà không phải vì yếu, mà vì biết đủ.",
  },
  cumon: {
    archetype: "Người Mở Cánh Cửa",
    mantra: "Lời nói của ta là một cánh cửa — ta học cách mở đúng lúc.",
  },

  // --- 24 song tinh --------------------------------------------------------

  "thienphu+tuvi": {
    archetype: "Bậc Quân Chủ",
    mantra: "Ta không cần giành ngôi — ta xây nền, rồi ngôi tự đến.",
  },
  "thamlang+tuvi": {
    archetype: "Kẻ Chinh Phục",
    mantra: "Muốn nhiều không phải lỗi; ta biến muốn nhiều thành làm được nhiều.",
  },
  "thientuong+tuvi": {
    archetype: "Bậc Quyền Ấn",
    mantra: "Uy tín của ta được đóng dấu bằng hành động, không bằng lời.",
  },
  "thatsat+tuvi": {
    archetype: "Bậc Khai Quốc",
    mantra: "Ta ra lệnh cho bản thân trước — thế giới nghe theo sau.",
  },
  "phaquan+tuvi": {
    archetype: "Người Khai Hoàng",
    mantra: "Ta dám phá cả những gì mình từng xây, để xây lại cho đúng.",
  },
  "phaquan+vukhuc": {
    archetype: "Người Đổi Vận",
    mantra: "Ta dám bỏ cả vốn lẫn vị thế để đổi lấy vận mới.",
  },
  "thienphu+vukhuc": {
    archetype: "Bậc Trữ Tài",
    mantra: "Tiền đến rồi ở lại với ta, vì ta coi trọng từng đồng một.",
  },
  "thamlang+vukhuc": {
    archetype: "Người Săn Tài",
    mantra: "Ta săn cơ hội bằng cả khát khao lẫn bản lĩnh.",
  },
  "thatsat+vukhuc": {
    archetype: "Vị Tướng Kiếm Kim",
    mantra: "Quyết định của ta nhanh nhưng không hời — kiếm sắc vì đã qua lò rèn.",
  },
  "thientuong+vukhuc": {
    archetype: "Người Định Giá",
    mantra: "Ta biết giá của tiền, và biết giá của chữ tín.",
  },
  "liemtrinh+thienphu": {
    archetype: "Người Giữ Thành",
    mantra: "Trong thành có kho, quanh thành có lửa — ta vừa giữ, vừa bảo vệ.",
  },
  "liemtrinh+thatsat": {
    archetype: "Vị Kiên Tướng",
    mantra: "Ta cứng với mục tiêu, và cứng hơn nữa với chính mình.",
  },
  "liemtrinh+thientuong": {
    archetype: "Bậc Chính Ấn",
    mantra: "Ta sống ngay thẳng đến mức người khác lấy ta làm thước.",
  },
  "liemtrinh+thamlang": {
    archetype: "Người Đam Mê",
    mantra: "Đam mê của ta không tản ra — nó hội tụ thành một mũi nhọn.",
  },
  "liemtrinh+phaquan": {
    archetype: "Người Phá Lập",
    mantra: "Ta phá luật cũ rồi tự đặt luật mới, nghiêm khắc hơn.",
  },
  "thaiam+thaiduong": {
    archetype: "Người Hai Vầng Sáng",
    mantra: "Ta mang cả mặt trời lẫn mặt trăng — biết rực rỡ, biết dịu dàng.",
  },
  "thaiduong+thienluong": {
    archetype: "Người Nắng Ấm",
    mantra: "Ta tỏa sáng để sưởi ấm, không phải để thiêu đốt.",
  },
  "cumon+thaiduong": {
    archetype: "Người Nói Ánh Sáng",
    mantra: "Lời ta như nắng — thẳng, rõ, và khiến mọi thứ lộ ra.",
  },
  "thaiam+thienco": {
    archetype: "Người Trăng Trí",
    mantra: "Trí tuệ của ta lên như trăng — lặng lẽ mà soi khắp.",
  },
  "thaiam+thiendong": {
    archetype: "Người Nước Hiền",
    mantra: "Ta mềm như nước; và như nước, không gì mài được ta.",
  },
  "cumon+thiendong": {
    archetype: "Người Lời Hiền",
    mantra: "Ta nói ít hơn một chút, để lời nói ra đáng nghe hơn.",
  },
  "cumon+thienco": {
    archetype: "Người Biện Cơ",
    mantra: "Ta thấy kẽ hở trong lập luận như thấy kẽ hở trong bức tường.",
  },
  "thienco+thienluong": {
    archetype: "Người Mưu Đức",
    mantra: "Mưu trí dùng để giúp người mới là mưu trí bền.",
  },
  "thiendong+thienluong": {
    archetype: "Người Phúc Ấm",
    mantra: "Phúc của ta không ồn ào — nó như bếp lửa, ấm lâu.",
  },
};

/**
 * The entry for a Mệnh chính tinh key. An unknown key falls back to the vô
 * chính diệu entry rather than rendering blank — unreachable given the
 * table's totality, so a future backend change cannot empty the card.
 */
export function destinyFor(starKey: string): DestinyEntry {
  return DESTINY_ENTRIES[starKey] ?? VO_CHINH_DIEU_ENTRY;
}
