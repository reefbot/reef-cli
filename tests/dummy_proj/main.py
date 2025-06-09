import os

from .hello_world.hello_world import hello_world, HelloUniverse
from .hello_world.hello_world import call_hello_world as chw


def stupid_function() -> None:
    print("stupid")


if __name__ == "__main__":
    print(os.getcwd())
    hello_world()



