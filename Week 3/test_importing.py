from test2 import printJP, main as te_main # type: ignore
from python_test_error_responses import pretty_printer, main as er_main

df = [
    [10, 2214124, 31234124, 4.5, 512312],
    [1010.24214, 12401240, 2413.2323, 0.000534343224]
]

for row in df:
    print(pretty_printer(row))
er_main()  # Calls the main function from python_test_error_responses