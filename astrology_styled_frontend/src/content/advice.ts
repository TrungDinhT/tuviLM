import type { AmDuongRelation, MenhCucRelation } from "@/lib/api/schemas";

/**
 * Lời Khuyên — ten entries keyed by (Mệnh–Cục relation, âm dương polarity).
 *
 * Adapted from the agent's own reviewed prose, not authored from scratch:
 * `_RELATION_LENS` meanings (`src/agent/tool/ban_menh/ban_menh_meaning.py`)
 * supply the relation's reading, and `_YEAR_MENH_POLARITY_LENS.development_focus`
 * (`laso_foundation.py`) supplies the advice axis — reworded here into card
 * voice so the card and the future Hỏi AI tell the same chart one story.
 *
 * The Record's key type is total: TypeScript rejects a missing pair at
 * compile time, and the test re-asserts all ten resolve.
 */

export type AdviceKey = `${MenhCucRelation}:${AmDuongRelation}`;

export interface AdviceEntry {
  /** The short key phrase heading the card. */
  readonly phrase: string;
  /** The advice body, two to three sentences. */
  readonly advice: string;
}

export const ADVICE_ENTRIES: Record<AdviceKey, AdviceEntry> = {
  "sinh_xuat:thuan_ly": {
    phrase: "Tiên phong, nhưng có chừng mực",
    advice:
      "Vận của bạn do chính mình tạo ra — hành động trước, hoàn cảnh sẽ biến đổi theo. Nền thuận lý cho bạn đà tiến nhanh, nên thứ cần rèn duy nhất là sự tiết chế: quyết liệt vừa đủ để đường đi không gây tổn hại cho người xung quanh.",
  },
  "sinh_xuat:nghich_ly": {
    phrase: "Tự thân vận động",
    advice:
      "Hoàn cảnh không tự đổi theo ý bạn — bạn là người phải hành động trước. Bối cảnh đầu đời có thể không thuận, nhưng chính vì vậy rèn được sức vượt khó; lấy dĩ hòa vi quý làm lối đi.",
  },
  "sinh_nhap:thuan_ly": {
    phrase: "Được nâng, đừng ỷ lại",
    advice:
      "Bạn là người được hoàn cảnh hỗ trợ và ưu đãi, đà tiến vì thế thuận hơn người khác. Giữ nhịp quyết liệt của mình ở mức vừa phải — sự dễ dãi đáng sợ hơn nghịch cảnh.",
  },
  "sinh_nhap:nghich_ly": {
    phrase: "May mắn đến theo cách lạ",
    advice:
      "Bạn được hoàn cảnh đỡ, nhưng thường theo cách không giống mình tưởng tượng. Mở lòng với sự khác biệt quanh mình — hòa hợp với nó là cách lộc trời thật sự chảy về.",
  },
  "khac_xuat:thuan_ly": {
    phrase: "Người cải cách",
    advice:
      "Bạn có sức thay đổi môi trường quanh mình, và nền thuận lý khiến điều đó dễ được công nhận. Sức mạnh ấy cần đi cùng sự đúng đắn — cải cách để xây, không phải để thắng.",
  },
  "khac_xuat:nghich_ly": {
    phrase: "Thay đổi từ trong ra ngoài",
    advice:
      "Bạn sinh ra để cải cách môi trường, nhưng môi trường ban đầu có thể chưa đồng điệu với bạn. Đừng ép nó đổi theo mình — hàm dưỡng sự mềm để sức thay đổi của bạn được lắng nghe.",
  },
  "khac_nhap:thuan_ly": {
    phrase: "Bị ép, nhưng không bị bẻ",
    advice:
      "Hoàn cảnh đặt áp lực lên bản tính của bạn; may mà nền thuận lý giữ bạn đứng thẳng. Tiết chế phản ứng quyết liệt và chọn trận đánh đáng đánh — không phải trận nào cũng cần thắng.",
  },
  "khac_nhap:nghich_ly": {
    phrase: "Rèn qua nghịch cảnh",
    advice:
      "Hoàn cảnh gây khó khăn và buộc bạn phải đổi để thích nghi — đó là lò rèn thật sự của bạn. Học cách hoá giải bất hòa giữa người với người; sự bền bỉ rèn từ nghịch cảnh là thứ không ai lấy được.",
  },
  "binh_hoa:thuan_ly": {
    phrase: "Ngang hàng, tự do",
    advice:
      "Mệnh và hoàn cảnh không chi phối nhau — bạn tự do chọn hướng đi của mình. Nền thuận lý giúp đường đi thẳng; rèn cách sống đúng đắn để tự do ấy không trôi thành phóng túng.",
  },
  "binh_hoa:nghich_ly": {
    phrase: "Cân bằng là nghệ thuật",
    advice:
      "Không bên nào ép bên nào giữa bạn và hoàn cảnh, nhưng hai bên cũng chẳng tự nhiên đồng điệu. Hàm dưỡng bản thân và xử lý khéo sự bất hòa — cân bằng là thứ bạn tự tạo, không phải thứ có sẵn.",
  },
};

export function adviceFor(
  relation: MenhCucRelation,
  polarity: AmDuongRelation,
): AdviceEntry {
  return ADVICE_ENTRIES[`${relation}:${polarity}`];
}
