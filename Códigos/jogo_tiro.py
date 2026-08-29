import pygame
import random

pygame.init()

LARGURA = 800
ALTURA = 600

FPS = 60
clock = pygame.time.Clock()


def gerar_posicao_borda():
    lado = random.choice(['cima', 'baixo', 'esquerda', 'direita'])

    if lado == 'cima':
        x = random.randint(0, LARGURA - 40)
        y = -40
    elif lado == 'baixo':
        x = random.randint(0, LARGURA - 40)
        y = ALTURA + 40
    elif lado == 'esquerda':
        x = -40
        y = random.randint(0, ALTURA - 40)
    else:  # direita
        x = LARGURA + 40
        y = random.randint(0, ALTURA - 40)

    return x, y, lado


# CLASSE BASE
class Entidade(pygame.sprite.Sprite):
    def __init__(self, x, y, velocidade):
        super().__init__()
        self.velocidade = velocidade
        self.image = pygame.Surface((40, 40))
        self.rect = self.image.get_rect(center=(x, y))

    def mover(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy


# JOGADOR
class Jogador(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 5)
        self.image.fill((0, 255, 0))  # verde
        self.vida = 5
        self.direcao_atual = (0, -1)  # começa "olhando" pra cima

    def update(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.mover(0, -self.velocidade)
            self.direcao_atual = (0, -1)
        if keys[pygame.K_s]:
            self.mover(0, self.velocidade)
            self.direcao_atual = (0, 1)
        if keys[pygame.K_a]:
            self.mover(-self.velocidade, 0)
            self.direcao_atual = (-1, 0)
        if keys[pygame.K_d]:
            self.mover(self.velocidade, 0)
            self.direcao_atual = (1, 0)

        # limites de tela
        self.rect.x = max(0, min(self.rect.x, LARGURA - 40))
        self.rect.y = max(0, min(self.rect.y, ALTURA - 40))


# TIRO (DO JOGADOR)
class Tiro(Entidade):
    def __init__(self, x, y, direcao):
        super().__init__(x, y, 10)
        self.image.fill((255, 255, 0))  # amarelo
        self.dx, self.dy = direcao

    def update(self):
        self.rect.x += self.dx * self.velocidade
        self.rect.y += self.dy * self.velocidade

        # remove o tiro se sair da tela em qualquer direção
        if (self.rect.right < 0 or self.rect.left > LARGURA or
                self.rect.bottom < 0 or self.rect.top > ALTURA):
            self.kill()


# ROBO BASE
class Robo(Entidade):
    def __init__(self, x, y, velocidade):
        super().__init__(x, y, velocidade)
        self.image.fill((255, 0, 0))  # vermelho

    def atualizar_posicao(self):
        raise NotImplementedError


# ROBO EXEMPLO — ZigueZague
class RoboZigueZague(Robo):
    def __init__(self, x, y, lado):
        super().__init__(x, y, velocidade=3)
        self.lado = lado
        self.direcao = 1

    def atualizar_posicao(self):
        if self.lado in ('cima', 'baixo'):
            self.rect.y += self.velocidade if self.lado == 'cima' else -self.velocidade
            self.rect.x += self.direcao * 3
            if self.rect.x <= 0 or self.rect.x >= LARGURA - 40:
                self.direcao *= -1
        else:
            self.rect.x += self.velocidade if self.lado == 'esquerda' else -self.velocidade
            self.rect.y += self.direcao * 3
            if self.rect.y <= 0 or self.rect.y >= ALTURA - 40:
                self.direcao *= -1

    def update(self):
        self.atualizar_posicao()

        # só remove o robô quando ele sai pelo lado OPOSTO ao de entrada
        saiu = False
        if self.lado == 'cima' and self.rect.top > ALTURA:
            saiu = True
        elif self.lado == 'baixo' and self.rect.bottom < 0:
            saiu = True
        elif self.lado == 'esquerda' and self.rect.left > LARGURA:
            saiu = True
        elif self.lado == 'direita' and self.rect.right < 0:
            saiu = True

        if saiu:
            self.kill()


def iniciar(tela):
    """Roda o loop principal do jogo. Recebe a tela já criada pelo main.py
    (o jogo_tiro não cria mais a própria janela, reaproveita a do menu)."""

    todos_sprites = pygame.sprite.Group()
    inimigos = pygame.sprite.Group()
    tiros = pygame.sprite.Group()

    jogador = Jogador(LARGURA // 2, ALTURA - 60)
    todos_sprites.add(jogador)

    pontos = 0
    spawn_timer = 0

    COOLDOWN_TIRO = 15  # frames de espera entre um tiro e outro (15 frames ~ 0.25s a 60 FPS)
    tiro_timer = 0

    font = pygame.font.SysFont(None, 30)

    rodando = True
    while rodando:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False

        # disparo contínuo enquanto a seta estiver pressionada, limitado pelo cooldown
        tiro_timer += 1
        keys = pygame.key.get_pressed()

        direcao = None
        if keys[pygame.K_UP]:
            direcao = (0, -1)
        elif keys[pygame.K_DOWN]:
            direcao = (0, 1)
        elif keys[pygame.K_LEFT]:
            direcao = (-1, 0)
        elif keys[pygame.K_RIGHT]:
            direcao = (1, 0)

        if direcao and tiro_timer >= COOLDOWN_TIRO:
            tiro = Tiro(jogador.rect.centerx, jogador.rect.centery, direcao)
            todos_sprites.add(tiro)
            tiros.add(tiro)
            tiro_timer = 0

        # timer de entrada dos inimigos
        spawn_timer += 1
        if spawn_timer > 40:
            x, y, lado = gerar_posicao_borda()
            robo = RoboZigueZague(x, y, lado)
            todos_sprites.add(robo)
            inimigos.add(robo)
            spawn_timer = 0

        # colisão tiro x robô
        colisao = pygame.sprite.groupcollide(inimigos, tiros, True, True)
        pontos += len(colisao)

        # colisão robô x jogador
        if pygame.sprite.spritecollide(jogador, inimigos, True):
            jogador.vida -= 1
            if jogador.vida <= 0:
                print("GAME OVER!")
                rodando = False

        # atualizar
        todos_sprites.update()

        # desenhar
        tela.fill((20, 20, 20))
        todos_sprites.draw(tela)

        # Painel de pontos e vida
        texto = font.render(f"Vida: {jogador.vida}  |  Pontos: {pontos}", True, (255, 255, 255))
        tela.blit(texto, (10, 10))

        pygame.display.flip()


# permite continuar testando o jogo_tiro sozinho, sem passar pelo menu
if __name__ == "__main__":
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Robot Defense - Template")
    iniciar(tela)
    pygame.quit()