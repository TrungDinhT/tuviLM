/** A deliberately low-detail deity form rendered behind the bright stars. */
export interface GodSilhouette {
  readonly deity: string;
  readonly fillPaths: readonly string[];
  readonly detailPaths: readonly string[];
  readonly symbolPaths: readonly string[];
}

const HEAD = "M44 22 C44 16 47 12 52 12 C58 12 61 17 60 23 C59 29 56 32 51 32 C46 31 43 27 44 22 Z";
const CROWNED_HEAD =
  "M43 22 C43 17 46 13 51 13 C57 13 60 17 60 23 C59 28 56 31 51 31 C46 31 43 27 43 22 Z M44 15 L46 9 L50 14 L53 8 L56 15 L60 11 L59 19 Z";
const FEMININE_ROBE =
  "M39 32 Q50 28 62 33 Q60 44 58 55 Q66 70 72 90 Q53 96 30 91 Q37 73 41 56 Q36 45 39 32 Z";
const MASCULINE_ROBE =
  "M38 32 Q50 27 64 34 Q60 45 59 56 Q67 71 72 91 Q53 96 31 91 Q37 72 41 56 Q35 45 38 32 Z";
const WARRIOR_BODY =
  "M37 33 Q50 27 65 34 L61 53 L68 68 L63 90 L55 90 L51 67 L44 68 L38 91 L31 90 L36 65 L41 53 Z";
const FLYING_BODY =
  "M39 35 Q51 28 63 36 L59 52 L68 63 L61 69 L53 59 L45 61 L38 77 L31 74 L37 55 L30 48 Z";
const ROBE_FOLDS = "M44 48 Q47 61 40 84 M51 49 L50 89 M57 49 Q56 65 64 85 M37 89 Q51 84 68 90";
const BODY_DETAILS = "M43 34 Q50 39 59 34 M42 43 Q50 47 59 43 M42 55 Q50 59 59 55";

/**
 * Small inline-vector portraits for the fourteen chính tinh. The forms share a
 * few body paths but use distinct pose lines and symbols so they remain
 * recognizable without downloading bitmap artwork.
 */
export const GOD_SILHOUETTES: Readonly<Record<string, GodSilhouette>> = {
  tuvi: {
    deity: "Zeus",
    fillPaths: [CROWNED_HEAD, MASCULINE_ROBE],
    detailPaths: [
      BODY_DETAILS,
      ROBE_FOLDS,
      "M40 35 Q31 31 28 24 M61 36 Q68 42 68 53 M43 28 Q49 35 58 28",
    ],
    symbolPaths: ["M23 7 L29 18 L24 20 L32 27 L27 28 L34 39 L20 25 L25 23 L18 16 L24 15 Z"],
  },
  thienphu: {
    deity: "Hera",
    fillPaths: [CROWNED_HEAD, FEMININE_ROBE],
    detailPaths: [
      BODY_DETAILS,
      ROBE_FOLDS,
      "M39 36 Q31 39 29 52 M61 36 Q68 42 72 51 M44 28 Q51 34 58 28",
    ],
    symbolPaths: [
      "M28 12 L28 87 M24 17 Q28 8 32 17 M25 23 L31 23",
      "M70 52 Q76 47 79 53 Q75 58 70 56 M76 54 L77 83",
    ],
  },
  thatsat: {
    deity: "Ares",
    fillPaths: [CROWNED_HEAD, WARRIOR_BODY],
    detailPaths: [
      "M39 36 L31 47 L36 58 M63 36 L70 46 L66 57 M40 51 Q50 56 61 51 M35 66 L51 65 L65 67",
      "M45 31 L41 46 M58 31 L61 46",
    ],
    symbolPaths: [
      "M24 9 L31 83 M20 17 L24 8 L29 15",
      "M69 36 Q82 42 78 58 Q74 70 64 63 Q60 50 69 36 Z M67 48 L76 55 M76 47 L67 58",
    ],
  },
  phaquan: {
    deity: "Prometheus",
    fillPaths: [HEAD, MASCULINE_ROBE],
    detailPaths: [
      BODY_DETAILS,
      ROBE_FOLDS,
      "M40 36 Q31 34 29 27 M61 35 Q70 39 78 45 M43 28 Q50 35 58 28",
    ],
    symbolPaths: [
      "M81 44 C73 37 78 31 82 27 C81 34 89 34 87 42 C86 47 82 50 78 47 C82 47 84 45 81 44 Z",
      "M79 46 Q82 59 78 70",
    ],
  },
  thamlang: {
    deity: "Aphrodite",
    fillPaths: [HEAD, FEMININE_ROBE],
    detailPaths: [
      BODY_DETAILS,
      ROBE_FOLDS,
      "M40 35 Q32 37 27 46 M61 35 Q67 40 72 54 M43 27 Q50 34 58 27 M58 21 Q65 28 62 38",
    ],
    symbolPaths: [
      "M24 38 C18 38 18 47 24 48 C31 48 31 38 24 38 Z M24 48 L25 58",
      "M68 75 Q75 68 80 75 Q76 82 68 81 Q72 78 68 75 Z",
    ],
  },
  thaiduong: {
    deity: "Apollo",
    fillPaths: [HEAD, MASCULINE_ROBE],
    detailPaths: [
      BODY_DETAILS,
      ROBE_FOLDS,
      "M40 36 Q32 37 31 49 M61 36 Q69 41 72 52 M43 28 Q51 34 58 28",
    ],
    symbolPaths: [
      "M51 7 L51 2 M40 10 L36 5 M62 10 L66 5 M34 18 L28 16 M68 18 L74 16 M34 27 L28 30 M68 27 L74 30 M40 34 L36 39 M62 34 L66 39 M35 21 A16 16 0 1 1 67 21 A16 16 0 1 1 35 21",
      "M28 40 Q18 54 30 62 Q39 57 33 44 M25 46 L35 57 M22 51 L33 51",
    ],
  },
  thaiam: {
    deity: "Artemis",
    fillPaths: [HEAD, FEMININE_ROBE],
    detailPaths: [
      BODY_DETAILS,
      ROBE_FOLDS,
      "M40 35 Q33 36 31 46 M61 35 Q70 37 76 40 M43 27 Q50 34 58 27",
    ],
    symbolPaths: [
      "M76 9 Q94 35 79 66 Q74 75 66 79 Q84 55 82 36 Q81 22 76 9 Z",
      "M38 39 L85 39 M80 35 L86 39 L80 43 M72 12 Q89 38 69 69",
    ],
  },
  vukhuc: {
    deity: "Hermes",
    fillPaths: [HEAD, FLYING_BODY],
    detailPaths: [
      "M39 37 Q30 38 27 48 M62 37 Q70 43 74 53 M43 53 Q49 58 57 54 M39 61 L31 76 M55 59 L65 71",
      "M45 15 L38 10 L42 20 M57 15 L64 10 L60 20 M31 74 L22 72 L29 80 M63 69 L71 66 L66 76",
    ],
    symbolPaths: [
      "M26 8 L28 57 M20 15 Q28 8 36 15 M22 23 Q35 27 24 34 Q15 39 27 45 Q38 50 25 56 M34 23 Q21 27 32 34 Q41 39 29 45 Q18 50 31 56",
      "M25 7 L29 3 L32 8 L28 11 Z",
    ],
  },
  liemtrinh: {
    deity: "Nemesis",
    fillPaths: [HEAD, FEMININE_ROBE],
    detailPaths: [
      BODY_DETAILS,
      ROBE_FOLDS,
      "M40 35 Q32 38 27 44 M61 35 Q68 38 72 45 M43 27 Q50 34 58 27",
    ],
    symbolPaths: [
      "M27 11 L27 55 M17 24 L37 24 M18 24 Q18 35 13 38 Q8 34 8 24 M36 24 Q36 35 41 38 Q46 34 46 24 M11 39 L15 39 M39 39 L43 39",
      "M71 40 L64 88 M68 43 L75 39 M62 88 L67 88",
    ],
  },
  thienco: {
    deity: "Athena",
    fillPaths: [CROWNED_HEAD, WARRIOR_BODY],
    detailPaths: [
      "M39 36 L30 45 L35 56 M63 36 L70 45 L66 56 M41 51 Q50 55 61 51 M35 66 L51 65 L65 67",
      "M44 30 L39 47 M58 30 L62 47",
    ],
    symbolPaths: [
      "M24 8 L29 85 M20 16 L24 7 L29 15",
      "M68 39 Q81 43 78 59 Q74 70 64 63 Q61 49 68 39 Z M67 48 L76 55 M75 47 L67 59",
      "M22 72 Q15 67 12 74 Q15 82 22 77 M16 72 L16 81",
    ],
  },
  thienluong: {
    deity: "Demeter",
    fillPaths: [CROWNED_HEAD, FEMININE_ROBE],
    detailPaths: [
      BODY_DETAILS,
      ROBE_FOLDS,
      "M40 35 Q32 38 28 48 M61 35 Q67 40 72 51 M43 27 Q50 34 58 27",
    ],
    symbolPaths: [
      "M27 12 L28 57 M28 19 L20 14 M28 25 L36 18 M28 32 L19 27 M28 39 L37 31 M28 46 L20 42",
      "M70 72 Q80 68 84 76 Q80 86 67 82 Z M69 73 Q75 78 82 75",
    ],
  },
  thientuong: {
    deity: "Hades",
    fillPaths: [CROWNED_HEAD, MASCULINE_ROBE],
    detailPaths: [
      BODY_DETAILS,
      ROBE_FOLDS,
      "M40 35 Q32 38 29 48 M61 35 Q68 40 70 52 M43 27 Q50 34 58 27",
    ],
    symbolPaths: [
      "M26 12 L27 89 M18 17 Q20 8 26 17 Q32 8 35 17 M18 17 L18 26 M35 17 L35 26",
      "M71 70 Q76 62 81 70 Q87 62 91 71 Q88 80 82 78 Q77 83 70 78 Z M75 69 L73 63 M82 69 L82 62 M88 70 L91 65",
    ],
  },
  thiendong: {
    deity: "Dionysus",
    fillPaths: [CROWNED_HEAD, MASCULINE_ROBE],
    detailPaths: [
      BODY_DETAILS,
      ROBE_FOLDS,
      "M40 35 Q31 36 28 43 M61 35 Q68 39 73 49 M43 27 Q50 34 58 27",
    ],
    symbolPaths: [
      "M23 12 L34 12 Q34 21 29 24 L29 31 M24 31 L34 31 M20 12 Q21 19 29 20 Q37 19 38 12",
      "M72 48 C78 44 84 49 82 55 C87 59 82 66 77 63 C73 68 67 63 70 58 C65 54 68 48 72 48 Z",
    ],
  },
  cumon: {
    deity: "Iris",
    fillPaths: [HEAD, FEMININE_ROBE],
    detailPaths: [
      BODY_DETAILS,
      ROBE_FOLDS,
      "M40 35 Q32 34 28 27 M61 35 Q68 40 71 52 M43 27 Q50 34 58 27",
    ],
    symbolPaths: [
      "M25 8 C20 13 21 18 26 21 C30 18 31 13 25 8 Z M26 21 L28 58",
      "M68 63 Q79 52 88 61 Q83 75 69 76 M71 65 Q78 66 85 61 M71 70 Q78 72 84 67",
    ],
  },
};
