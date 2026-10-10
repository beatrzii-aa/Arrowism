"""Cenário, HUD, OVNI e transições desenhados pelo Pygame."""

import math
import random
import pygame
from configuracoes import TOTAL_SALAS
from itens import ITENS


class Ovni:
    def desenhar(self, tela, centro, escala=1):
        x, y = centro
        def ret(dx, dy, w, h):
            return pygame.Rect(x + dx * escala, y + dy * escala, w * escala, h * escala)
        pygame.draw.ellipse(tela, (105, 209, 174), ret(-19, -24, 38, 29))
        pygame.draw.ellipse(tela, (79, 69, 111), ret(-48, -8, 96, 25))
        pygame.draw.ellipse(tela, (162, 141, 190), ret(-48, -8, 96, 25), 2)
        for dx in (-30, -10, 10, 30):
            pygame.draw.circle(tela, (173, 248, 195), (int(x + dx * escala), int(y + 7 * escala)), max(2, int(3 * escala)))


class CenarioSala:
    def __init__(self, tamanho):
        self.tamanho = tamanho
        self.limites = pygame.Rect(48, 134, tamanho[0] - 96, tamanho[1] - 202)
        self.fundo = pygame.Surface(tamanho)
        self.fonte = pygame.font.SysFont("arial", 17)
        self.preparar(1)

    def preparar(self, numero):
        rng = random.Random(numero * 83)
        self.fundo.fill((12, 17, 23))
        pygame.draw.rect(self.fundo, (51, 54, 63), self.limites.inflate(26, 26), border_radius=9)
        for y in range(self.limites.top, self.limites.bottom, 44):
            for x in range(self.limites.left, self.limites.right, 64):
                tom = rng.randint(-3, 5)
                cor = (26 + tom, 33 + tom, 37 + tom)
                bloco = pygame.Rect(x + 1, y + 1, min(62, self.limites.right - x - 1),
                                    min(42, self.limites.bottom - y - 1))
                pygame.draw.rect(self.fundo, cor, bloco)
                if rng.random() < .18:
                    pygame.draw.line(self.fundo, (20, 28, 31), bloco.topleft, bloco.center, 1)
        pygame.draw.rect(self.fundo, (78, 96, 101), self.limites, 2)
        for x in (self.limites.left + 12, self.limites.right - 12):
            for y in (self.limites.top + 22, self.limites.bottom - 22):
                pygame.draw.rect(self.fundo, (57, 64, 71), (x - 8, y - 10, 16, 20), border_radius=3)
                pygame.draw.line(self.fundo, (118, 185, 160), (x, y - 6), (x, y + 6), 2)
        centro = self.limites.center
        pygame.draw.circle(self.fundo, (35, 46, 49), centro, 86, 2)
        pygame.draw.circle(self.fundo, (35, 46, 49), centro, 71, 1)
        for angulo in range(0, 360, 60):
            inicio = pygame.Vector2(centro) + pygame.Vector2(74, 0).rotate(angulo)
            fim = pygame.Vector2(centro) + pygame.Vector2(84, 0).rotate(angulo)
            pygame.draw.line(self.fundo, (55, 76, 75), inicio, fim, 2)

    @property
    def portal_saida(self):
        return pygame.Vector2(self.limites.centerx, self.limites.top + 42)

    def desenhar(self, tela, sala, tempo):
        tela.blit(self.fundo, (0, 0))
        if sala.concluida and sala.numero < TOTAL_SALAS:
            centro = self.portal_saida
            pygame.draw.circle(tela, (57, 113, 109), centro, 34, 3)
            pygame.draw.circle(tela, (126, 226, 181), centro, 23 + int(math.sin(tempo / 200) * 3), 2)
            texto = self.fonte.render("E · próxima sala", True, (210, 230, 207))
            tela.blit(texto, texto.get_rect(center=(centro.x, centro.y + 52)))


class HUD:
    def __init__(self, tamanho, recursos):
        self.tamanho = tamanho
        self.recursos = recursos
        self.fonte = pygame.font.SysFont("arial", 21, bold=True)
        self.pequena = pygame.font.SysFont("arial", 16)
        self.grande = pygame.font.SysFont("arial", 34, bold=True)

    def desenhar(self, tela, jogo):
        jogador = jogo.jogador
        largura, altura = self.tamanho
        pygame.draw.rect(tela, (15, 21, 28), (0, 0, largura, 113))
        for indice in range(jogador.vida_maxima):
            imagem = self.recursos.coracao if indice < jogador.vida else self.recursos.coracao_vazio
            tela.blit(pygame.transform.scale(imagem, (28, 30)), (28 + indice * 34, 19))
        if jogador.inventario.possui("escudo"):
            cor = (122, 204, 237) if jogador.escudo else (58, 71, 84)
            pygame.draw.polygon(tela, cor, [(141, 22), (161, 22), (159, 39), (151, 47), (143, 39)], 2)
        textos = ((f"SALA {jogo.sala.numero}/{TOTAL_SALAS}  ·  {jogo.sala.nome}", (190, 18)),
                  (f"{jogo.pontos:04d} pontos", (largura - 166, 18)))
        for texto, posicao in textos:
            tela.blit(self.fonte.render(texto, True, (211, 216, 210)), posicao)
        info = f"Concluídas: {jogo.salas_concluidas}  |  Onda {max(1, jogo.sala.onda)}/{jogo.sala.total_ondas}"
        if jogo.sala.concluida:
            info = "Sala limpa — recolha os itens e vá ao portal"
        tela.blit(self.pequena.render(info, True, (130, 168, 166)), (190, 47))
        x = 28
        for codigo in jogador.inventario.adquiridos:
            item = ITENS[codigo]
            nome = item.nome.replace("Tiro mais rápido", "Flecha veloz").replace("Espada alongada", "Espada longa")
            if codigo == "vida_extra" and jogador.inventario.revive_usado:
                nome = "Vida extra usada"
            texto = self.pequena.render(nome, True, item.cor)
            largura_item = texto.get_width() + 16
            pygame.draw.rect(tela, (28, 34, 45), (x, 79, largura_item, 25), border_radius=4)
            tela.blit(texto, (x + 8, 81))
            x += largura_item + 6
        if not jogador.inventario.adquiridos:
            tela.blit(self.pequena.render("Uma espada. Uma flecha. Uma última chance.", True, (109, 122, 134)), (28, 82))
        estados = {"pronta": "Flecha pronta", "voando": "Flecha em voo · Espaço: chamar",
                   "parada": "Flecha no chão · Espaço: chamar", "voltando": "Flecha retornando"}
        tela.blit(self.pequena.render(estados[jogo.flecha.estado], True, (197, 201, 166)), (48, altura - 52))
        controles = "WASD mover  ·  Setas disparar  ·  J espada  ·  E avançar  ·  Esc pausa  ·  M som"
        texto = self.pequena.render(controles, True, (138, 151, 163))
        tela.blit(texto, texto.get_rect(center=(largura // 2, altura - 20)))
        if jogo.mensagem_tempo > 0:
            texto = self.pequena.render(jogo.mensagem, True, (231, 212, 147))
            fundo = texto.get_rect(center=(largura // 2, altura - 82)).inflate(26, 16)
            pygame.draw.rect(tela, (16, 23, 30), fundo, border_radius=6)
            tela.blit(texto, texto.get_rect(center=fundo.center))
        chefe = next((i for i in jogo.inimigos if i.nome == "ARCONTE DO VAZIO" and not i.morrendo), None)
        if chefe:
            barra = pygame.Rect(largura // 2 - 200, 147, 400, 12)
            pygame.draw.rect(tela, (48, 34, 55), barra)
            pygame.draw.rect(tela, (194, 103, 183), (barra.x, barra.y, 400 * chefe.vida / chefe.vida_maxima, 12))
            titulo = self.pequena.render(f"{chefe.nome} · Fase {chefe.fase}", True, (221, 186, 218))
            tela.blit(titulo, titulo.get_rect(center=(largura // 2, 176)))
        if jogo.pausado:
            sombra = pygame.Surface(self.tamanho, pygame.SRCALPHA)
            sombra.fill((7, 11, 19, 205))
            tela.blit(sombra, (0, 0))
            for texto, y, fonte in (("PAUSADO", altura // 2 - 55, self.grande),
                                    ("Esc: continuar  ·  R: reiniciar  ·  Q: menu", altura // 2 + 10, self.fonte),
                                    ("Mouse: esquerdo usa espada; direito dispara", altura // 2 + 55, self.pequena)):
                img = fonte.render(texto, True, (218, 219, 210))
                tela.blit(img, img.get_rect(center=(largura // 2, y)))


class Transicao:
    def __init__(self, tamanho, texto, ao_meio=None):
        self.tamanho = tamanho
        self.texto = texto
        self.ao_meio = ao_meio
        self.tempo = 0
        self.duracao = 1500
        self.trocou = False
        self.ovni = Ovni()
        self.fonte = pygame.font.SysFont("arial", 24, bold=True)

    @property
    def finalizada(self):
        return self.tempo >= self.duracao

    def atualizar(self, dt):
        self.tempo += dt
        if self.tempo >= self.duracao / 2 and not self.trocou:
            self.trocou = True
            if self.ao_meio:
                self.ao_meio()

    def desenhar(self, tela):
        t = min(1, self.tempo / self.duracao)
        opacidade = int(255 * min(1, min(t, 1 - t) * 3))
        sombra = pygame.Surface(self.tamanho, pygame.SRCALPHA)
        sombra.fill((5, 9, 17, opacidade))
        tela.blit(sombra, (0, 0))
        self.ovni.desenhar(tela, (-70 + t * (self.tamanho[0] + 140), self.tamanho[1] // 2), .7)
        if .22 < t < .78:
            texto = self.fonte.render(self.texto, True, (189, 219, 204))
            tela.blit(texto, texto.get_rect(center=(self.tamanho[0] // 2, self.tamanho[1] // 2 + 65)))
