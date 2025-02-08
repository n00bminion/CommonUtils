from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


def useMultiThread(func, *arg):
    with ThreadPoolExecutor() as tpe:
        res = tpe.map(func, *arg)
    return [i for i in res]


def useMultiProcess(func, *arg):
    with ProcessPoolExecutor() as ppe:
        res = ppe.map(func, *arg)
    return [i for i in res]
