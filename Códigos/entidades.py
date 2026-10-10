"""Entidades com posição contínua, animação e estado próprio."""

import pygame
from configuracoes import VIDA_INICIAL
from itens import Inventario
from sprites import Animacao


def nome_direcao(vetor):
    if abs(vetor.x) > abs(vetor.y):
        return "direita" if vetor.x > 0 else "esquerda"
    return "baixo" if vetor.y > 0 else "cima"


class Entidade(pygame.sprite.Sprite):
    def __init__(self, posicao, imagem):
        super().__init__()
        self.posicao = pygame.Vector2(posicao)
        self.image = imagem
        self.rect = imagem.get_rect(center=posicao)
        self.mask = pygame.mask.from_surface(imagem)

    @property
    def hitbox(self):
        return self.rect.inflate(-self.rect.width * .40, -self.rect.height * .30)

    def definir_imagem(self, imagem):
        if imagem is not self.image:
            self.image = imagem
            self.rect = imagem.get_rect(center=self.posicao)
            self.mask = pygame.mask.from_surface(imagem)

    def mover(self, deslocamento, limites):
        self.posicao += deslocamento
        self.rect.center = (round(self.posicao.x), round(self.posicao.y))
        limitado = self.rect.clamp(limites)
        if limitado != self.rect:
            self.rect = limitado
            self.posicao.update(self.rect.center)


class EntidadeAnimada(Entidade):
    def __init__(self, posicao, quadros):
        self.animacao = Animacao(quadros)
        super().__init__(posicao, self.animacao.imagem)

    def animar(self, dt, estado, direcao="baixo", repetir=True, intervalo=120):
        self.animacao.selecionar(estado, direcao, repetir, intervalo)
        self.animacao.atualizar(dt)
        self.definir_imagem(self.animacao.imagem)


class Jogador(EntidadeAnimada):
    def __init__(self, x, y, recursos):
        super().__init__((x, y), recursos.jogador)
        self.vida_maxima = VIDA_INICIAL
        self.vida = self.vida_maxima
        self.inventario = Inventario()
        self.escudo = 0
        self.velocidade = 235
        self.direcao = pygame.Vector2(0, -1)
        self.tempo_ataque = 0
        self.tempo_dano = 0
        self.invulneravel = 0
        self.reviver_pendente = False

    @property
    def morte_finalizada(self):
        return self.vida <= 0 and self.animacao.finalizada

    def curar(self, quantidade):
        self.vida = min(self.vida_maxima, self.vida + quantidade)

    def recarregar_escudo(self):
        if self.inventario.possui("escudo"):
            self.escudo = 1

    def sofrer_dano(self, dano=1):
        if self.vida <= 0 or self.invulneravel > 0:
            return False
        self.invulneravel = 1100
        self.tempo_dano = 240
        if self.escudo:
            self.escudo = 0
            return True
        self.vida = max(0, self.vida - dano)
        if self.vida == 0 and self.inventario.possui("vida_extra") and not self.inventario.revive_usado:
            self.vida = 1
            self.inventario.revive_usado = True
            self.invulneravel = 2200
            self.reviver_pendente = True
        return True

    def atacar(self, direcao):
        if direcao.length_squared():
            self.direcao = pygame.Vector2(direcao).normalize()
        self.tempo_ataque = 240

    def atualizar(self, dt, teclas, limites):
        if self.vida <= 0:
            self.animar(dt, "morrer", nome_direcao(self.direcao), repetir=False)
            return
        self.invulneravel = max(0, self.invulneravel - dt)
        movimento = pygame.Vector2(int(teclas[pygame.K_d]) - int(teclas[pygame.K_a]),
                                  int(teclas[pygame.K_s]) - int(teclas[pygame.K_w]))
        if movimento.length_squared():
            movimento = movimento.normalize()
            self.mover(movimento * self.velocidade * dt / 1000, limites)
            if self.tempo_ataque <= 0:
                self.direcao = movimento
        if self.tempo_dano > 0:
            estado = "levar_dano"
        elif self.tempo_ataque > 0:
            estado = "andando_atirando" if movimento.length_squared() else "atirando"
        else:
            estado = "andando" if movimento.length_squared() else "parado"
        self.animar(dt, estado, nome_direcao(self.direcao), intervalo=60 if self.tempo_ataque > 0 else 120)
        self.tempo_ataque = max(0, self.tempo_ataque - dt)
        self.tempo_dano = max(0, self.tempo_dano - dt)

    def desenhar(self, tela):
        if self.invulneravel <= 0 or int(self.invulneravel / 85) % 2 == 0:
            tela.blit(self.image, self.rect)
        if self.escudo:
            pygame.draw.circle(tela, (103, 191, 223), self.rect.center, 29, 1)
