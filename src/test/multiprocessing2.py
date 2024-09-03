from multiprocessing import Process, Value
from multiprocessing.managers import BaseManager
import time
import asyncio

class Test1:
    def __init__(self):
        self.value = Value("f", 0.0)
    
    def increment(self):
        self.value.value += 1
    
    def get(self):
        return self.value.value
    
    async def update(self):
        while True:
            self.increment()
            print(self.get())
            await asyncio.sleep(0.05)

class Test2:
    def __init__(self, test1: Test1):
        self.test1: Test1 = test1
    
    def show(self):
        print("value:", self.test1.get())
    
    def invoke(self):
        async def _invoke():
            tasks = [
                asyncio.create_task(self.test1.update())
            ]
            await asyncio.gather(*tasks)
        asyncio.run(_invoke())

def main():
    test1 = Test1()
    test2 = Test2(test1)

    process = Process(target=test2.invoke, daemon=True)
    process.start()

    while True:
        test2.show()
        time.sleep(1)

if __name__ == "__main__":
    main()