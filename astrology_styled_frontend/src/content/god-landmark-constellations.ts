import type { GodConstellation, GodConstellationPoint } from "./god-constellations";

type Landmark = readonly [name: string, x: number, y: number, power?: number];

/**
 * Convert named, hand-picked landmarks into the compact indexed data consumed
 * by the SVG renderer. Keeping names here makes individual joints and divine
 * symbols straightforward to tune against the reference portraits.
 */
function createConstellation<const T extends readonly Landmark[]>(
  landmarks: T,
  links: readonly (readonly [T[number][0], T[number][0]])[],
): GodConstellation {
  const indexes = new Map<string, number>(landmarks.map(([name], index) => [name, index]));

  return {
    points: landmarks.map(([, x, y, power]) =>
      power === undefined
        ? ([x, y] as GodConstellationPoint)
        : ([x, y, power] as GodConstellationPoint),
    ),
    lines: links.map(([from, to]) => {
      const fromIndex = indexes.get(from);
      const toIndex = indexes.get(to);
      if (fromIndex === undefined || toIndex === undefined) {
        throw new Error(`Unknown god landmark link: ${from} -> ${to}`);
      }
      return [fromIndex, toIndex] as const;
    }),
  };
}

/**
 * Anatomical and symbolic constellations traced by hand over the fourteen
 * portraits in `UI_test/image_processed/lighter`. Unlike the former contour
 * sampler, these links describe a figure: head, shoulders, articulated limbs,
 * stance, and the deity's identifying object.
 */
export const GOD_LANDMARK_CONSTELLATIONS: Readonly<Record<string, GodConstellation>> = {
  tuvi: createConstellation(
    [
      // Ordered as marked in zeus_with_stars.svg; coordinates include
      // the horizontal padding from displaying its portrait with `contain`.
      ["crownLeft", 44.1032, 16.939],
      ["crownInnerLeft", 46.4248, 19.5185, 1.4],
      ["crownInnerRight", 51.6698, 19.4325, 1.4],
      ["crownRight", 54.9372, 17.2829],
      ["lightningHand", 26.8203, 15.9071, 1.4],
      ["lightningTip", 32.4953, 3.2674, 1.2],
      ["lightningLower", 18.3078, 26.9991, 1.25],
      ["rightShoulder", 57.0009, 34.5658, 1.15],
      ["robeLower", 53.4755, 67.0679, 1.2],
    ],
    [
      ["crownLeft", "crownInnerLeft"],
      ["crownInnerLeft", "crownInnerRight"],
      ["crownInnerRight", "crownRight"],
      ["crownRight", "crownLeft"],
      ["lightningTip", "lightningHand"],
      ["lightningHand", "lightningLower"],
      ["rightShoulder", "robeLower"],
    ],
  ),

  thienphu: createConstellation(
    [
      // Ordered as marked in hera_with_stars.svg; coordinates include
      // the horizontal padding from displaying its portrait with `contain`.
      ["crownLeft", 44.7709, 12.8117, 1.1],
      ["crownCenter", 50.4459, 12.5537, 1.3],
      ["crownRight", 53.8853, 15.7352, 1.1],
      ["scepterCrown", 25.4244, 9.1144, 1.8],
      ["scepterHand", 29.5516, 32.3302, 1.2],
      ["chest", 44.083, 40.6707],
      ["peacockTailUpperRight", 81.2283, 57.1797],
      ["peacockTailMidLeft", 74.4356, 68.7016, 1.2],
      ["peacockTailLowerRight", 83.6359, 82.3732],
      ["peacockTailMidRight", 85.1836, 74.2046],
      ["peacockTailTip", 80.6264, 88.994, 1.1],
    ],
    [
      ["crownLeft", "crownCenter"],
      ["crownCenter", "crownRight"],
      ["scepterCrown", "scepterHand"],
      ["scepterHand", "chest"],
      ["peacockTailUpperRight", "peacockTailMidLeft"],
      ["peacockTailMidLeft", "peacockTailLowerRight"],
      ["peacockTailMidLeft", "peacockTailTip"],
      ["peacockTailMidLeft", "peacockTailMidRight"],
    ],
  ),

  thatsat: createConstellation(
    [
      // Normalized from ares_with_stars.svg's 145 0 1667 2048 viewBox,
      // including the horizontal space created by `contain`.
      // Array order is the authored firing order.
      ["spearTip", 13.4813, 3, 1.3],
      ["spearLower", 17.5563, 12.4678, 0.8],
      ["spearUpperRight", 20.8237, 8.2545, 0.8],
      ["spearUpperLeft", 16.4385, 6.7068, 1.8],
      ["raisedArm", 30.8839, 25.8813],
      ["beltCenter", 46.0171, 45.2279],
      ["shieldTop", 69.233, 34.3078],
      ["shieldBoss", 72.9303, 44.454],
      ["shieldBottom", 73.0163, 56.3199],
      ["shieldOuter", 78.5193, 44.7979],
    ],
    [
      ["beltCenter", "raisedArm"],
      ["raisedArm", "spearUpperLeft"],
      ["spearLower", "spearTip"],
      ["spearUpperRight", "spearTip"],
      ["shieldTop", "shieldBoss"],
      ["shieldBoss", "shieldBottom"],
      ["shieldTop", "shieldOuter"],
      ["shieldOuter", "shieldBottom"],
    ],
  ),

  phaquan: createConstellation(
    [
      // Ordered as marked in prometheus_with_stars.svg; coordinates include
      // the horizontal padding from displaying its portrait with `contain`.
      ["crown", 41.9174, 15.4772, 1.8],
      ["flameTip", 18.294, 3.2674, 1.4],
      ["flameUpper", 23.1409, 8.2545],
      ["flameMiddle", 18.5296, 13.9295],
      ["flameBase", 21.625, 21.8401, 1.2],
      ["leftFoot", 35.5545, 81.6853],
      ["leftKnee", 32.803, 57.0937],
      ["rightKnee", 49.656, 66.638],
      ["rightFoot", 59.6302, 93.2072, 1.2],
      ["waist", 41.9174, 50.215],
      ["rightShoulder", 51.4617, 28.7188],
    ],
    [
      ["flameTip", "flameUpper"],
      ["flameUpper", "flameMiddle"],
      ["flameMiddle", "flameBase"],
      ["rightShoulder", "waist"],
      ["waist", "leftKnee"],
      ["leftKnee", "leftFoot"],
      ["waist", "rightKnee"],
      ["rightKnee", "rightFoot"],
    ],
  ),

  thamlang: createConstellation(
    [
      ["mirrorTop", 32.2442, 5.331],
      ["mirrorCenter", 33.534, 12.8977, 2],
      ["mirrorBottom", 34.3938, 19.2605],
      ["leftShoulder", 45.6578, 25.6234],
      ["waistLeft", 45.5718, 36.6294, 1.5],
      ["waistRight", 55.1161, 36.0275, 1.5],
      ["rightShoulder", 55.718, 27.687],
      ["hairRight", 70.8512, 27.859],
      ["shellCenter", 38.3491, 73.4308],
      ["shellTop", 29.1488, 68.1857],
      ["shellLeft", 23.2158, 69.3035],
      ["shellTip", 18.4867, 82.9751],
      ["doveLeft", 19.3465, 51.7627],
      ["doveRight", 25.6234, 53.8263],
    ],
    [
      ["mirrorTop", "mirrorCenter"],
      ["mirrorCenter", "mirrorBottom"],
      ["mirrorBottom", "leftShoulder"],
      ["leftShoulder", "waistLeft"],
      ["waistLeft", "waistRight"],
      ["rightShoulder", "hairRight"],
      ["leftShoulder", "rightShoulder"],
      ["rightShoulder", "waistRight"],
      ["shellTop", "shellCenter"],
      ["shellLeft", "shellTop"],
      ["shellTip", "shellLeft"],
      ["doveLeft", "doveRight"],
    ],
  ),

  thaiduong: createConstellation(
    [
      ["lyreTopLeft", 25.8301, 13.4996],
      ["lyreBottomLeft", 26.432, 27.515],
      ["lyreBottomRight", 36.2342, 26.1393],
      ["lyreTopRight", 32.193, 13.2416],
      ["rightShoulder", 56.0107, 27.687, 2],
      ["waist", 54.033, 45.3998, 2],
      ["sunCrown", 50.3357, 8.0825, 2],
      ["sunLeft", 43.027, 20.2064],
      ["sunRight", 58.7622, 18.3147],
    ],
    [
      ["lyreTopLeft", "lyreBottomLeft"],
      ["lyreBottomLeft", "lyreBottomRight"],
      ["lyreBottomRight", "lyreTopRight"],
      ["lyreTopRight", "lyreTopLeft"],
      ["sunCrown", "sunLeft"],
      ["sunCrown", "sunRight"],
      ["sunLeft", "rightShoulder"],
      ["sunRight", "rightShoulder"],
      ["rightShoulder", "waist"],
    ],
  ),

  thaiam: createConstellation(
    [
      // Ordered as marked in athemis_with_stars.svg. Its square viewBox
      // maps directly to normalized coordinates.
      ["head", 53.4824, 15.7352, 1.8],
      ["chest", 44.9699, 44.368],
      ["leftShoulder", 38.6071, 28.8908],
      ["arrowEnd", 54.6071, 29.8908, 0.6],
      ["bowHand", 78.8478, 28.2029, 1.2],
      ["arrowTip", 89.4239, 27.515, 1.4],
      ["hip", 43.5082, 56.9218],
      ["knee", 51.3328, 68.5297],
      ["foot", 68.8736, 82.2012, 1.15],
    ],
    [
      ["head", "leftShoulder"],
      ["leftShoulder", "chest"],
      ["arrowEnd", "bowHand"],
      ["bowHand", "arrowTip"],
      ["hip", "knee"],
      ["knee", "foot"],
    ],
  ),

  vukhuc: createConstellation(
    [
      // Ordered as marked in hermes_with_stars.svg; coordinates include
      // the horizontal padding from displaying its portrait with `contain`.
      ["rightShoulder", 59.554, 27.945, 1.2],
      ["belt", 46.0545, 48.0653, 1.2],
      ["leftWingedFoot", 34.7905, 75.1505, 1.2],
      ["rightWingedFoot", 59.898, 89.8538, 1.2],
      ["pouchBottomLeft", 70.818, 63.3706],
      ["pouchTopLeft", 73.2256, 57.9536],
      ["pouchTopRight", 79.1585, 58.6414],
      ["pouchBottomRight", 79.3305, 65.3482, 1.2],
    ],
    [
      ["rightShoulder", "belt"],
      ["belt", "leftWingedFoot"],
      ["belt", "rightWingedFoot"],
      ["pouchTopLeft", "pouchTopRight"],
      ["pouchTopRight", "pouchBottomRight"],
      ["pouchBottomRight", "pouchBottomLeft"],
      ["pouchBottomLeft", "pouchTopLeft"],
    ],
  ),

  liemtrinh: createConstellation(
    [
      // Ordered as marked in nemesis_with_stars.svg; coordinates include
      // the horizontal padding from displaying its portrait with `contain`.
      ["leftPan", 18.9226, 36.6294],
      ["rightPan", 35.5176, 36.9733],
      ["balanceGrip", 26.9191, 15.4772, 1.6],
      ["raisedArm", 44.8039, 25.6234],
      ["beltCenter", 50.049, 38.865, 1.2],
      ["swordHand", 69.7394, 59.3293],
      ["swordBlade", 74.1246, 77.902, 1.3],
    ],
    [
      ["balanceGrip", "leftPan"],
      ["balanceGrip", "rightPan"],
      ["raisedArm", "beltCenter"],
      ["beltCenter", "swordHand"],
      ["swordHand", "swordBlade"],
    ],
  ),

  thienco: createConstellation(
    [
      // Ordered as marked in athena_with_stars.svg; coordinates include
      // the horizontal padding from displaying its portrait with `contain`.
      ["owlLowerLeft", 29.4761, 66.638, 1.2],
      ["owlLowerRight", 32.7436, 66.638, 1.2],
      ["owlUpperLeft", 26.6387, 62.9407, 0.8],
      ["owlUpperRight", 34.5492, 63.0267, 0.8],
      ["helmetRightLower", 53.7238, 14.4454, 1.6],
      ["helmetLeftLower", 41.8579, 18.2287],
      ["helmetUpperLeft", 44.6094, 9.0284],
      ["rightShoulder", 54.8416, 27.1711],
      ["chest", 47.017, 40.7567, 1.8],
      ["leftShoulder", 44.2655, 27.859],
    ],
    [
      ["owlUpperLeft", "owlLowerLeft"],
      ["owlLowerRight", "owlUpperRight"],
      ["helmetUpperLeft", "helmetRightLower"],
      ["helmetRightLower", "helmetLeftLower"],
      ["helmetLeftLower", "helmetUpperLeft"],
      ["leftShoulder", "chest"],
      ["rightShoulder", "chest"],
    ],
  ),

  thienluong: createConstellation(
    [
      // Ordered as marked in demeter_with_stars.svg; coordinates include
      // the horizontal padding from displaying its portrait with `contain`.
      ["waist", 44.22, 40.7567, 1.6],
      ["rightShoulder", 56.8597, 26.0533, 1.6],
      ["basketHandle", 68.6396, 59.1574, 1.3],
      ["basketTopLeft", 62.5347, 70.4213],
      ["basketTopRight", 74.2286, 70.5073],
      ["basketBottomLeft", 65.1142, 79.2777],
      ["basketBottomRight", 71.3911, 79.0198],
      ["wheatBase", 29.4306, 29.1488, 1.3],
      ["wheatRight", 34.5037, 18.0567],
      ["wheatCenter", 28.3988, 12.2098],
      ["wheatUpperLeft", 21.1761, 14.0155],
      ["wheatLowerLeft", 19.0265, 21.2382],
    ],
    [
      ["wheatBase", "wheatRight"],
      ["wheatBase", "wheatCenter"],
      ["wheatBase", "wheatUpperLeft"],
      ["wheatBase", "wheatLowerLeft"],
      ["wheatBase", "waist"],
      ["waist", "rightShoulder"],
      ["rightShoulder", "basketHandle"],
      ["basketHandle", "basketTopLeft"],
      ["basketHandle", "basketTopRight"],
      ["basketTopLeft", "basketTopRight"],
      ["basketTopLeft", "basketBottomLeft"],
      ["basketTopRight", "basketBottomRight"],
      ["basketBottomLeft", "basketBottomRight"],
    ],
  ),

  thientuong: createConstellation(
    [
      // Ordered as marked in hades_with_stars.svg; coordinates include
      // the horizontal padding from displaying its portrait with `contain`.
      ["upperBody", 53.5477, 27.859],
      ["leftWaist", 40.3921, 43.6801],
      ["rightWaist", 51.1401, 44.1101],
      ["staffCrown", 25.7747, 12.0378, 1.8],
      ["staffHand", 26.7205, 34.5658, 1.2],
      ["cerberusLowerMid", 63.006, 62.7687],
      ["cerberusUpperLeft", 70.8306, 56.2339],
      ["cerberusUpperCenter", 75.0438, 55.804],
      ["cerberusRight", 83.0404, 60.7051],
      ["cerberusFarRight", 86.6517, 60.7911],
      ["cerberusLowerLeft", 59.5666, 63.2846],
    ],
    [
      ["staffCrown", "staffHand"],
      ["leftWaist", "upperBody"],
      ["upperBody", "rightWaist"],
      ["rightWaist", "leftWaist"],
      ["cerberusLowerLeft", "cerberusLowerMid"],
      ["cerberusUpperLeft", "cerberusUpperCenter"],
      ["cerberusRight", "cerberusFarRight"],
    ],
  ),

  thiendong: createConstellation(
    [
      // Normalized from dionysos_with_stars.svg's 1254×1254 viewBox.
      // Array order is the authored firing order.
      ["gobletRimLeft", 28.2889, 3.9553],
      ["gobletBowlLeft", 31.0404, 8.4265],
      ["gobletBowlRight", 34.7377, 8.8564],
      ["gobletRimRight", 37.4893, 4.1273],
      ["gobletBaseLeft", 29.0628, 17.2829],
      ["gobletBaseRight", 34.2218, 17.1969],
      ["raisedArm", 38.2631, 31.4703],
      ["chest", 51.0748, 42.8203],
      ["waist", 51.6767, 52.7945],
      ["robeKnee", 63.3706, 66.2941],
      ["robeLower", 60.7051, 77.644],
    ],
    [
      ["gobletRimLeft", "gobletBowlLeft"],
      ["gobletBowlLeft", "gobletBowlRight"],
      ["gobletBowlRight", "gobletRimRight"],
      ["gobletRimRight", "gobletRimLeft"],
      ["gobletBowlLeft", "gobletBaseLeft"],
      ["gobletBowlRight", "gobletBaseRight"],
      ["gobletBaseLeft", "gobletBaseRight"],
      ["raisedArm", "chest"],
      ["chest", "waist"],
      ["waist", "robeKnee"],
      ["robeKnee", "robeLower"],
    ],
  ),

  cumon: createConstellation(
    [
      // Ordered as marked in iris_with_stars.svg; coordinates include the
      // horizontal padding from displaying its portrait with `contain`.
      ["staffCrown", 30.8562, 9.3723, 2],
      ["rightArm", 53.814, 30.5245],
      ["waist", 52.5243, 42.2184, 1.2],
      ["head", 46.8493, 17.7128, 1.4],
    ],
    [
      ["waist", "rightArm"],
      ["rightArm", "head"],
    ],
  ),
};
