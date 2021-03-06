# import csv
# from collections import defaultdict
# from datetime import datetime
# from statistics import mean
# 
import matplotlib.pyplot as plt
# 
# 
# def to_date(date_str: str):
#     return datetime.strptime(date_str, '%Y-%m-%d').date()
# 
# 
# def get_data(path: str) -> defaultdict:
#     data = defaultdict(list)
#     with open(path, mode='r') as fin:
#         reader = csv.reader(fin)
#         next(reader)
#         for row in reader:
#             if row[4] not in data[row[1]]:
#                 data[row[1]].append(row[4])
#             data[row[1]].append({row[2]: to_date(row[3])})
#     return data
# 
# 
# def get_guide(path: str) -> defaultdict:
#     guide = defaultdict()
#     with open(path, mode='r') as fin:
#         reader = csv.reader(fin)
#         next(reader)
#         for row in reader:
#             guide[row[2]] = row[1]
#     return guide
# 
# 
# def get_average_by_month(data: defaultdict[list]) -> dict:
#     group_by_month = defaultdict(list)
#     for key in data.keys():
#         try:
#             group_by_month[f"{data[key][1]['Прием товара'].month} {data[key][1]['Прием товара'].year}"].append(
#                 (data[key][2]['Выдача товара'] - data[key][1]['Прием товара']).days)
#         except IndexError:
#             pass
#     average_by_month = {month: round(mean(group_by_month[month]), 3) for month in group_by_month}
#     return average_by_month
# 
# 
# def get_group_by_week(data: defaultdict[list]) -> dict:
#     group_by_week = dict()
#     for key in data.keys():
#         region = guide[data[key][0]]
# 
#         if region not in group_by_week.keys():
#             group_by_week[region] = dict()
# 
#         week = data[key][1]['Прием товара'].isocalendar()[1]
# 
#         if week not in group_by_week[region].keys():
#             group_by_week[region][week] = list()
#         try:
#             group_by_week[region][week].append(
#                 (data[key][2]['Выдача товара'] - data[key][1]['Прием товара']).days)
#         except IndexError:
#             pass
#     for region in group_by_week:
#         for week in group_by_week[region]:
#             group_by_week[region][week] = round(mean(group_by_week[region][week]), 3)
#     return group_by_week
# 
# 
def autolabel(rects, height_factor=1.01):
    for i, rect in enumerate(rects):
        height = rect.get_height()
        label = f'{int(height):d}'
        ax.text(rect.get_x() + rect.get_width() / 2., height_factor * height,
                f'{label}',
                ha='center', va='bottom')
# 
# 
# if __name__ == '__main__':
#     data = get_data('files/data.csv')
#     guide = get_guide('files/Справочник.csv')
# 
#     # Общая динамика по месяцам
#     average_by_month = get_average_by_month(data)
# 
#     with open("files/months.csv", "w") as file:
#         writer = csv.writer(file)
#         writer.writerow(['Месяц', 'Среднее значение'])
#         for month, average in average_by_month.items():
#             writer.writerow([month, average])
# 
#     # по регионам каждую неделю
#     group_by_week = get_group_by_week(data)
# 
#     with open("files/regions.csv", "w") as file:
#         writer = csv.writer(file)
#         regions = list(group_by_week.keys())
#         writer.writerow(['Неделя'] + regions)
#         for i in range(1, 53):
#             writer.writerow([i] + [group_by_week[region][i] for region in regions])
# 
#     # нормативный срок по всей компании
#     standard_time_limit = round(mean(i for i in average_by_month.values()), 3)
#     print(f'Нормативный срок по всей компании: {standard_time_limit}')
# 
#     # график
#     index = list()
#     values = list()
#     for region in group_by_week:
#         index.append(region)
#         values.append(mean(group_by_week[region].values()))
#     plt.bar(index, values)


from datetime import datetime

import pandas as pd


def to_date(input_str: str):
    return [datetime.strptime(i, '%Y-%m-%d').date() for i in input_str]


data = pd.read_csv('files/data.csv')
guide = pd.read_csv('files/Справочник.csv')

data.rename(columns={'Идентификатор филиалы документа': 'Идентификатор филиала'}, inplace=True)
data = data.merge(guide[['Идентификатор филиала', 'Наименование региона филиала']])

del(guide)

receiving_product = data[data['Вид операции документа'] == 'Прием товара'][['Идентификатор товара', 'Дата документа']]
receiving_product.rename(columns={'Дата документа': 'Прием товара'}, inplace=True)
extradition_product = data[data['Вид операции документа'] == 'Выдача товара'][
    ['Идентификатор товара', 'Дата документа']]

extradition_product.rename(columns={'Дата документа': 'Выдача товара'}, inplace=True)
group_by_products = receiving_product.merge(extradition_product)
group_by_products = group_by_products.merge(data[['Идентификатор товара', 'Наименование региона филиала']])

del(data)

group_by_products[['Прием товара', 'Выдача товара']] = group_by_products[['Прием товара', 'Выдача товара']].apply(to_date)
group_by_products['Месяц'] = group_by_products['Прием товара'].apply(lambda x: x.month)
group_by_products['Неделя'] = group_by_products['Прием товара'].apply(lambda x: x.isocalendar()[1])
group_by_products['Количество дней'] = (group_by_products['Выдача товара'] - group_by_products['Прием товара']).apply(
    lambda x: x.days)

groups_ = group_by_products[['Месяц', 'Количество дней']].groupby('Месяц')['Количество дней'].mean()

print(groups_)
standard_time_limit=group_by_products["Количество дней"].mean()
print(f'Нормативный срок по всей компании = {standard_time_limit}')
groups_.to_csv('files/months.csv')

group_by_month = group_by_products[['Неделя', 'Наименование региона филиала', 'Количество дней']].groupby(
    ['Неделя', 'Наименование региона филиала'])['Количество дней'].mean().to_csv('files/regions.csv')

del(group_by_month)

group_by_week = group_by_products[['Наименование региона филиала', 'Количество дней']].groupby('Наименование региона филиала')[
    'Количество дней'].mean()

index = list(group_by_week.index)

values = group_by_week.to_list()
plt.bar(index, values)
plt.axhline(y=standard_time_limit, color='r', linestyle='-')
ax = plt.gca()
autolabel(ax.patches, height_factor=1.01)
plt.show()
