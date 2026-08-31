/**
 * God portraits for the fourteen chính tinh, keyed by `starKeyFromName`.
 *
 * The browser-ready WebP files are optimized copies of the source artwork in
 * `UI_test/images`; keeping the mapping here lets every UI surface use the
 * same star-to-deity pairing without depending on asset filenames.
 */
export interface GodPortrait {
  readonly src: string;
  readonly deity: string;
}

export const GOD_PORTRAITS: Readonly<Record<string, GodPortrait>> = {
  tuvi: { src: "/assets/gods/tuvi.webp", deity: "Zeus" },
  thienphu: {
    src: "/assets/gods/thienphu.webp",
    deity: "Hera",
  },
  thatsat: {
    src: "/assets/gods/thatsat.webp",
    deity: "Ares",
  },
  phaquan: {
    src: "/assets/gods/phaquan.webp",
    deity: "Prometheus",
  },
  thamlang: {
    src: "/assets/gods/thamlang.webp",
    deity: "Aphrodite",
  },
  thaiduong: {
    src: "/assets/gods/thaiduong.webp",
    deity: "Apollo",
  },
  thaiam: {
    src: "/assets/gods/thaiam.webp",
    deity: "Artemis",
  },
  vukhuc: {
    src: "/assets/gods/vukhuc.webp",
    deity: "Hermes",
  },
  liemtrinh: {
    src: "/assets/gods/liemtrinh.webp",
    deity: "Nemesis",
  },
  thienco: {
    src: "/assets/gods/thienco.webp",
    deity: "Athena",
  },
  thienluong: {
    src: "/assets/gods/thienluong.webp",
    deity: "Demeter",
  },
  thientuong: {
    src: "/assets/gods/thientuong.webp",
    deity: "Hades",
  },
  thiendong: {
    src: "/assets/gods/thiendong.webp",
    deity: "Dionysus",
  },
  cumon: {
    src: "/assets/gods/cumon.webp",
    deity: "Iris",
  },
};
