class Animal:
    is_live: bool
    age: int

    def __init__(self, is_live: bool, age: int):
        self.is_live = is_live
        self.age = age

    def grow(self):
        if self.is_live:
            self.age += 1


class Mammal(Animal):
    fur_color: str

    def __init__(self, is_live: bool, age: int, fur_color: str):
        super().__init__(is_live, age)
        self.fur_color = fur_color




cat = Mammal(True, 1, fur_color='yellow')
dog = Mammal(True, 5, fur_color='white')

print(cat.age)
cat.grow()
print(cat.age)