"""Flecha única recuperável, espada e projéteis alienígenas."""

import math
import pygame


class Flecha:
    def __init__(self, recursos):
        self.imagem_base = recursos.flechas[(1, 0)]
        self.reiniciar()

    def reiniciar(self):
        self.estado = "pronta"
        self.posicao = pygame.Vector2()
        self.direcao = pygame.Vector2(0, -1)
        self.distancia = 0
        self.atingidos = [set(), set(), set()]
        self.tripla = False

    def disparar(self, jogador, direcao):
        direcao = pygame.Vector2(direcao)
        if self.estado != "pronta" or not direcao.length_squared():
            return False
        self.estado = "voando"
        self.posicao = jogador.posicao.copy()
        self.direcao = direcao.normalize()
        self.distancia = 0
        self.atingidos = [set(), set(), set()]
        self.tripla = jogador.inventario.possui("triplo")
        jogador.atacar(self.direcao)
        return True

    def chamar(self):
        if self.estado in ("voando", "parada"):
            self.estado = "voltando"
            self.atingidos = [set(), set(), set()]
            return True
        return False

    def _atingir(self, inicio, fim, inimigos, registro):
        for inimigo in inimigos:
            if inimigo.morrendo or inimigo in registro:
                continue
            if inimigo.hitbox.inflate(6, 6).clipline(inicio, fim):
                inimigo.receber_dano(1)
                registro.add(inimigo)

    def atualizar(self, dt, jogador, inimigos, limites):
        if self.estado in ("pronta", "parada"):
            return
        inicio = self.posicao.copy()
        velocidade = (760 if self.estado == "voltando" else 600)
        if jogador.inventario.possui("veloz"):
            velocidade *= 1.35
        passo = velocidade * dt / 1000
        recolhida = False
        if self.estado == "voltando":
            diferenca = jogador.posicao - self.posicao
            recolhida = diferenca.length() <= passo + 12
            if diferenca.length_squared():
                self.direcao = diferenca.normalize()
            destino = jogador.posicao.copy() if recolhida else self.posicao + self.direcao * passo
        else:
            if jogador.inventario.possui("mental"):
                alvos = [i for i in inimigos if not i.morrendo and i not in self.atingidos[0]
                         and (i.posicao - self.posicao).length_squared() < 240 ** 2]
                if alvos:
                    alvo = min(alvos, key=lambda i: (i.posicao - self.posicao).length_squared())
                    vetor = alvo.posicao - self.posicao
                    if vetor.length_squared():
                        curva = self.direcao.lerp(vetor.normalize(), min(1, dt / 180))
                        if curva.length_squared():
                            self.direcao = curva.normalize()
            alcance = 580 if jogador.inventario.possui("distante") else 380
            passo = min(passo, alcance - self.distancia)
            destino = self.posicao + self.direcao * passo
            destino.x = max(limites.left + 8, min(limites.right - 8, destino.x))
            destino.y = max(limites.top + 8, min(limites.bottom - 8, destino.y))
            self.distancia += (destino - self.posicao).length()
        self._atingir(inicio, destino, inimigos, self.atingidos[0])
        if self.tripla:
            perpendicular = pygame.Vector2(-self.direcao.y, self.direcao.x) * 22
            for indice, sinal in ((1, -1), (2, 1)):
                self._atingir(inicio + perpendicular * sinal, destino + perpendicular * sinal,
                              inimigos, self.atingidos[indice])
        self.posicao = destino
        if recolhida:
            self.reiniciar()
        elif self.estado == "voando":
            na_borda = (destino.x in (limites.left + 8, limites.right - 8)
                        or destino.y in (limites.top + 8, limites.bottom - 8))
            if self.distancia >= alcance - .01 or na_borda:
                self.estado = "parada"
                self.tripla = False

    def desenhar(self, tela):
        if self.estado == "pronta":
            return
        angulo = -math.degrees(math.atan2(self.direcao.y, self.direcao.x))
        imagem = pygame.transform.rotate(self.imagem_base, angulo)
        if self.estado in ("parada", "voltando"):
            pygame.draw.circle(tela, (95, 145, 137), self.posicao, 17, 1)
        tela.blit(imagem, imagem.get_rect(center=self.posicao))
        if self.tripla:
            pequena = pygame.transform.scale(imagem, (max(1, imagem.get_width() * 2 // 3),
                                                     max(1, imagem.get_height() * 2 // 3)))
            perpendicular = pygame.Vector2(-self.direcao.y, self.direcao.x) * 22
            for sinal in (-1, 1):
                tela.blit(pequena, pequena.get_rect(center=self.posicao + perpendicular * sinal))


class Espada:
    def __init__(self):
        self.tempo = 0
        self.recarga = 0
        self.direcao = pygame.Vector2(0, -1)
        self.atingidos = set()

    def atacar(self, jogador, direcao=None):
        if self.recarga > 0 or jogador.vida <= 0:
            return False
        vetor = pygame.Vector2(direcao) if direcao is not None else jogador.direcao.copy()
        self.direcao = vetor.normalize() if vetor.length_squared() else jogador.direcao.copy()
        self.tempo = 180
        self.recarga = 430
        self.atingidos.clear()
        jogador.atacar(self.direcao)
        return True

    def atualizar(self, dt, jogador, inimigos):
        self.recarga = max(0, self.recarga - dt)
        if self.tempo <= 0:
            return
        alcance = 112 if jogador.inventario.possui("espada_longa") else 72
        for inimigo in inimigos:
            if inimigo.morrendo or inimigo in self.atingidos:
                continue
            vetor = inimigo.posicao - jogador.posicao
            if vetor.length() <= alcance + inimigo.hitbox.width / 3:
                if not vetor.length_squared() or vetor.normalize().dot(self.direcao) >= .20:
                    inimigo.receber_dano(2, elemental=jogador.inventario.possui("elemental"))
                    self.atingidos.add(inimigo)
        self.tempo = max(0, self.tempo - dt)

    def desenhar(self, tela, jogador):
        if self.tempo <= 0:
            return
        alcance = 112 if jogador.inventario.possui("espada_longa") else 72
        cor = (250, 169, 92) if jogador.inventario.possui("elemental") else (218, 227, 211)
        progresso = 1 - self.tempo / 180
        angulo = -70 + 140 * progresso
        ponta = jogador.posicao + self.direcao.rotate(angulo) * alcance
        base = jogador.posicao + self.direcao.rotate(angulo) * 20
        pygame.draw.line(tela, (98, 144, 149), base, ponta, 9)
        pygame.draw.line(tela, cor, base, ponta, 4)
        for deslocamento in (15, 30):
            rastro = jogador.posicao + self.direcao.rotate(angulo - deslocamento) * alcance
            pygame.draw.line(tela, (79, 114, 122), rastro, ponta, 1)


class ProjetilAlien(pygame.sprite.Sprite):
    def __init__(self, posicao, direcao, velocidade=200, dano=1, cor=(99, 239, 194)):
        super().__init__()
        self.posicao = pygame.Vector2(posicao)
        vetor = pygame.Vector2(direcao)
        self.velocidade = vetor.normalize() * velocidade if vetor.length_squared() else pygame.Vector2(0, 1)
        self.dano = dano
        self.image = pygame.Surface((18, 18), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (*cor, 55), (9, 9), 9)
        pygame.draw.circle(self.image, cor, (9, 9), 5)
        pygame.draw.circle(self.image, (222, 255, 237), (8, 8), 2)
        self.rect = self.image.get_rect(center=posicao)
        self.anterior = self.posicao.copy()

    def atualizar(self, dt, limites):
        self.anterior = self.posicao.copy()
        self.posicao += self.velocidade * dt / 1000
        self.rect.center = self.posicao
        if not limites.inflate(40, 40).collidepoint(self.posicao):
            self.kill()

    def atingiu(self, jogador):
        return bool(jogador.hitbox.inflate(8, 8).clipline(self.anterior, self.posicao))
