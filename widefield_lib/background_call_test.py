from multiprocessing import Process

a = 0

def func1():
    print(f'func1 starting')
    for i in range(10000000):
        a = a + 1
    print(f'func1 ended')
def func2():
    print(f'func2 starting')
    for i in range(10000000): pass
    print(f'func2 ended')


if __name__ == '__main__':
    p1 = Process(target=func1)
    p1.start()
    p2 = Process(target=func2)
    p2.start()
    p1.join()
    p2.join()