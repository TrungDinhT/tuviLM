import json

ZODIAC_CONFIG_FILE = "data/zodiac_config.json"


def find_cung_each_n_step(begin: str, cung_list: list[str], n: int) -> list[str]:
    begin_idx = cung_list.index(begin) + n
    nb_cung_total = len(cung_list)
    nb_cung_to_find = nb_cung_total // n - 1
    return [cung_list[(i * n + begin_idx) % nb_cung_total] for i in range(nb_cung_to_find)]


def find_cung_xung_chieu(cung: str, zodiac_config: dict) -> list[str]:
    cung_list = zodiac_config["cung"]
    return find_cung_each_n_step(cung, cung_list, 6)


def find_cung_tam_hop(cung: str, zodiac_config: dict) -> list[str]:
    cung_list = zodiac_config["cung"]
    return find_cung_each_n_step(cung, cung_list, 4)

def find_cung_nhi_hop(cung: str, zodiac_config: dict) -> list[str]:
    for (first, second) in zodiac_config["nhi_hop"]:
        if cung == first: 
            return [second]
        elif cung == second: 
            return [first]



def preprocess(cung_map: dict):
    with open(ZODIAC_CONFIG_FILE, "r") as zodiac_file:
        config = json.load(zodiac_file)
        cung_list = config["cung"]
        zodiac_map = {}
        for gio, data in cung_map.items():
            # print(find_cung_xung_chieu(gio, config))
            zodiac_map[data["cung"]] = {
                "sao": data["sao"],
                "xung_chieu": [cung_map[cung_xung_chieu] for cung_xung_chieu in find_cung_xung_chieu(gio, config)],
                "tam_hop": [cung_map[cung_tam_hop] for cung_tam_hop in find_cung_tam_hop(gio, config)],
                "nhi_hop": [cung_map[cung_nhi_hop] for cung_nhi_hop in find_cung_nhi_hop(gio, config)]
            }

        with open("data/zodiac_map.json", "w") as zodiac_map_file:
            json.dump(zodiac_map, zodiac_map_file, indent=4)


preprocess(
    {
        "thin": {
            "cung": "Tat Ach",
            "sao": {
                "chinh_tinh": [
                    "Thien Luong",
                    "Thien Co"
                ],
                "phu_tinh": [
                    "Long Tri",
                    "Hoa Cai",
                    "Hoa Quyen",
                    "Da La",
                    "Quan Phu",
                    "Quan Phu?",
                    "Thien La",
                    "Thien Su",
                ],
                "vong_trang_sinh": "Quan Doi"
            },
        },
        "ty": {
            "cung": "Tai Bach",
            "sao": {
                "chinh_tinh": [
                    "Tu Vi",
                    "That Sat",
                ],
                "phu_tinh": [
                    "Phong Cao",
                    "Dia Giai",
                    "Loc Ton",
                    "Thien Quan",
                    "Nguyet Duc",
                    "Bac Sy",
                    "Hoa Tinh",
                    "Kiep Sat",
                    "Tu Phu",
                    "Dau Quan",
                ],
                "vong_trang_sinh": "Lam Quan"
            }
        },
        "ngo": {
            "cung": "Tu Tuc",
            "sao": {
                "chinh_tinh": [],
                "phu_tinh": [
                    "Thien Giai",
                    "Luc Sy",
                    "Kinh Duong",
                    "Thien Khoc",
                    "Thien Hu",
                    "Tue Pha",
                ],
                "vong_trang_sinh": "De Vuong"
            }
        },
        "mui": {
            "cung": "Phu The",
            "sao": {
                "chinh_tinh": [],
                "phu_tinh": [
                    "Van Khuc",
                    "Van Xuong",
                    "Long Duc",
                    "Thanh Long",
                    "Hoa Khoa",
                    "Linh Tinh",
                    "Thien Hinh",
                    "Luu Ha",
                ],
                "vong_trang_sinh": "Suy"
            }
        },
        "than": {
            "cung": "Huynh De",
            "sao": {
                "chinh_tinh": [],
                "phu_tinh": [
                    "Van Tinh",
                    "Dia Khong",
                    "Bach Ho",
                    "Tieu Hao"
                ],
                "vong_trang_sinh": "Benh"
            }
        },
        "dau": {
            "cung": "Menh",
            "sao": {
                "chinh_tinh": [
                    "Pha Quan",
                    "Liem Trinh"
                ],
                "phu_tinh": [
                    "Thai Phu",
                    "Thien Viet",
                    "Dao Hoa",
                    "Thien Hi",
                    "Thien Duc",
                    "Phuc Duc",
                    "Thien Tai",
                    "Tuong Quan",
                    "Hoa Ky"
                ],
                "vong_trang_sinh": "Tu"
            },
        },
        "tuat" : {
            "cung" : "Phu Mau",
            "sao": {
                "chinh_tinh" : [],
                "phu_tinh" : ["Duong Phu", "Giai Than", "Phuong cac", "Tau thu", "Qua Tu", "Dieu Khach", "Dia Vong"],
                "vong_trang_sing" : "Mo"
            }
        },
        "hoi" : {
            "cung" : "Phuc Duc",
            "sao": {
            "chinh_tinh" : ["Thien Phu"],
            "phu_tinh" : ["Thien Y", "Thien Khoi", "Thien Quy", "Tam Thai", "Thien Dieu", "Truc Phu", "Phi Liem", "Bach Ho"],
            "vong_trang_sing" : "Tuyet"}
        },
        "ti" : {
            "cung" : "Dien Trach",
            "sao": {
            "chinh_tinh" : ["Thai Am", "Thien Dong"],
            "phu_tinh" : ["Huu Bat", "Thien Phuc", "Thien Tru", "Hy Than", "Hoa Loc", "Thai Tue"],
            "vong_trang_sing" : "Thai"}
        },
        "suu" : {
            "cung" : "Quan Loc",
            "sao": {
            "chinh_tinh" : ["Tham Lang", "Vu Khuc"],
            "phu_tinh" : ["Quoc An", "Thieu Duong", "Thien Khong", "Benh Phu"],
            "vong_trang_sing" : "Duong"}
        },
        "dan" : {
            "cung" : "No Boc",
            "sao": {
            "chinh_tinh" : ["Cu Mon", "Thai Duong"],
            "phu_tinh" : ["Ta Phu", "Thien Ma", "Dia Kiep", "Co Than", "Tang Mon", "Dai Hao", "Thien Thuong"],
            "vong_trang_sing" : "Trang Sinh"}
        },
        "mao" : {
            "cung" : "Thien Di",
            "sao": {
            "chinh_tinh" : ["Thien Tuong"],
            "phu_tinh" : ["Hong Loan", "Thieu Am", "An Quang", "Bat Toa", "Thien Tho", "Phuc Binh"],
            "vong_trang_sing" : "Moc Duc"}
        }
    }
)



