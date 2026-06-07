from random import choice, randint

import pygame

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
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов"""

    speed_game = 15

    def __init__(self):
        """Инициализирует базовые параметры объекта."""
        self.board_background_color = BOARD_BACKGROUND_COLOR
        self.border_color = BORDER_COLOR
        self.position = (SCREEN_CENTER_X, SCREEN_CENTER_Y)
        self.body_color = None

    def draw():
        """Отрисовка объекта — должен быть реализован в подклассах."""
        pass

    @classmethod
    def game_acceleration(cls, length_of_snake):
        """Увеличивает скорость игры.

        Arg:
            length_of_snake (int): Длина змейки.
        """
        if length_of_snake % 3 == 0:
            cls.speed_game += 1


class Apple(GameObject):
    """Класс игрового объекта "яблоко"."""

    def __init__(self):
        """Инициализация парметров, свойственных для объекта "яблоко"."""
        super().__init__()
        self.body_color = APPLE_COLOR
        self.position = Apple.randomize_position(
            (SCREEN_CENTER_X, SCREEN_CENTER_Y),
            (SCREEN_CENTER_X, SCREEN_CENTER_Y),
            (SCREEN_CENTER_X, SCREEN_CENTER_Y)
        )

    @staticmethod
    def randomize_position(
            snake_positions,
            obstacle_position,
            poison_position
    ):
        """Задает уникальное положение объекта.

        Args:
            snake_positions (list[tuple]): Координаты положения змейки.
            obstacle_position (tuple): Координаты положения препятствия.
            poison_position (tuple): Координаты положения яда.
        """
        while True:
            coordinate_x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            coordinate_y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            new_coordinate = (coordinate_x, coordinate_y)
            try:
                snake_positions.index(new_coordinate)
                obstacle_position.index(new_coordinate)
                poison_position.index(new_coordinate)
                continue
            except ValueError:
                break
        return new_coordinate

    def draw(self):
        """Отрисовка объекта яблоко"""
        center_of_form_x, center_of_form_y = self.position
        coord_of_center = (
            center_of_form_x + GRID_SIZE // 2,
            center_of_form_y + GRID_SIZE // 2
        )
        pygame.draw.circle(
            screen,
            self.body_color,
            coord_of_center,
            GRID_SIZE // 2
        )
        pygame.draw.circle(
            screen,
            BORDER_COLOR,
            coord_of_center,
            GRID_SIZE // 2,
            1
        )


class Snake(GameObject):
    """Класс игрового объекта "змейка"."""

    def __init__(self):
        """Инициализация парметров, свойственных для объекта "змейка"."""
        super().__init__()
        self.body_color = SNAKE_COLOR
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.positions = [(SCREEN_CENTER_X, SCREEN_CENTER_Y)]
        self.last = self.positions[-1]

    def get_head_position(self):
        """Получение координат "головы" змейки."""
        return self.positions[0]

    def move(self, eating=False, poisoning=False):
        """Движение змейки.

        Args:
            eating (bool): Столкновение головы змейки с яблоком.
            poisoning (bool): Столкновение головы змейки с ядом.
        """
        current_head_position_x, \
            current_head_position_y = self.get_head_position()
        dx, dy = self.direction
        new_head_position_x = current_head_position_x + dx * GRID_SIZE
        new_head_position_y = current_head_position_y + dy * GRID_SIZE
        new_head_position = Snake.check_board_field(
            new_head_position_x,
            new_head_position_y
        )
        self.positions.insert(0, new_head_position)
        if eating:
            self.length += 1
            GameObject.game_acceleration(self.length)
        if poisoning:
            self.length -= 1
        while len(self.positions) != self.length:
            self.last = self.positions.pop()

    @staticmethod
    def check_board_field(position_x, position_y):
        """Проверяет выход змейки за границы экрана."""
        if position_x >= SCREEN_WIDTH:
            position_x = 0
        if position_x < 0:
            position_x = SCREEN_WIDTH - GRID_SIZE
        if position_y >= SCREEN_HEIGHT:
            position_y = 0
        if position_y < 0:
            position_y = SCREEN_HEIGHT - GRID_SIZE
        return (position_x, position_y)

    def draw(self):
        """Отрисовка объекта змейка."""
        for position in self.positions[1:]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        center_of_form_x, center_of_form_y = self.positions[0]
        coord_of_circle = (
            center_of_form_x + GRID_SIZE // 2,
            center_of_form_y + GRID_SIZE // 2,
        )
        if self.direction == RIGHT:
            coord_of_rect = (
                center_of_form_x,
                center_of_form_y
            )
            head_rect = pygame.Rect(coord_of_rect, (GRID_SIZE // 2, GRID_SIZE))
        if self.direction == LEFT:
            coord_of_rect = (
                center_of_form_x + GRID_SIZE // 2,
                center_of_form_y
            )
            head_rect = pygame.Rect(coord_of_rect, (GRID_SIZE // 2, GRID_SIZE))
        if self.direction == UP:
            coord_of_rect = (
                center_of_form_x,
                center_of_form_y + GRID_SIZE // 2
            )
            head_rect = pygame.Rect(coord_of_rect, (GRID_SIZE, GRID_SIZE // 2))
        if self.direction == DOWN:
            coord_of_rect = (
                center_of_form_x,
                center_of_form_y
            )
            head_rect = pygame.Rect(coord_of_rect, (GRID_SIZE, GRID_SIZE // 2))

        pygame.draw.circle(
            screen,
            self.body_color,
            coord_of_circle,
            GRID_SIZE // 2
        )
        pygame.draw.circle(
            screen,
            BORDER_COLOR,
            coord_of_circle,
            GRID_SIZE // 2,
            1
        )

        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def update_direction(self):
        """Обновляет направление движения змейки после нажатия клавиши."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def reset(self, apple, obstacle, poison):
        """Инициализирует начальные параметры игры."""
        self.positions = [(SCREEN_CENTER_X, SCREEN_CENTER_Y)]
        self.length = 1
        self.direction = choice((UP, DOWN, LEFT, RIGHT))
        obstacle.postion = obstacle.randomize_position(self.position)
        apple.position = apple.randomize_position(
            self.positions,
            obstacle.position,
            poison.position
        )
        poison.position = poison.randomize_position(
            self.positions,
            obstacle.position,
            apple.position
        )
        GameObject.speed_game = 15


class Obstacle(GameObject):
    """Класс игрового объекта "препятствие"."""

    def __init__(self):
        """Инициализация парметров, свойственных для объекта "препятствие"."""
        super().__init__()
        self.body_color = OBSTACLE_COLOR
        self.position = Obstacle.randomize_position(
            (SCREEN_CENTER_X, SCREEN_CENTER_Y)
        )

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
            try:
                snake_positions.index(new_coordinate)
                continue
            except ValueError:
                break
        return new_coordinate

    def draw(self):
        """Отрисовка объекта препятствие."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Poison(GameObject):
    """Класс игрового объекта "яд"."""

    def __init__(self):
        """Инициализация парметров, свойственных для объекта "яд"."""
        super().__init__()
        self.body_color = POISON_COLOR
        self.position = Poison.randomize_position(
            (SCREEN_CENTER_X, SCREEN_CENTER_Y),
            (SCREEN_CENTER_X, SCREEN_CENTER_Y),
            (SCREEN_CENTER_X, SCREEN_CENTER_Y)
        )

    @staticmethod
    def randomize_position(
            snake_positions,
            obstacle_position,
            apple_position
    ):
        """Задает уникальное положение объекта.

        Args:
            snake_positions (list[tuple]): Координаты положения змейки.
            obstacle_position (tuple): Координаты положения препятствия.
            apple_position (tuple): Координаты положения яблока.
        """
        while True:
            coordinate_x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            coordinate_y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            new_coordinate = (coordinate_x, coordinate_y)
            try:
                snake_positions.index(new_coordinate)
                obstacle_position.index(new_coordinate)
                apple_position.index(new_coordinate)
                continue
            except ValueError:
                break
        return new_coordinate

    def draw(self):
        """Отрисовка объекта яд."""
        center_of_form_x, center_of_form_y = self.position
        listpoint = [
            (center_of_form_x + GRID_SIZE // 2, center_of_form_y),
            (center_of_form_x, center_of_form_y + GRID_SIZE),
            (center_of_form_x + GRID_SIZE, center_of_form_y + GRID_SIZE)
        ]
        pygame.draw.polygon(screen, self.body_color, listpoint)
        pygame.draw.polygon(screen, BORDER_COLOR, listpoint, 1)


def handle_keys(game_object):
    """Обрабатывает нажатие клавиш направления движения.

    Arg:
        game_object (Snake): Объект класса Snake.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT
        game_object.update_direction()


def check_eating(snake, apple, obstacle, poison):
    """Проверяет столкновение головы змейки и яблока.

    Returns:
        bool: Было ли столкновение.
    """
    if snake.get_head_position() == apple.position:
        snake.move(eating=True)
        apple.position = apple.randomize_position(
            snake.positions,
            obstacle.position,
            poison.position
        )
    else:
        return True


def check_poisoning(snake, apple, obstacle, poison):
    """Проверяет столкновение головы змейки и яда.

    Returns:
        bool: Было ли столкновение.
    """
    if snake.get_head_position() == poison.position:
        if snake.length == 1:
            snake.reset(apple, obstacle, poison)
        else:
            snake.move(poisoning=True)
            poison.position = poison.randomize_position(
                snake.positions,
                obstacle.position,
                apple.position
            )
            return True


def check_collision(apple, snake, obstacle, poison):
    """Проверяет столкновение головы змейки с совим "телом" и препятствием."""
    if (snake.get_head_position() in snake.positions[1:]
            or snake.get_head_position() == obstacle.position):
        snake.reset(apple, obstacle, poison)
        screen.fill((0, 0, 0))


def main():
    """Выполняет основной цикл игры."""
    # Инициализация PyGame:
    pygame.init()

    snake = Snake()
    obstacle = Obstacle()
    poison = Poison()
    apple = Apple()

    while True:
        clock.tick(GameObject.speed_game)
        screen.fill((0, 0, 0))
        # Тут опишите основную логику игры.
        snake.draw()
        obstacle.draw()
        poison.draw()
        apple.draw()
        if (not check_eating(snake, apple, obstacle, poison)
                or not check_poisoning(snake, apple, obstacle, poison)):
            snake.move()

        check_collision(apple, snake, obstacle, poison)
        handle_keys(snake)
        pygame.display.update()


if __name__ == '__main__':
    main()
