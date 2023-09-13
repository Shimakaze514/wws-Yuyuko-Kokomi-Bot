import os
import asyncio
import json
import httpx
file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'json')


class update:
    def __init__(self) -> None:
        self.ship_info_data = json.load(
            open(os.path.join(file_path, 'ship_name.json'), "r", encoding="utf-8"))

    async def update_name(self):
        async with httpx.AsyncClient() as client:
            url = 'https://vortex.worldofwarships.asia/api/encyclopedia/en/vehicles/'
            res = await client.get(url, timeout=3)
            if res.status_code != 200:
                return 'error'
            result = res.json()
            new_ship = []
            for ship_id, ship_data in result['data'].items():
                if ship_id in self.ship_info_data:
                    continue
                else:
                    tier = ship_data['level']
                    type = ship_data['tags'][0]
                    nation = ship_data['nation']
                    name = ship_data['name'].split('_')[0]
                    name_zh = ship_data['localization']['shortmark']['zh_sg']
                    name_en = ship_data['localization']['shortmark']['en']
                    new_ship.append(name_zh)
                    print(name)
                    print(name_zh)
                    self.ship_info_data[ship_id] = {
                        'tier': tier,
                        'type': type,
                        'nation': nation,
                        'name': name,
                        'ship_name': {
                            'zh_sg': name_zh,
                            'en': name_en,
                            'nick': [],
                            'other': []
                        }
                    }
                    self.ship_info_data[ship_id]['ship_name']['other'].append(
                        name_zh)
                    self.ship_info_data[ship_id]['ship_name']['other'].append(
                        name_en)
                    if name_zh != self.name_format(name_zh):
                        self.ship_info_data[ship_id]['ship_name']['other'].append(
                            self.name_format(name_zh))
                    self.ship_info_data[ship_id]['ship_name']['other'].append(
                        self.name_format(name_en))
            with open(os.path.join(file_path, 'ship_name.json'), 'w', encoding='utf-8') as f:
                f.write(json.dumps(
                    self.ship_info_data, ensure_ascii=False))
            f.close()

    def name_format(self, in_str: str):
        in_str_list = in_str.split()
        in_str = None
        in_str = ''.join(in_str_list)
        en_list = {
            'a': ['à', 'á', 'â', 'ã', 'ä', 'å'],
            'e': ['è', 'é', 'ê', 'ë'],
            'i': ['ì', 'í', 'î', 'ï'],
            'o': ['ó', 'ö', 'ô', 'õ', 'ò', 'ō'],
            'u': ['ü', 'û', 'ú', 'ù', 'ū'],
            'y': ['ÿ', 'ý']
        }
        for en, lar in en_list.items():
            for index in lar:
                if index in in_str:
                    in_str = in_str.replace(index, en)
                if index.upper() in in_str:
                    in_str = in_str.replace(index.upper(), en.upper())
        re_str = ['_', '-', '·', '.', '\'']
        for index in re_str:
            if index in in_str:
                in_str = in_str.replace(index, '')
        in_str = in_str.lower()
        return in_str


# asyncio.run(update().update_name())
