const TOOL_LABELS: Record<string, string> = {
  get_laso_foundation: "Đang xem nền tảng lá số",
  get_vong_thai_tue: "Đang tra cứu vòng Thái Tuế",
  get_cung_by_position: "Đang xem cung",
  get_cung_by_role: "Đang xem cung",
  get_list_cach_cuc: "Đang tra cứu cách cục",
  get_phu_tinh_tam_phuong_tu_chinh: "Đang tra cứu phụ tinh",
  get_trang_sinh: "Đang xem Tràng Sinh",
  get_tam_hop: "Đang xem Tam Hợp",
  get_xung_chieu: "Đang xem Xung Chiếu",
  get_star_description: "Đang tra cứu sao",
  get_star_role_interaction: "Đang tra cứu tương tác sao",
  get_tinh_cach_b3_b4_context: "Đang tra cứu tính cách",
  get_cung_analyze_skill: "Đang phân tích cung",
  run_tinh_cach_workflow: "Đang chạy workflow tính cách",
  read_book_tuvi_tan_bien: "Đang tra cứu Tử Vi Tân Biên",
  get_role_instruction: "Đang đọc hướng dẫn luận giải",
};

/**
 * A Vietnamese activity label for a streamed tool call, so the chat can show
 * what the agent is doing ("Đang tra cứu…") before the answer streams.
 */
export function toolStatusLabel(toolName: string): string {
  return TOOL_LABELS[toolName] ?? "Đang tra cứu";
}
