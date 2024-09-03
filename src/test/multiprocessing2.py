from multiprocessing import Process, Value
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

class Test3:
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
    def __init__(self, test1: Test1, test3: Test3):
        self.test1: Test1 = test1
        self.test3: Test3 = test3
    
    def show(self):
        print("value:", self.test1.get())
        print("value3:", self.test3.get())
    
    def invoke(self):
        async def _invoke():
            tasks = [
                asyncio.create_task(self.test1.update()),
                asyncio.create_task(self.test3.update())
            ]
            await asyncio.gather(*tasks)
        asyncio.run(_invoke())

def main():
    test1 = Test1()
    test3 = Test3()
    test2 = Test2(test1, test3)

    process = Process(target=test2.invoke, daemon=True)
    process.start()

    while True:
        test2.show()
        time.sleep(1)

if __name__ == "__main__":
    main()