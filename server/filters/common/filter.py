class FilterColumns:
    def __init__(self, columns, wanted_columns):
        columns = columns.split(",")
        wanted_columns = wanted_columns.split(",")

        self.idxs = [i for i, col in enumerate(columns) if col in wanted_columns]

    def __obtain_idxs(self):
        return [i for i, col in enumerate(self.columns) if col in self.wanted_columns]

    def filter(self, columns):
        columns = columns.split(",")
        result = []

        for i, col in enumerate(columns):
            if i in self.idxs:
                result.append(col)

        return ",".join(result)


class FilterRows:
    def __init__(self, columns, dict_cond):
        keys = columns.split(",")
        new_dict = {}
        for i, key in enumerate(keys):
            if key in dict_cond:
                new_dict[i] = dict_cond[key]

        self.conditions = self.__map_conditions(len(keys), new_dict)

    def __map_conditions(self, max_args, dict_cond):
        conditions = []
        for i in dict_cond:
            conditions = self.__fill_conds(conditions, i)
            conditions.append(dict_cond[i])

        return conditions

    def __fill_conds(self, conds, next):
        diff_cons = next - len(conds)
        for i in range(len(conds), diff_cons):
            conds.append(True)

        return conds

    def filter(self, row):
        elements = row.split(",")
        result = []
        for elem, condition in zip(elements, self.conditions):
            if callable(condition):
                if not condition(elem):
                    return None
        return row


class Filter:
    def __init__(self, columns_names, wanted_columns, filter_conditions):
        self.filter_columns = FilterColumns(columns_names, wanted_columns)
        self.filter_rows = FilterRows(wanted_columns, filter_conditions)

    def apply(self, trip):
        transf_trip = self.filter_columns.filter(trip)

        if self.filter_rows.filter(transf_trip):
            return transf_trip
        else:
            return None
