import concurrent.futures
import requests
import itertools
from header_generator.header_generator import header_generator
from proxy_checker.proxy_checker import proxy_checker, read_proxies

def main():
    proxy_list = 'proxy_checker/proxy.txt'
    total_attempts = 0
    successful_connections = 0
    num_url = input("Введите url: ")
    num_cycles = int(input("Введите количество циклов: "))
    num_threads = int(input("Введите количество потоков: "))
    proxy_checker(proxy_list, num_url, num_threads)
    proxies = read_proxies(proxy_list)

    proxy_iterator = itertools.cycle(proxies)

    def attempt_connection():
        nonlocal successful_connections
        proxy = next(proxy_iterator)
        try:
            session = requests.Session()
            print(header_generator())
            session.headers.update(header_generator())
            response = session.get(num_url, proxies={"http": proxy, "https": proxy}, timeout=5)
            session.close()
            if response.status_code == 200:
                successful_connections += 1
                # Здесь можно добавить действия на сайте
                return proxy, True
        except:
            pass
        return proxy, False

    for cycle in range(num_cycles):
        used_proxies = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(attempt_connection) for _ in range(num_threads)]
            for future in concurrent.futures.as_completed(futures):
                proxy, success = future.result()
                used_proxies.append((proxy, success))

        total_attempts += num_threads
        successful_proxies = [proxy for proxy, success in used_proxies if success]
        print(f"Цикл {cycle + 1}/{num_cycles}. Выполнено {total_attempts} попыток. Успешных подключений: {successful_connections}.")
        print(f"Использованные прокси в этом цикле: {successful_proxies}")

main()
