"""Variações de alienígenas e o chefe da invasão."""

import math
import pygame
from armas import ProjetilAlien
from entidades import EntidadeAnimada, nome_direcao


class Alien(EntidadeAnimada):
    nome = "Batedor"
    tamanho = 56
    brilho = (0, 0, 0)

    def __init__(self, posicao, nivel, recursos):
        super().__init__(posicao, recursos.alien_variante(self.tamanho, self.brilho))
        self.vida_maxima = 1 + (nivel - 1) // 2
        self.vida = self.vida_maxima
        self.velocidade = 66 + nivel * 9
        self.dano = 1
        self.nivel = nivel
        self.morrendo = False
        self.recompensado = False
        self.valor = 10
        self.direcao = pygame.Vector2(0, 1)
        self.tempo = 0
        self.atingido = 0
        self.queimando = 0
        self.tick_fogo = 0
        self.tempo_ataque = 0

    def receber_dano(self, dano, elemental=False):
        if self.morrendo:
            return False
        self.vida = max(0, self.vida - dano)
        self.atingido = 140
        if elemental:
            if self.queimando <= 0:
                self.tick_fogo = 0
            self.queimando = 3000
        if self.vida <= 0:
            self.morrendo = True
        return True

    def comportamento(self, dt, jogador, limites, projeteis):
        vetor = jogador.posicao - self.posicao
        if vetor.length_squared():
            self.direcao = vetor.normalize()
            self.mover(self.direcao * self.velocidade * dt / 1000, limites)

    def atualizar(self, dt, jogador, limites, projeteis):
        self.tempo += dt
        if self.queimando > 0 and not self.morrendo:
            self.tick_fogo += min(dt, self.queimando)
            self.queimando = max(0, self.queimando - dt)
            while self.tick_fogo >= 1000 and not self.morrendo:
                self.tick_fogo -= 1000
                self.receber_dano(1)
        if self.morrendo:
            self.animar(dt, "morrendo", nome_direcao(self.direcao), repetir=False)
            if self.animacao.finalizada:
                self.kill()
            return
        self.atingido = max(0, self.atingido - dt)
        self.tempo_ataque = max(0, self.tempo_ataque - dt)
        self.comportamento(dt, jogador, limites, projeteis)
        estado = "atirando" if self.tempo_ataque > 0 else "andando"
        self.animar(dt, estado, nome_direcao(self.direcao))

    def desenhar(self, tela):
        pygame.draw.ellipse(tela, (12, 17, 21), (self.rect.centerx - self.rect.width / 4,
                            self.rect.bottom - 13, self.rect.width / 2, 10))
        tela.blit(self.image, self.rect)
        if not self.morrendo and self.atingido:
            pygame.draw.circle(tela, (234, 207, 153), self.rect.center, self.rect.width // 3, 1)
        if self.queimando > 0 and not self.morrendo:
            for x in (-12, 0, 12):
                altura = 10 + int(math.sin(self.tempo / 70 + x) * 5)
                pygame.draw.line(tela, (239, 150, 66),
                                 (self.rect.centerx + x, self.rect.bottom - 8),
                                 (self.rect.centerx + x, self.rect.bottom - 8 - altura), 3)
        if self.vida_maxima > 1 and not self.morrendo and not isinstance(self, Chefe):
            barra = pygame.Rect(self.rect.centerx - 18, self.rect.top - 3, 36, 3)
            pygame.draw.rect(tela, (63, 45, 55), barra)
            pygame.draw.rect(tela, (110, 209, 170), (barra.x, barra.y, 36 * self.vida / self.vida_maxima, 3))


class AlienAtirador(Alien):
    nome = "Sentinela"
    brilho = (35, 0, 40)

    def __init__(self, posicao, nivel, recursos):
        super().__init__(posicao, nivel, recursos)
        self.vida_maxima += 1
        self.vida = self.vida_maxima
        self.recarga = 1200
        self.valor = 15

    def comportamento(self, dt, jogador, limites, projeteis):
        vetor = jogador.posicao - self.posicao
        distancia = vetor.length()
        if distancia:
            self.direcao = vetor.normalize()
            movimento = self.direcao if distancia > 290 else -self.direcao if distancia < 170 else self.direcao.rotate(90) * .4
            self.mover(movimento * self.velocidade * .65 * dt / 1000, limites)
        self.recarga -= dt
        if self.recarga < 350:
            self.tempo_ataque = 350
        if self.recarga <= 0:
            projeteis.add(ProjetilAlien(self.posicao, self.direcao, 175 + 12 * self.nivel))
            self.recarga = max(1050, 1800 - self.nivel * 90)


class AlienCorredor(Alien):
    nome = "Caçador"
    brilho = (42, 24, 0)

    def __init__(self, posicao, nivel, recursos):
        super().__init__(posicao, nivel, recursos)
        self.recarga = 1600
        self.arrancada = 0
        self.aviso = 0
        self.valor = 15

    def comportamento(self, dt, jogador, limites, projeteis):
        if self.arrancada > 0:
            self.mover(self.direcao * 360 * dt / 1000, limites)
            self.arrancada -= dt
        elif self.aviso > 0:
            self.aviso -= dt
            if self.aviso <= 0:
                vetor = jogador.posicao - self.posicao
                if vetor.length_squared():
                    self.direcao = vetor.normalize()
                self.arrancada = 360
        else:
            super().comportamento(dt, jogador, limites, projeteis)
            self.recarga -= dt
            if self.recarga <= 0:
                self.aviso = 550
                self.recarga = 2600

    def desenhar(self, tela):
        super().desenhar(tela)
        if self.aviso > 0 and not self.morrendo:
            pygame.draw.circle(tela, (242, 172, 88), self.rect.center, 32, 2)


class AlienBruto(Alien):
    nome = "Guardião"
    tamanho = 84
    brilho = (45, 4, 10)

    def __init__(self, posicao, nivel, recursos):
        super().__init__(posicao, nivel, recursos)
        self.vida_maxima += 3
        self.vida = self.vida_maxima
        self.velocidade *= .65
        self.dano = 2
        self.valor = 25


class Chefe(Alien):
    nome = "ARCONTE DO VAZIO"
    tamanho = 156
    brilho = (55, 0, 38)

    def __init__(self, posicao, nivel, recursos):
        super().__init__(posicao, nivel, recursos)
        self.vida_maxima = 52
        self.vida = self.vida_maxima
        self.velocidade = 48
        self.dano = 2
        self.valor = 500
        self.fase = 1
        self.recarga = 1600
        self.aviso = 0
        self.padrao = 0

    def comportamento(self, dt, jogador, limites, projeteis):
        self.fase = 2 if self.vida <= self.vida_maxima / 2 else 1
        vetor = jogador.posicao - self.posicao
        if vetor.length_squared():
            self.direcao = vetor.normalize()
        self.recarga -= dt
        self.aviso = max(0, 650 - self.recarga) if self.recarga < 650 else 0
        if self.aviso:
            self.tempo_ataque = 250
        else:
            self.mover(self.direcao * self.velocidade * self.fase * dt / 1000, limites)
        if self.recarga <= 0:
            quantidade = 8 if self.fase == 1 else 12
            for indice in range(quantidade):
                angulo = indice * 360 / quantidade + self.padrao * 17
                projeteis.add(ProjetilAlien(self.posicao, pygame.Vector2(1, 0).rotate(angulo),
                                          155 + self.fase * 25, cor=(211, 130, 230)))
            if self.fase == 2:
                for angulo in (-12, 0, 12):
                    projeteis.add(ProjetilAlien(self.posicao, self.direcao.rotate(angulo), 235))
            self.padrao += 1
            self.recarga = 2400 if self.fase == 1 else 1850

    def desenhar(self, tela):
        if not self.morrendo:
            raio = 65 + int(math.sin(self.tempo / 160) * 4)
            pygame.draw.circle(tela, (98, 62, 119), self.rect.center, raio, 2)
            if self.aviso:
                pygame.draw.circle(tela, (229, 131, 208), self.rect.center, raio + 12, 2)
        super().desenhar(tela)


TIPOS_INIMIGOS = {"batedor": Alien, "sentinela": AlienAtirador,
                  "cacador": AlienCorredor, "bruto": AlienBruto, "chefe": Chefe}
