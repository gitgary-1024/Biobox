import time
import pygame
import random
import math
from pygame.draw import circle
from pygame.locals import *

pygame.init()

screen = pygame.display.set_mode((1000, 600))

font = pygame.font.Font(None, 15)  # 使用默认字体，设置字号为15
clock = pygame.time.Clock()
fps = 120

running = True
debug = False

all_oxygen = 1000  # 总共有1000点氧气

season_cycle = 60  # 四个季节周期为60秒
season_amplitude = 2  # 决定速度变化幅度
base_speed_blue = 1  # 蓝球的基础速度
base_speed_predator = 2  # 捕食者的基础速度

oxygen_gain_probability = 0.01  # 1%概率获得剩余氧气的一部分


# noinspection PyMethodMayBeStatic
class Student:
    def __init__(self, x, y):
        self.location = [x, y]
        self.speed = random.uniform(3, 6)  # 随机速度
        self.angle = random.uniform(0, 2 * math.pi)  # 随机方向
        self.radius = 5  # 球的半径
        self.perception_radius = random.randint(10, 50)  # 感知半径
        self.oxygen = 0  # 初始氧气总量
        self.current_cooldown = 0  # 当前繁育冷却计时器
        self.life = random.randint(100, 1000)

    def move(self, circles, predator):

        if self.life != 0:
            self.life -= 1

        if self.current_cooldown != 0:
            self.current_cooldown -= 1

        # 检查氧气获取
        self.collect_oxygen()

        # 躲避捕食者
        self.avoid_predator(predator)

        # 更新位置
        self.location[0] += self.speed * 0.5 * math.cos(self.angle)
        self.location[1] += self.speed * 0.5 * math.sin(self.angle)
        self.check_bounds()
        self.flocking(circles)

    def get_speed(self):
        time_passed = time.time() % season_cycle  # 获取当前时间的周期
        season_factor = (1 + season_amplitude * math.sin((time_passed / season_cycle) * (2 * math.pi)))  # 计算季节因子
        return base_speed_blue * season_factor  # 根据季节因子调整速度

    def collect_oxygen(self):
        global all_oxygen
        # 每帧有一定概率获得剩余的氧气的一部分
        if random.random() < oxygen_gain_probability:  # 1%概率
            oxygen_gain = random.uniform(0, all_oxygen)  # 获得剩余氧气的一部分
            self.oxygen += oxygen_gain  # 增加氧气
            all_oxygen -= oxygen_gain

    def check_bounds(self):
        if self.location[0] < self.radius:  # 左边界
            self.location[0] = self.radius
            self.angle = math.pi - self.angle
        elif self.location[0] > 600 - self.radius:  # 右边界
            self.location[0] = 600 - self.radius
            self.angle = math.pi - self.angle

        if self.location[1] < self.radius:  # 上边界
            self.location[1] = self.radius
            self.angle = -self.angle
        elif self.location[1] > 600 - self.radius:  # 下边界
            self.location[1] = 600 - self.radius
            self.angle = -self.angle

    def flocking(self, circles):
        alignment = [0, 0]
        cohesion = [0, 0]
        separation = [0, 0]
        total = 0

        for other in circles:
            if other != self:
                distance = math.sqrt(
                    (self.location[0] - other.location[0]) ** 2 + (self.location[1] - other.location[1]) ** 2)

                if distance < self.perception_radius:
                    # 对齐行为
                    alignment[0] += math.cos(other.angle)
                    alignment[1] += math.sin(other.angle)

                    # 聚集行为
                    cohesion[0] += other.location[0]
                    cohesion[1] += other.location[1]

                    # 分离行为
                    if distance < 10:  # 10个像素内分离
                        separation[0] -= (other.location[0] - self.location[0])
                        separation[1] -= (other.location[1] - self.location[1])

                    total += 1

        if total > 0:
            # 对齐
            alignment[0] /= total
            alignment[1] /= total

            # 聚集
            cohesion[0] /= total
            cohesion[1] /= total
            cohesion[0] = (cohesion[0] - self.location[0]) * 0.01
            cohesion[1] = (cohesion[1] - self.location[1]) * 0.01

            self.angle += math.atan2(alignment[1], alignment[0]) * 0.05
            self.angle += math.atan2(cohesion[1], cohesion[0]) * 0.05
            self.location[0] += separation[0] * 0.1
            self.location[1] += separation[1] * 0.1

    def avoid_predator(self, predator):
        predator_distance = math.sqrt((self.location[0] - predator.location[0]) ** 2 +
                                      (self.location[1] - predator.location[1]) ** 2)

        if predator_distance < predator.radius + self.perception_radius:
            avoidance_angle = math.atan2(self.location[1] - predator.location[1],
                                         self.location[0] - predator.location[0])
            self.angle = avoidance_angle + random.uniform(0.5, 1.5)

    def draw(self, screen, show_debug):
        circle(screen, (0, 0, 255), (int(self.location[0]), int(self.location[1])), self.radius)
        # 绘制重要参数
        if show_debug:
            stats = f"Speed: {self.speed:.1f}, Oxygen: {self.oxygen:.1f}, Cooldown: {self.current_cooldown}"
            text_surface = font.render(stats, True, (0, 0, 0))
            screen.blit(text_surface, (self.location[0] - self.radius, self.location[1] + self.radius))

    def get_rect(self):
        return pygame.Rect(self.location[0] - self.radius, self.location[1] - self.radius, self.radius * 2,
                           self.radius * 2)

    def check_death(self, circles_blue):
        # if self.life <= 0:
        #     circles_blue.remove(self)
        return False

    def can_spawn(self):
        return self.oxygen > 0 >= self.current_cooldown  # 判断是否可以繁殖


# noinspection PyMethodMayBeStatic
class Teacher:
    def __init__(self, x, y):
        self.location = [x, y]
        self.speed = 1  # 捕食者速度
        self.radius = 5  # 捕食者的半径
        self.perception_radius = 20  # 感知半径
        self.capture_count = 0  # 捕获的蓝球数量
        self.time_capture = 100

    def move(self, prey, predators):

        if self.time_capture != 0:
            self.time_capture -= 1

        self.flocking(predators)

        if prey:
            closest_prey = min(prey, key=lambda p: math.sqrt(
                (self.location[0] - p.location[0]) ** 2 + (self.location[1] - p.location[1]) ** 2))
            direction_x = closest_prey.location[0] - self.location[0]
            direction_y = closest_prey.location[1] - self.location[1]
            distance = math.sqrt(direction_x ** 2 + direction_y ** 2)

            if distance > 0:
                direction_x /= distance
                direction_y /= distance

                self.location[0] += direction_x * self.speed
                self.location[1] += direction_y * self.speed

        self.check_bounds()

    def get_speed(self):
        time_passed = time.time() % season_cycle  # 获取当前时间的周期
        season_factor = (1 + season_amplitude * math.sin((time_passed / season_cycle) * (2 * math.pi)))  # 计算季节因子
        return base_speed_predator * season_factor  # 根据季节因子调整速度

    def check_bounds(self):
        if self.location[0] < self.radius:  # 左边界
            self.location[0] = self.radius
        elif self.location[0] > 600 - self.radius:  # 右边界
            self.location[0] = 600 - self.radius

        if self.location[1] < self.radius:  # 上边界
            self.location[1] = self.radius
        elif self.location[1] > 600 - self.radius:  # 下边界
            self.location[1] = 600 - self.radius

    def flocking(self, predators):
        alignment = [0, 0]
        separation = [0, 0]
        total = 0

        for other in predators:
            if other != self:
                distance = math.sqrt(
                    (self.location[0] - other.location[0]) ** 2 + (self.location[1] - other.location[1]) ** 2)
                if distance < self.perception_radius:
                    # # 对齐行为
                    # alignment[0] += math.cos(other.location[0])
                    # alignment[1] += math.sin(other.location[1])

                    # 分离行为
                    if distance < 10:  # 若距离小于10像素，分离
                        separation[0] -= (other.location[0] - self.location[0])
                        separation[1] -= (other.location[1] - self.location[1])

                    total += 1

        if total > 0:
            alignment[0] /= total
            alignment[1] /= total
            self.angle = math.atan2(alignment[1], alignment[0])
            self.location[0] += separation[0] * 0.1  # 更新位置
            self.location[1] += separation[1] * 0.1

    def draw(self, screen, show_debug):
        circle(screen, (255, 0, 0), (int(self.location[0]), int(self.location[1])), self.radius)
        # 绘制重要参数
        if show_debug:
            stats = f"Captures: {self.capture_count},Speed:{self.speed}, Time left: {self.time_capture}"
            text_surface = font.render(stats, True, (0, 0, 0))
            screen.blit(text_surface, (self.location[0] - self.radius, self.location[1] + self.radius))

    def check_capture(self, prey):
        global all_oxygen
        for p in prey.copy():
            if self.get_rect().colliderect(p.get_rect()):
                prey.remove(p)
                all_oxygen += p.oxygen  # 捕食者释放氧气
                self.capture_count += 1  # 捕获时递增计数器
                self.time_capture = random.randint(100, 600)

    def check_death(self, predators):
        if self.time_capture <= 0:
            predators.remove(self)

    def can_spawn(self):
        return 6 <= self.capture_count  # 捕食者是否可以繁殖

    def reproduce(self):
        if self.can_spawn():
            new_x = self.location[0] + random.uniform(-20, 20)
            new_y = self.location[1] + random.uniform(-20, 20)
            new_predator = Teacher(new_x, new_y)
            return new_predator
        return None

    def get_rect(self):
        return pygame.Rect(self.location[0] - self.radius, self.location[1] - self.radius, self.radius * 2,
                           self.radius * 2)


def check_collision_and_spawn(circles):
    for i in range(len(circles)):
        if circles[i].oxygen >= 2:
            circles.append(Student(circles[i].location[0], circles[i].location[1]))  # 添加新生成的蓝球
        for j in range(i + 1, len(circles)):
            circle_a = circles[i]
            circle_b = circles[j]
            distance = math.sqrt(
                (circle_a.location[0] - circle_b.location[0]) ** 2 + (circle_a.location[1] - circle_b.location[1]) ** 2)

            if distance < circle_a.radius + circle_b.radius + 10 and (
                    circle_a.oxygen >= 1 or circle_b.oxygen >= 1):  # 如果两个蓝球相碰
                if circle_a.can_spawn() and circle_b.can_spawn() and not random.randint(0, 10):  # 检查是否都可以繁殖
                    for _ in range(random.randint(1, 2)):
                        new_x = (circle_a.location[0] + circle_b.location[0]) / 2 + random.uniform(-5, 5)
                        new_y = (circle_a.location[1] + circle_b.location[1]) / 2 + random.uniform(-5, 5)
                        new_circle = Student(new_x, new_y)
                        new_circle.perception_radius = max(10, (
                                circle_a.perception_radius + circle_b.perception_radius) / 2 + random.randint(-5,
                                                                                                              5))  # 新蓝球的感知半径
                        new_circle.current_cooldown = 100
                        new_circle.oxygen = (circle_a.oxygen + circle_b.oxygen) / 2
                        circle_a.oxygen /= 2
                        circle_b.oxygen /= 2
                        new_circle.speed = max(1, (circle_a.speed + circle_b.speed) // 2 + random.randint(-2, 4))
                        new_circle.speed = min(10, new_circle.speed)

                        circles.append(new_circle)  # 添加新生成的蓝球
                    return  # 防止重复生成


count_Student, count_Teacher, count_fps, count_oxygen = [0] * 400, [0] * 400, [0] * 400, [0] * 400


def show_debug(screen, count_student, count_teacher):
    # 调整基线高度，设置为600，这样可以在屏幕的下方绘制数据
    base_height = 600

    # 绘制学生数量的线条
    for i in range(len(count_student) - 1):
        # 确保绘制坐标在屏幕范围内
        pygame.draw.line(screen, (0, 0, 255),
                         (i + 600, min(600, base_height - count_student[i])),  # 当前点
                         (i + 601, min(600, base_height - count_student[i + 1])),  # 下一个点
                         1)

    # 绘制捕食者数量的线条
    for i in range(len(count_teacher) - 1):
        # 确保绘制坐标在屏幕范围内
        pygame.draw.line(screen, (255, 0, 0),
                         (i + 600, min(600, base_height - count_teacher[i])),  # 当前点
                         (i + 601, min(600, base_height - count_teacher[i + 1])),  # 下一个点
                         1)

    for i in range(len(count_fps) - 1):
        # 确保绘制坐标在屏幕范围内
        pygame.draw.line(screen, (0, 255, 0),
                         (i + 600, min(600, base_height - count_fps[i])),  # 当前点
                         (i + 601, min(600, base_height - count_fps[i + 1])),  # 下一个点
                         1)

    for i in range(len(count_fps) - 1):
        # 确保绘制坐标在屏幕范围内
        pygame.draw.line(screen, (0, 0, 0),
                         (i + 600, min(600, base_height - count_oxygen[i])),  # 当前点
                         (i + 601, min(600, base_height - count_oxygen[i + 1])),  # 下一个点
                         1)


def main():
    # 创建一些蓝色的球和捕食者
    global running, debug
    circles_blue = [Student(random.randint(0, 600), random.randint(0, 600)) for _ in range(20)]
    predators = [Teacher(random.randint(300, 500), random.randint(300, 500)) for _ in range(5)]

    predators.append(Teacher(10, 10))

    index = 0

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_d]:
            debug = not debug
            print(debug)

        screen.fill((255, 255, 255))

        for blue_circle in circles_blue:
            closest_predator = min(predators, key=lambda p: math.sqrt(
                (blue_circle.location[0] - p.location[0]) ** 2 + (blue_circle.location[1] - p.location[1]) ** 2))
            blue_circle.move(circles_blue, closest_predator)
            blue_circle.draw(screen, debug)
            blue_circle.check_death(circles_blue)

        time_passed = time.time() % season_cycle  # 获取当前时间的周期
        season_factor = (1 + season_amplitude * math.sin((time_passed / season_cycle) * (2 * math.pi)))  # 计算季节因子
        if time_passed / season_factor > 1 / 8:
            pass

        for predator in predators:
            predator.move(circles_blue, predators)
            predator.check_capture(circles_blue)
            predator.draw(screen, debug)
            if predator.capture_count >= 6:
                predators.append(Teacher(predator.location[0], predator.location[1]))  # 添加新捕食者
                predator.capture_count /= 2
            # 检查捕食者之间的繁殖
            for other_predator in predators:
                if predator != other_predator and predator.can_spawn() and other_predator.can_spawn():
                    distance = math.sqrt((predator.location[0] - other_predator.location[0]) ** 2 +
                                         (predator.location[1] - other_predator.location[1]) ** 2)
                    if distance < predator.radius + other_predator.radius + 10:  # 碰撞范围
                        # if random.randint(1, 100) <= 5 and len(predators) >= 20:  # 意外死亡
                        #     predators.remove(predator)
                        #     predators.remove(other_predator)
                        #     continue

                        for _ in range(random.randint(0, 1)):
                            new_predator = predator.reproduce()
                            if new_predator:
                                new_predator.speed = max(1,
                                                         int(predator.get_speed() + other_predator.get_speed()) // 2 + random.randint(
                                                             -2, 1))
                                new_predator.speed = min(3, new_predator.speed)
                                predators.append(new_predator)  # 添加新捕食者
                                predator.capture_count /= 2
                                other_predator.capture_count /= 2
        for predator in predators[:]:
            predator.move(circles_blue, predators)
            predator.check_capture(circles_blue)
            # predator.draw(screen)
            predator.check_death(predators)  # 检查是否该捕食者死亡

        if not predators or not circles_blue:
            print("End")
            continue

        check_collision_and_spawn(circles_blue)  # 检测是否有蓝球相碰并生成新的蓝球

        stats = f"All oxygen: {all_oxygen}"
        text_surface = font.render(stats, True, (255, 0, 255))
        screen.blit(text_surface, (600, 0))
        stats = f"Student:{len(circles_blue)}，Teacher:{len(predators)}"
        text_surface = font.render(stats, True, (255, 0, 255))
        screen.blit(text_surface, (600, 10))
        stats = f"Fps:{clock.get_fps()},Season:{circles_blue[0].get_speed()}"
        text_surface = font.render(stats, True, (255, 0, 255))
        screen.blit(text_surface, (600, 20))

        index %= 400
        count_Student[index] = len(circles_blue)
        count_Teacher[index] = len(predators)
        count_fps[index] = int(clock.get_fps())
        count_oxygen[index] = all_oxygen
        index += 1

        show_debug(screen, count_Student, count_Teacher)

        pygame.display.flip()

        clock.tick(fps)


main()
pygame.quit()
