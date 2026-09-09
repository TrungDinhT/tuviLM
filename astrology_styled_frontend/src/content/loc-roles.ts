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
  Mệnh: "may mắn đến từ chính con người và quyết định của bạn",
  "Phụ Mẫu": "bạn được người lớn, thầy cô và bề trên đỡ đầu",
  "Phúc Đức": "phúc phần của bạn nằm ở sự an nhiên trong tâm trí",
  "Điền Trạch": "nhà cửa và tài sản là nền may mắn lâu dài của bạn",
  "Quan Lộc": "công việc chính là nơi vận may của bạn đổ về",
  "Nô Bộc": "bạn được nâng lên nhờ bạn bè và người đi theo mình",
  "Thiên Di": "ra ngoài, đi xa, đổi môi trường là mở được vận may",
  "Tật Ách": "sức khỏe được chăm tốt chính là nguồn lộc của bạn",
  "Tài Bạch": "vận may của bạn đi thẳng vào khả năng kiếm và giữ tiền",
  "Tử Tức": "thế hệ sau và những gì bạn tạo ra đem lộc về",
  "Phu Thê": "người bạn đời là cánh cửa đưa may mắn vào đời bạn",
  "Huynh Đệ": "anh chị em, bạn ngang hàng chính là quý nhân của bạn",
};

/** Blurb for a cung role; empty string only when the role is unknown. */
export function locRoleBlurb(role: string): string {
  return LOC_ROLE_BLURBS[role] ?? "";
}
