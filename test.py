from crs import CRS, CRSColumn
crs = CRS()

result_dict = crs.fetch_all(
    search_term = 'cs',
    #schedule_text = 'Midyear Term 2022',
    columns = [
        CRSColumn.Class,
        CRSColumn.AvailableSlots,
        CRSColumn.TotalSlots,
        CRSColumn.Demand
    ]
)

table = crs.tabulize(result_dict)
print(table)