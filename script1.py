import re
from datetime import datetime
from importlib.metadata import files


class ned():
    def __init__(self, cost: int, owner: str, datee):
        self.cost = cost
        self.owner = owner
        self.datee = datee

    def __str__(self):
        return (f"Недвижимость:"
                f"{self.owner} "
                f"{self.datee.strftime('%Y.%m.%d')} "
                f"{self.cost} руб.")

def pars(input_str):
    patt = {
        'date': r'(\d{4}\.\d{2}\.\d{2})',
        'cost': r'(\d+)'
    }
    found = {}
    date_found = re.search(patt['date'],input_str)
    if date_found:
        datestr = date_found.group(1)
        year, month, day = map(int, datestr.split('.'))
        found['reg'] = datetime(year,month,day)
        input_str = input_str.replace(datestr, '', 1)

    cost_found = re.search(patt['cost'], input_str)
    if cost_found:
        coststr = cost_found.group(1)
        found['cost'] = int(coststr)
        input_str = input_str.replace(coststr, '', 1)


    ownerstr = input_str.strip()
    if ownerstr:
        if ownerstr.startswith('"') and ownerstr.endswith('"'):
            found['own'] = ownerstr[1:-1].strip()
        else:
            found['own'] = ownerstr.strip()

    return ned(
        owner=found['own'],
        datee=found['reg'],
        cost=found['cost']
    )


objects_list = []
filename = "data.txt"


with open(filename, 'r', encoding='utf-8') as file:
    for line in file:
        if line.strip():
            parsed_object = pars(line.strip())
            objects_list.append(parsed_object)

for obj in objects_list:
    print(obj)