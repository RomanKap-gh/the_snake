from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SCREEN_CENTER_X, SCREEN_CENTER_Y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)
# Цвет препятствия
OBSTACLE_COLOR = (88, 57, 39)
# Цвет "ядовитой" еды
POISON_COLOR = (255, 255, 0)
# Цвет яблока
APPLE_COLOR = (255, 0, 0)
# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов"""

    speed_game = 15
    occupied_cells = [(SCREEN_CENTER_X, SCREEN_CENTER_Y)]

    def __init__(self):
        """Инициализирует базовые параметры объекта."""
        self.board_background_color = BOARD_BACKGROUND_COLOR
        self.border_color = BORDER_COLOR
        self.position = (SCREEN_CENTER_X, SCREEN_CENTER_Y)
        # Задаю цвет в явном виде, т.к. есть проверка PyTest
        self.body_color = None

    def draw():
        """Отрисовка объекта — должен быть реализован в подклассах."""

    @staticmethod
    def randomize_position(snake_positions):
        """Задает уникальное положение объекта.

        Args:
            snake_positions (list[tuple]): Координаты положения змейки.
        """
        while True:
            coordinate_x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            coordinate_y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            new_coordinate = (coordinate_x, coordinate_y)
            if (new_coordinate in GameObject.occupied_cells
                    or new_coordinate in snake_positions):
                continue
            else:
                GameObject.occupied_cells.append(new_coordinate)
                return new_coordinate

    def draw_rect(self, position):
        """Отображает прямоугольник с заданными параметрами

        Args:
            position (tuple): Координаты
        """
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс игрового объекта 'яблоко'."""

    def __init__(self):
        """Инициализация парметров, свойственных для объекта 'яблоко'."""
        super().__init__()
        self.body_color = APPLE_COLOR
        self.position = self.randomize_position(
            (SCREEN_CENTER_X, SCREEN_CENTER_Y)
        )

    def draw(self):
        """Отрисовка объекта яблоко."""
        center_of_form_x, center_of_form_y = self.position
        coord_of_center = (
            center_of_form_x + GRID_SIZE // 2,
            center_of_form_y + GRID_SIZE // 2
        )
        pg.draw.circle(
            screen,
            self.body_color,
            coord_of_center,
            GRID_SIZE // 2
        )
        pg.draw.circle(
            screen,
            BORDER_COLOR,
            coord_of_center,
            GRID_SIZE // 2,
            1
        )


class Snake(GameObject):
    """Класс игрового объекта 'змейка'."""

    def __init__(self):
        """Инициализация парметров, свойственных для объекта 'змейка'."""
        super().__init__()
        self.body_color = SNAKE_COLOR
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.positions = [(SCREEN_CENTER_X, SCREEN_CENTER_Y)]
        self.last = self.positions[-1]

    def get_head_position(self):
        """Получение координат 'головы' змейки."""
        return self.positions[0]

    def move(self, eating=False, poisoning=False):
        """Движение змейки.

        Args:
            eating (bool): Столкновение головы змейки с яблоком.
            poisoning (bool): Столкновение головы змейки с ядом.
        """
        (current_head_position_x,
         current_head_position_y) = self.get_head_position()
        dx, dy = self.direction
        new_head_position_x = (
            (current_head_position_x + dx * GRID_SIZE) % SCREEN_WIDTH
        )
        new_head_position_y = (
            (current_head_position_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        )
        new_head_position = (new_head_position_x, new_head_position_y)
        self.positions.insert(0, new_head_position)
        if eating:
            self.length += 1
        if poisoning:
            self.length -= 1
        while len(self.positions) != self.length:
            self.last = self.positions.pop()

    def draw(self):
        """Отрисовка объекта змейка."""
        for position in self.positions[1:]:
            self.draw_rect(position)

        # Отрисовка головы змейки путем "склеивания" круга и прямоугольника
        # в ячейке. Круг рисуется всегда, а прямоугольник перерисовывается
        # в зависимости от направления движения (для полукруглой головы змейки)
        center_of_form_x, center_of_form_y = self.get_head_position()
        coord_of_circle = (
            center_of_form_x + GRID_SIZE // 2,
            center_of_form_y + GRID_SIZE // 2,
        )
        if self.direction == RIGHT:
            coord_of_rect = (
                center_of_form_x,
                center_of_form_y
            )
            head_rect = pg.Rect(coord_of_rect, (GRID_SIZE // 2, GRID_SIZE))
        if self.direction == LEFT:
            coord_of_rect = (
                center_of_form_x + GRID_SIZE // 2,
                center_of_form_y
            )
            head_rect = pg.Rect(coord_of_rect, (GRID_SIZE // 2, GRID_SIZE))
        if self.direction == UP:
            coord_of_rect = (
                center_of_form_x,
                center_of_form_y + GRID_SIZE // 2
            )
            head_rect = pg.Rect(coord_of_rect, (GRID_SIZE, GRID_SIZE // 2))
        if self.direction == DOWN:
            coord_of_rect = (
                center_of_form_x,
                center_of_form_y
            )
            head_rect = pg.Rect(coord_of_rect, (GRID_SIZE, GRID_SIZE // 2))

        pg.draw.circle(
            screen,
            self.body_color,
            coord_of_circle,
            GRID_SIZE // 2
        )
        pg.draw.circle(
            screen,
            BORDER_COLOR,
            coord_of_circle,
            GRID_SIZE // 2,
            1
        )

        pg.draw.rect(screen, self.body_color, head_rect)
        pg.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def update_direction(self, new_direction):
        """Обновляет направление движения змейки после нажатия клавиши."""
        self.direction = new_direction

    def reset(self, apple, obstacle, poison):
        """Инициализирует начальные параметры игры."""
        self.positions = [(SCREEN_CENTER_X, SCREEN_CENTER_Y)]
        self.length = 1
        self.direction = choice((UP, DOWN, LEFT, RIGHT))
        GameObject.occupied_cells.clear()
        obstacle.position = obstacle.randomize_position(self.positions)
        apple.position = apple.randomize_position(self.positions)
        poison.position = poison.randomize_position(self.positions)
        GameObject.speed_game = 15


class Obstacle(GameObject):
    """Класс игрового объекта 'препятствие'."""

    def __init__(self):
        """Инициализация парметров, свойственных для объекта 'препятствие'."""
        super().__init__()
        self.body_color = OBSTACLE_COLOR
        self.position = self.randomize_position(
            (SCREEN_CENTER_X, SCREEN_CENTER_Y)
        )

    def draw(self):
        """Отрисовка объекта препятствие."""
        self.draw_rect(self.position)


class Poison(GameObject):
    """Класс игрового объекта 'яд'."""

    def __init__(self):
        """Инициализация парметров, свойственных для объекта 'яд'."""
        super().__init__()
        self.body_color = POISON_COLOR
        self.position = Poison.randomize_position(
            (SCREEN_CENTER_X, SCREEN_CENTER_Y)
        )

    def draw(self):
        """Отрисовка объекта яд."""
        center_of_form_x, center_of_form_y = self.position
        listpoint = [
            (center_of_form_x + GRID_SIZE // 2, center_of_form_y),
            (center_of_form_x, center_of_form_y + GRID_SIZE),
            (center_of_form_x + GRID_SIZE, center_of_form_y + GRID_SIZE)
        ]
        pg.draw.polygon(screen, self.body_color, listpoint)
        pg.draw.polygon(screen, BORDER_COLOR, listpoint, 1)


def handle_keys(game_object):
    """Обрабатывает нажатие клавиш направления движения.

    Arg:
        game_object (Snake): Объект класса Snake.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.update_direction(UP)
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.update_direction(DOWN)
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.update_direction(LEFT)
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.update_direction(RIGHT)


def check_eating(snake, apple):
    """Проверяет столкновение головы змейки и яблока.

    Args:
        snake (Snake): Объект класса Snake.
        apple (Apple): Объект класса Apple.

    Returns:
        bool: Было ли столкновение.
    """
    if snake.get_head_position() == apple.position:
        snake.move(eating=True)
        GameObject.occupied_cells.remove(apple.position)
        apple.position = apple.randomize_position(snake.positions)
        if snake.length % 3 == 0:
            GameObject.speed_game += 1
    else:
        return True


def check_poisoning(snake, apple, obstacle, poison):
    """Проверяет столкновение головы змейки и яда.

    Args:
        snake (Snake): Объект класса Snake.
        apple (Apple): Объект класса Apple.
        obstacle (Obstacle): Объект класса Obstacle.
        poison (Poison): Объект класса Poison.

    Returns:
        bool: Было ли столкновение.
    """
    if snake.get_head_position() == poison.position:
        if snake.length == 1:
            snake.reset(apple, obstacle, poison)
        else:
            snake.move(poisoning=True)
            GameObject.occupied_cells.remove(poison.position)
            poison.position = poison.randomize_position(snake.positions)
            return True


def check_collision(snake, apple, obstacle, poison):
    """Проверяет столкновение головы змейки с совим "телом" и препятствием.

    Args:
        snake (Snake): Объект класса Snake.
        apple (Apple): Объект класса Apple.
        obstacle (Obstacle): Объект класса Obstacle.
        poison (Poison): Объект класса Poison.
    """
    if (snake.get_head_position() in snake.positions[1:]
            or snake.get_head_position() == obstacle.position):
        snake.reset(apple, obstacle, poison)
        screen.fill((0, 0, 0))


def main():
    """Выполняет основной цикл игры."""
    # Инициализация pg:
    pg.init()

    snake = Snake()
    apple = Apple()
    obstacle = Obstacle()
    poison = Poison()

    while True:
        clock.tick(GameObject.speed_game)
        screen.fill((0, 0, 0))
        # Тут опишите основную логику игры.
        if (not check_eating(snake, apple)
                or not check_poisoning(snake, apple, obstacle, poison)):
            snake.move()
        check_collision(snake, apple, obstacle, poison)
        handle_keys(snake)
        snake.draw()
        obstacle.draw()
        poison.draw()
        apple.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
