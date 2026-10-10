"""Inventário de uma tentativa e objetos coletáveis."""

from dataclasses import dataclass
import math
import pygame


@dataclass(frozen=True)
class Item:
    codigo: str
    nome: str
    descricao: str
    cor: tuple
    simbolo: str


ITENS = {
    "triplo": Item("triplo", "Tiro triplo", "Duas flechas menores acompanham o disparo.", (222, 185, 90), "III"),
    "escudo": Item("escudo", "Escudo", "Absorve um golpe e recarrega ao limpar a sala.", (104, 186, 234), "E"),
    "vida_extra": Item("vida_extra", "Vida extra", "Revive com um coração, uma vez nesta tentativa.", (235, 136, 165), "+"),
    "veloz": Item("veloz", "Tiro mais rápido", "Flecha 35% mais rápida na ida e na volta.", (135, 225, 201), ">>"),
    "espada_longa": Item("espada_longa", "Espada alongada", "Aumenta o alcance da espada de 72 para 112.", (194, 194, 231), "L"),
    "distante": Item("distante", "Tiro distante", "Aumenta o alcance da flecha de 380 para 580.", (174, 203, 114), "D"),
    "mental": Item("mental", "Flecha mental", "Na ida, a flecha busca inimigos próximos.", (185, 141, 238), "M"),
    "elemental": Item("elemental", "Espada elemental", "A espada incendeia o alvo por três segundos.", (245, 146, 82), "F"),
}


class Inventario:
    CHANCES = (("triplo", .20), ("escudo", .20), ("vida_extra", .10), ("veloz", .25))
    ADICIONAIS = ("espada_longa", "distante", "mental", "elemental")

    def __init__(self):
        self.adquiridos = []
        self.revive_usado = False

    def possui(self, codigo):
        return codigo in self.adquiridos

    def adquirir(self, codigo):
        if codigo not in ITENS or self.possui(codigo):
            return False
        self.adquiridos.append(codigo)
        return True

    def sortear_recompensas(self, rng):
        # Uma rolagem independente por item e por sala; não se acumulam cópias.
        resultado = [codigo for codigo, chance in self.CHANCES
                     if rng.random() < chance and not self.possui(codigo)]
        adicionais = [codigo for codigo in self.ADICIONAIS if not self.possui(codigo)]
        if rng.random() < .25 and adicionais:
            resultado.append(rng.choice(adicionais))
        return resultado


class Coletavel:
    def __init__(self, codigo, posicao, recursos):
        self.codigo = codigo
        self.posicao = pygame.Vector2(posicao)
        self.rect = pygame.Rect(0, 0, 32, 32)
        self.rect.center = posicao
        self.tempo = 0
        self.fonte = pygame.font.SysFont("arial", 14, bold=True)
        self.imagem = pygame.Surface((36, 36), pygame.SRCALPHA)
        if codigo == "coracao":
            self.imagem.blit(recursos.coracao, (6, 5))
        else:
            item = ITENS[codigo]
            pygame.draw.circle(self.imagem, (25, 29, 40), (18, 18), 17)
            pygame.draw.circle(self.imagem, item.cor, (18, 18), 16, 2)
            texto = self.fonte.render(item.simbolo, True, item.cor)
            self.imagem.blit(texto, texto.get_rect(center=(18, 18)))

    def atualizar(self, dt):
        self.tempo += dt

    def coletar(self, jogador):
        if self.codigo == "coracao":
            if jogador.vida >= jogador.vida_maxima:
                return False
            jogador.curar(1)
            return True
        if not jogador.inventario.adquirir(self.codigo):
            return False
        if self.codigo == "escudo":
            jogador.escudo = 1
        return True

    def desenhar(self, tela, mostrar_nome=False):
        deslocamento = math.sin(self.tempo / 230) * 4
        posicao = (round(self.posicao.x - 18), round(self.posicao.y - 18 + deslocamento))
        pygame.draw.ellipse(tela, (13, 17, 23), (self.posicao.x - 14, self.posicao.y + 16, 28, 8))
        tela.blit(self.imagem, posicao)
        if mostrar_nome and self.codigo in ITENS:
            item = ITENS[self.codigo]
            texto = self.fonte.render(item.nome, True, item.cor)
            tela.blit(texto, texto.get_rect(center=(self.posicao.x, self.posicao.y + 38)))
