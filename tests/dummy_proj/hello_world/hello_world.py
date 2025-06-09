from ..main import stupid_function


class HelloUniverse:
    @staticmethod
    def hello_universe() -> None:
        print("hello universe!")



async def hello_world(person: str = "mike") -> None:
    print("Hello World!")
    stupid_function()


def call_hello_world() -> None:
    hello_world()
