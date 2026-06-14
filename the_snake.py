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

# Исходное положение змейки
START_SNAKE_POSITION = (SCREEN_CENTER_X, SCREEN_CENTER_Y)

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов"""

    def __init__(self):
        """Инициализирует базовые параметры объекта."""
        self.board_background_color = BOARD_BACKGROUND_COLOR
        self.border_color = BORDER_COLOR
        self.position = (SCREEN_CENTER_X, SCREEN_CENTER_Y)
        # Задаю цвет в явном виде, т.к. есть проверка PyTest
        self.body_color = None

    def draw():
        """Отрисовка объекта — должен быть реализован в подклассах."""

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

    def __init__(self, occupied_cells=None):
        """Инициализация парметров, свойственных для объекта 'яблоко'."""
        super().__init__()
        self.body_color = APPLE_COLOR
        self.position = self.randomize_position(occupied_cells)

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

    @staticmethod
    def randomize_position(occupied_cells):
        """Задает уникальное положение объекта.

        Args:
            occupied_cells (list[tuple]): Координаты занятый ячеек.

        Returns:
            tuple: Положение объекта.
        """
        while True:
            coordinate_x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            coordinate_y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            new_coordinate = (coordinate_x, coordinate_y)
            if occupied_cells is not None:
                match_position = False
                for position in occupied_cells:
                    if isinstance(position, list):
                        for point in position:
                            if new_coordinate == point:
                                match_position = True
                    elif new_coordinate == position:
                        match_position = True
                    if match_position:
                        break
                if match_position:
                    continue
            return new_coordinate


class Snake(GameObject):
    """Класс игрового объекта 'змейка'."""

    def __init__(self):
        """Инициализация парметров, свойственных для объекта 'змейка'."""
        super().__init__()
        self.body_color = SNAKE_COLOR
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.positions = [START_SNAKE_POSITION]
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

    def reset(self):
        """Инициализирует начальные параметры объекта змейка."""
        self.positions = [START_SNAKE_POSITION]
        self.length = 1
        self.direction = choice((UP, DOWN, LEFT, RIGHT))


class Obstacle(Apple):
    """Класс игрового объекта 'препятствие'."""

    def __init__(self, occupied_cells=None):
        """Инициализация парметров, свойственных для объекта 'препятствие'."""
        super().__init__(occupied_cells)
        self.body_color = OBSTACLE_COLOR

    def draw(self):
        """Отрисовка объекта препятствие."""
        self.draw_rect(self.position)


class Poison(Apple):
    """Класс игрового объекта 'яд'."""

    def __init__(self, occupied_cells=None):
        """Инициализация парметров, свойственных для объекта 'яд'."""
        super().__init__(occupied_cells)
        self.body_color = POISON_COLOR

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
        return True


def check_poisoning(snake, poison):
    """Проверяет столкновение головы змейки и яда.

    Args:
        snake (Snake): Объект класса Snake.
        poison (Poison): Объект класса Poison.

    Returns:
        bool: Было ли столкновение.
    """
    if snake.get_head_position() == poison.position:
        snake.move(poisoning=True)
        return True


def check_collision(snake, obstacle):
    """Проверяет столкновение головы змейки с совим "телом" и препятствием.

    Args:
        snake (Snake): Объект класса Snake.
        obstacle (Obstacle): Объект класса Obstacle.
    Returns:
        bool: Было ли столкновение.
    """
    if (snake.get_head_position() in snake.positions[1:]
            or snake.get_head_position() == obstacle.position):
        return True


def check_the_match_of_positions(
    occupied_cells,
    snake,
    apple,
    obstacle,
    poison
):
    """Проверяет совпадение координат объектов и обновляет положение объектов.

    Args:
        occupied_cells (list): Список занятых ячеек.
        snake (Snake): Объект класса Snake.
        apple (Apple): Объект класса Apple.
        obstacle (Obstacle): Объект класса Obstacle.
        poison (Poison): Объект класса Poison.
    Returns:
        list: Обновленный список занятых ячеек.
    """
    occupied_cells.append(snake.positions)
    if apple.position in occupied_cells:
        apple.position = Apple.randomize_position(occupied_cells)
    occupied_cells.append(apple.position)

    if obstacle.position in occupied_cells:
        obstacle.position = Apple.randomize_position(occupied_cells)
    occupied_cells.append(obstacle.position)

    if poison.position in occupied_cells:
        poison.position = Apple.randomize_position(occupied_cells)
    occupied_cells.append(poison.position)
    return occupied_cells


def update_position(occupied_cells, snake, game_object):
    """Обновляет положение объекта после игрового действия.

    Args:
        occupied_cells (list): Список занятых ячеек.
        snake (Snake): Объект класса Snake.
        object (object): Объект класса.
    Returns:
        list: Обновленный список занятых ячеек.
    """
    occupied_cells.pop(0)
    occupied_cells.insert(0, snake.positions)
    new_position = Apple.randomize_position(occupied_cells)
    if game_object.position in occupied_cells:
        occupied_cells.remove(game_object.position)
        game_object.position = new_position
        occupied_cells.append(game_object.position)
    return occupied_cells


def reset_game(
    occupied_cells,
    snake,
    apple,
    obstacle,
    poison
):
    """Задает начальные параметры объектов.

    Args:
        occupied_cells (list): Список занятых ячеек.
        snake (Snake): Объект класса Snake.
        apple (Apple): Объект класса Apple.
        obstacle (Obstacle): Объект класса Obstacle.
        poison (Poison): Объект класса Poison.
    Returns:
        list: Обновленный список занятых ячеек.
    """
    snake.reset()
    occupied_cells.clear()
    apple.position = apple.randomize_position(occupied_cells)
    obstacle.position = obstacle.randomize_position(occupied_cells)
    poison.position = poison.randomize_position(occupied_cells)
    return check_the_match_of_positions(
        occupied_cells,
        snake,
        apple,
        obstacle,
        poison
    )


def main():
    """Выполняет основной цикл игры."""
    # Инициализация pg:
    pg.init()

    speed_game = 15
    occupied_cells = []

    snake = Snake()
    apple = Apple()
    obstacle = Obstacle()
    poison = Poison()

    occupied_cells = check_the_match_of_positions(
        occupied_cells,
        snake,
        apple,
        obstacle,
        poison
    )

    while True:
        clock.tick(speed_game)
        screen.fill((BOARD_BACKGROUND_COLOR))
        if check_eating(snake, apple):
            occupied_cells = update_position(occupied_cells, snake, apple)
            if snake.length % 3 == 0:
                speed_game += 1
        elif check_collision(snake, obstacle):
            occupied_cells = reset_game(
                occupied_cells,
                snake,
                apple,
                obstacle,
                poison
            )
            speed_game = 15
        elif check_poisoning(snake, poison):
            if snake.length < 1:
                occupied_cells = reset_game(
                    occupied_cells,
                    snake,
                    apple,
                    obstacle,
                    poison
                )
                speed_game = 15
            else:
                occupied_cells = update_position(occupied_cells, snake, poison)
                if snake.length % 3 == 0:
                    speed_game -= 1
        else:
            snake.move()
        handle_keys(snake)
        snake.draw()
        obstacle.draw()
        poison.draw()
        apple.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
