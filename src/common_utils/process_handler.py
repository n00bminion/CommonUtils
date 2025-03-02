from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


def use_multi_thread(func, *arg):
    with ThreadPoolExecutor() as tpe:
        res = tpe.map(func, *arg)
    return [i for i in res]


def use_multi_process(func, *arg):
    with ProcessPoolExecutor() as ppe:
        res = ppe.map(func, *arg)
    return [i for i in res]
