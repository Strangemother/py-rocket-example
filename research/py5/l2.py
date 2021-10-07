


async def run_loop(addresses):
    loop = asyncio.get_event_loop()
    loops = [loop.create_task(execute_parallel, address) for address in addresses]
    loop.run_until_complete(asyncio.wait(loops))

def main():
    n_jobs = 3
    addresses = [list of addresses]
    _addresses = list_splitter(data=addresses, n=n_jobs)
    with multiprocessing.Pool(processes=n_jobs) as pool:
        pool.imap_unordered(run_loop, _addresses)
