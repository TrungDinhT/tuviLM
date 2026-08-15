import { z } from "zod";

function isValidCalendarDate(year: number, month: number, day: number): boolean {
  const d = new Date(year, month - 1, day);
  return (
    d.getFullYear() === year &&
    d.getMonth() === month - 1 &&
    d.getDate() === day
  );
}

export const EntryFormSchema = z
  .object({
    calendar: z.enum(["duong", "am"]),
    day: z
      .number({ message: "Ngày phải là số" })
      .int("Ngày phải là số nguyên")
      .min(1, "Ngày không hợp lệ")
      .max(31, "Ngày không hợp lệ"),
    month: z
      .number({ message: "Tháng phải là số" })
      .int("Tháng phải là số nguyên")
      .min(1, "Tháng không hợp lệ")
      .max(12, "Tháng không hợp lệ"),
    year: z
      .number({ message: "Năm phải là số" })
      .int("Năm phải là số nguyên")
      .min(700, "Năm chỉ tính từ 700 đến 2100")
      .max(2100, "Năm chỉ tính từ 700 đến 2100"),
    hour: z
      .number({ message: "Vui lòng nhập giờ sinh" })
      .int("Giờ phải là số nguyên")
      .min(0, "Vui lòng nhập giờ sinh trong khoảng 0 đến 23")
      .max(23, "Vui lòng nhập giờ sinh trong khoảng 0 đến 23"),
    minute: z
      .number({ message: "Vui lòng nhập phút sinh" })
      .int("Phút phải là số nguyên")
      .min(0, "Vui lòng nhập phút sinh trong khoảng 0 đến 59")
      .max(59, "Vui lòng nhập phút sinh trong khoảng 0 đến 59"),
    hour_in_dia_chi: z.enum([
      "ty",
      "suu",
      "dan",
      "meo",
      "thin",
      "ti",
      "ngo",
      "mui",
      "than",
      "dau",
      "tuat",
      "hoi",
    ]),
    is_leap_month: z.boolean(),
    gender: z.enum(["M", "F"]),
  })
  .superRefine((v, ctx) => {
    if (v.calendar === "duong" && !isValidCalendarDate(v.year, v.month, v.day)) {
      ctx.addIssue({
        code: "custom",
        path: ["day"],
        message: `Ngày ${v.day}/${v.month}/${v.year} không tồn tại`,
      });
    }
  });

export type EntryFormParsed = z.infer<typeof EntryFormSchema>;
