from concurrent.futures import ThreadPoolExecutor, as_completed


def use_multi_processing():
    raise NotImplementedError("Multi-processing is not implemented yet.")


def use_multi_threading(
    function: callable, args: list[tuple], timeout: int = None, max_workers: int = None
) -> dict:
    """
    Execute function using multi-threading via ThreadPoolExecutor.

    Args:
        function (callable): IO-bound function to be executed.
        args (list[tuple]): List of argument tuples to pass to the function.
        timeout (int, optional): Maximum time to wait for each function call. Defaults to None.
        max_workers (int, optional): Maximum number of worker threads. Defaults to None.
    Returns:
        dict: A dictionary mapping each argument tuple to its corresponding function result.
    """

    assert callable(function), "function must be callable"
    assert all(map(lambda x: isinstance(x, tuple), args)), (
        "args must be a list/tuple of tuples to be passed to the function"
    )

    results = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(function, *arg): arg for arg in args}
        for future in as_completed(futures):
            arg = futures[future]
            try:
                results[arg] = future.result(timeout=timeout)
            except Exception as e:
                # possible to add a on_failure callback here to handle failures but
                # right now just print the exception
                print(
                    f"Function '{function}' call with arguments ({arg}) failed. "
                    "Setting function to return None for these arguments. "
                    f"Exception returned:\n{e}"
                )
                results[arg] = None

        return results


if __name__ == "__main__":
    import time

    def io_test_function(sleep_time: int, return_value: str):
        print(f"Sleeping for {sleep_time} seconds...")
        time.sleep(sleep_time)
        print(f"Returning value = {return_value}")
        return return_value

    args = [(1, "first"), (5, "second"), (3, "third"), (3, "fourth")]

    results = use_multi_threading(io_test_function, args)
    print(results)
