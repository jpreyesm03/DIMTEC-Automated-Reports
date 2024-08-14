import forallpeople as si # type: ignore

def limit_prefix_to_giga(value):
    value_in_giga = value / si.GA
    if value_in_giga >= 1:
        return f"{round(value_in_giga, 2)} GA"
    else:
        return str(value)

# Assuming ebt is defined as an integer
ebt = "1232132312312321321"
new_ebt = limit_prefix_to_giga(int(ebt))


print(new_ebt)
