/**
 * Where the user's lộc sits — one blurb per cung role, consumed for both
 * Hóa Lộc and Lộc Tồn on the Vận May card.
 *
 * Keyed by the backend's cung role string (a stable contract value), so a
 * reworded blurb never changes which role it attaches to. The blurb names
 * what that role means as a place for lộc; it must read the same whether the
 * star arriving there is Hóa Lộc or Lộc Tồn.
 */

export const LOC_ROLE_BLURBS: Record<string, string> = {
  Mệnh: "Lộc nằm ngay tại bản thân bạn — may mắn đến từ chính con người và quyết định của bạn.",
  "Phụ Mẫu": "Lộc nằm ở cung cha mẹ — bạn được đỡ đầu bởi người lớn, thầy cô và bề trên.",
  "Phúc Đức": "Lộc nằm ở cung phúc khí — phúc phần của bạn nằm ở sự an nhiên trong tâm trí.",
  "Điền Trạch": "Lộc nằm ở cung nhà đất — tài sản và chỗ ở là nền may mắn lâu dài của bạn.",
  "Quan Lộc": "Lộc nằm ở cung sự nghiệp — công việc chính là nơi vận may của bạn đổ về.",
  "Nô Bộc": "Lộc nằm ở cung bạn bè — bạn được nâng lên nhờ bạn bè, đồng nghiệp và người đi theo mình.",
  "Thiên Di": "Lộc nằm ở cung thiên di — ra ngoài, đi xa, đổi môi trường là mở được vận may.",
  "Tật Ách": "Lộc nằm ở cung sức khỏe — cơ thể và tinh thần được chăm tốt chính là nguồn lộc của bạn.",
  "Tài Bạch": "Lộc nằm ở cung tiền bạc — vận may của bạn đi thẳng vào khả năng kiếm và giữ tiền.",
  "Tử Tức": "Lộc nằm ở cung con cái — thế hệ sau và những gì bạn tạo ra đem lộc về cho bạn.",
  "Phu Thê": "Lộc nằm ở cung hôn nhân — người bạn đời là cánh cửa đưa may mắn vào đời bạn.",
  "Huynh Đệ": "Lộc nằm ở cung anh chị em — người ngang hàng quanh bạn chính là quý nhân của bạn.",
};

/** Blurb for a cung role; empty string only when the role is unknown. */
export function locRoleBlurb(role: string): string {
  return LOC_ROLE_BLURBS[role] ?? "";
}
