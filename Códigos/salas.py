"""Ondas finitas, avisos de surgimento e progressão da campanha."""

import pygame
from configuracoes import TOTAL_SALAS


class PortalInvocacao:
    def __init__(self, tipo, posicao, espera):
        self.tipo = tipo
        self.posicao = posicao
        self.tempo = espera

    def desenhar(self, tela):
        if self.tempo > 700:
            return
        raio = 14 + int((700 - self.tempo) / 35) % 17
        pygame.draw.circle(tela, (88, 111, 137), self.posicao, raio, 1)
        pygame.draw.circle(tela, (131, 224, 198), self.posicao, 10, 2)


class Sala:
    NOMES = ("O pátio esquecido", "Muralhas em silêncio", "O jardim corrompido",
             "A fortaleza ocupada", "O último bastião", "O coração da invasão")

    def __init__(self, numero, limites, rng):
        self.numero = numero
        self.nome = self.NOMES[numero - 1]
        self.limites = limites
        self.rng = rng
        self.onda = 0
        self.total_ondas = 1 if numero == TOTAL_SALAS else 2
        self.pendentes = []
        self.espera = 700
        self.concluida = False

    def _posicao(self, jogador):
        area = self.limites.inflate(-100, -100)
        candidatos = [(area.left, area.top), (area.right, area.top),
                      (area.left, area.bottom), (area.right, area.bottom),
                      (area.centerx, area.top), (area.left, area.centery), (area.right, area.centery)]
        seguros = [p for p in candidatos if (pygame.Vector2(p) - jogador.posicao).length() > 190]
        x, y = self.rng.choice(seguros or candidatos)
        return (x + self.rng.randint(-15, 15), y + self.rng.randint(-15, 15))

    def iniciar_onda(self, jogador):
        self.onda += 1
        if self.numero == TOTAL_SALAS:
            posicao = (self.limites.centerx, self.limites.top + 115)
            self.pendentes = [PortalInvocacao("chefe", posicao, 1000)]
            return
        tipos = ["batedor"]
        if self.numero >= 2:
            tipos.append("sentinela")
        if self.numero >= 3:
            tipos.append("cacador")
        if self.numero >= 4:
            tipos.append("bruto")
        self.pendentes = [PortalInvocacao(tipos[indice % len(tipos)], self._posicao(jogador),
                                          650 + indice * 230)
                          for indice in range(self.numero + 2)]

    def atualizar(self, dt, vivos, jogador):
        if self.concluida:
            return []
        novos = []
        for portal in self.pendentes[:]:
            portal.tempo -= dt
            if portal.tempo <= 0:
                novos.append((portal.tipo, portal.posicao))
                self.pendentes.remove(portal)
        if not vivos and not self.pendentes and not novos:
            self.espera -= dt
            if self.espera <= 0:
                if self.onda < self.total_ondas:
                    self.iniciar_onda(jogador)
                    self.espera = 1200
                else:
                    self.concluida = True
        return novos
