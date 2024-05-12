from settings import *
from random import choice
from timer import Timer


class Tooth(pygame.sprite.Sprite):
    """Running enemy."""

    def __init__(self, pos, frames, groups, collision_sprites):
        """Initialize the Tooth object with position, frames, groups, and collision_sprites."""
        super().__init__(groups)
        self.frames, self.frame_index = frames, 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(topleft=pos)
        self.z = Z_LAYERS['main']

        self.direction = choice((-1, 1))
        self.collision_rects = [sprite.rect for sprite in collision_sprites]
        self.speed = 200

        self.hit_timer = Timer(250)

    def reverse(self):
        """Reverse the direction of the enemy."""
        if not self.hit_timer.active:
            self.direction *= -1
            self.hit_timer.activate()

    def update(self, dt):
        """Update the enemy's movement."""
        self.hit_timer.update()

        # animate
        self.frame_index += ANIMATION_SPEED * dt
        self.image = self.frames[int(self.frame_index % len(self.frames))]
        self.image = pygame.transform.flip(self.image, True, False) if self.direction < 0 else self.image

        # move
        self.rect.x += self.direction * self.speed * dt

        # reverse direction
        floor_rect_right = pygame.FRect(self.rect.bottomright, (1, 1))
        floor_rect_left = pygame.FRect(self.rect.bottomleft, (-1, 1))
        wall_rect = pygame.FRect(self.rect.topleft + vector(-1, 0), (self.rect.width + 2, 1))

        # check if the enemy is about to fall off the edge
        if floor_rect_right.collidelist(self.collision_rects) < 0 < self.direction or \
                floor_rect_left.collidelist(self.collision_rects) < 0 and self.direction < 0 or \
                wall_rect.collidelist(self.collision_rects) != -1:
            self.direction *= -1


class Canon(pygame.sprite.Sprite):
    """Canon enemy."""

    def __init__(self, pos, frames, groups, reverse, player, create_canonball):
        """Initialize the Canon object with position, frames, groups, reverse, player, and create_canonball."""
        super().__init__(groups)

        # reverse the frames if needed
        if reverse:
            self.frames = {}
            for key, surfs in frames.items():
                self.frames[key] = [pygame.transform.flip(surf, True, False) for surf in surfs]
            self.bullet_direction = -1
        else:
            self.frames = frames
            self.bullet_direction = 1

        # init
        self.frame_index = 0
        self.state = 'idle'
        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_frect(topleft=pos)
        self.old_rect = self.rect.copy()
        self.z = Z_LAYERS['main']
        self.player = player
        self.shoot_timer = Timer(3000)
        self.has_fired = False
        self.create_canonball = create_canonball

    def state_management(self):
        """Check if the player is in range."""
        player_pos, canon_pos = vector(self.player.hitbox_rect.center), vector(self.rect.center)
        player_near = canon_pos.distance_to(player_pos) < 500
        player_front = canon_pos.x < player_pos.x if self.bullet_direction > 0 else canon_pos.x > player_pos.x
        player_level = abs(canon_pos.y - player_pos.y) < 30

        # check if the player is in range and in front of the canon
        if player_near and player_front and player_level and not self.shoot_timer.active:
            self.state = 'fire'
            self.frame_index = 0
            self.shoot_timer.activate()

    def update(self, dt):
        """Update the canon's state and animation."""
        self.shoot_timer.update()
        self.state_management()

        # animation / attack
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index < len(self.frames[self.state]):
            self.image = self.frames[self.state][int(self.frame_index)]

            # fire
            if self.state == 'fire' and int(self.frame_index) == 3 and not self.has_fired:
                self.create_canonball(self.rect.center, self.bullet_direction)
                self.has_fired = True

        else:
            # reset
            self.frame_index = 0
            if self.state == 'fire':
                self.state = 'idle'
                self.has_fired = False


class Ball(pygame.sprite.Sprite):
    """Canon bullet."""

    def __init__(self, pos, groups, surf, direction, speed):
        """Initialize the Ball object with position, groups, surf, direction, and speed."""
        self.canonball = True
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center=pos + vector(48 * direction, 0))
        self.direction = direction
        self.speed = speed
        self.z = Z_LAYERS['main']
        self.timers = {'lifetime': Timer(5000), 'reverse': Timer(250)}
        self.timers['lifetime'].activate()

    def reverse(self):
        """Reverse the direction of the bullet."""
        if not self.timers['reverse'].active:
            self.direction *= -1
            self.timers['reverse'].activate()

    def update(self, dt):
        """Update the bullet's movement."""
        for timer in self.timers.values():
            timer.update()

        # move
        self.rect.x += self.direction * self.speed * dt
        if not self.timers['lifetime'].active:
            self.kill()
