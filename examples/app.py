from jupdb.core import JuPDb

def example_function():
    a = 10
    jupdb = JuPDb()
    jupdb.set_trace()  # Breakpoint here
    b = 20
    print("Result:", a + b)

if __name__ == "__main__":
    example_function()
