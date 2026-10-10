"""Recortes e animações dos arquivos originais da pasta Sprites."""

import base64
import io
import json
from collections import deque
from pathlib import Path

import pygame


DIRECOES = {(0, -1): "cima", (0, 1): "baixo", (-1, 0): "esquerda", (1, 0): "direita"}


class FolhaSprites:
    """Recorta a folha em JPG e remove o fundo conectado às bordas."""

    def __init__(self, caminho):
        self.imagem = pygame.image.load(str(caminho)).convert_alpha()

    def recortar(self, regiao):
        imagem = self.imagem.subsurface(pygame.Rect(regiao)).copy()
        largura, altura = imagem.get_size()
        bordas = [(x, y) for x in range(largura) for y in (0, altura - 1)]
        bordas += [(x, y) for y in range(altura) for x in (0, largura - 1)]
        fila = deque(bordas)
        visitados = set()
        while fila:
            x, y = fila.popleft()
            if (x, y) in visitados or not (0 <= x < largura and 0 <= y < altura):
                continue
            visitados.add((x, y))
            r, g, b, _ = imagem.get_at((x, y))
            # O fundo da folha é azul escuro. O preenchimento pelas bordas
            # preserva os detalhes escuros que estão dentro dos personagens.
            if r <= 42 and g <= 52 and b <= 66 and r <= g + 4 and r <= b:
                imagem.set_at((x, y), (0, 0, 0, 0))
                fila.extend(((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))
        return imagem

    def sequencia(self, x, y, passo=48, largura=48, altura=54):
        quadros = []
        for indice in range(4):
            recorte = self.recortar((x + indice * passo, y, largura, altura))
            # A mesma tela e a mesma linha dos pés evitam mudanças de tamanho
            # e de posição quando a animação troca de quadro.
            quadro = pygame.Surface((56, 56), pygame.SRCALPHA)
            quadro.blit(recorte, ((56 - largura) // 2, 56 - altura))
            quadros.append(quadro)
        return tuple(quadros)


class ArquivoPixil:
    """Lê os PNGs transparentes guardados nas camadas de um projeto Pixilart."""

    def __init__(self, caminho):
        with caminho.open(encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        self.quadros = []
        self.duracoes = []
        for quadro in dados["frames"]:
            imagem = pygame.Surface((dados["width"], dados["height"]), pygame.SRCALPHA)
            for camada in quadro["layers"]:
                png = base64.b64decode(camada["src"].split(",", 1)[1])
                parte = pygame.image.load(io.BytesIO(png)).convert_alpha()
                parte.set_alpha(round(float(camada.get("opacity", 1)) * 255))
                imagem.blit(parte, (0, 0))
            self.quadros.append(imagem)
            self.duracoes.append(quadro["speed"])


class RecursosSprites:
    """Carrega as imagens uma vez e compartilha os quadros entre as entidades."""

    def __init__(self):
        pasta = Path(__file__).resolve().parent.parent / "Sprites"
        folha = FolhaSprites(pasta / "Personagem e Alien.jpg")
        self.jogador = {}
        self.alien = {}
        direcoes = tuple(DIRECOES.values())

        for estado, x in (("parado", 259), ("andando", 461),
                          ("atirando", 668), ("andando_atirando", 872)):
            self.jogador[estado] = {
                direcao: folha.sequencia(x, y)
                for direcao, y in zip(direcoes, (110, 171, 231, 291))
            }
        for estado, x, passo in (("pegar_item", 176, 49), ("abrir_bau", 396, 50),
                                 ("levar_dano", 607, 50), ("morrer", 817, 50)):
            quadros = folha.sequencia(x, 410, passo=passo)
            self.jogador[estado] = dict.fromkeys(direcoes, quadros)

        for estado, x, passo, largura in (("parado", 300, 40, 40),
                                          ("andando", 474, 48, 46),
                                          ("atirando", 671, 48, 48),
                                          ("morrendo", 878, 48, 48)):
            self.alien[estado] = {
                direcao: folha.sequencia(x, y, passo=passo, largura=largura, altura=50)
                for direcao, y in zip(direcoes, (569, 625, 683, 741))
            }

        # O projeto do arco já contém uma flecha horizontal com transparência.
        arco = ArquivoPixil(pasta / "ARCO E FLECHA.pixil")
        flecha = arco.quadros[0].subsurface((75, 62, 15, 3)).copy()
        flecha = pygame.transform.scale(flecha, (30, 6))
        self.flechas = {
            (1, 0): flecha,
            (-1, 0): pygame.transform.flip(flecha, True, False),
            (0, -1): pygame.transform.rotate(flecha, 90),
            (0, 1): pygame.transform.rotate(flecha, -90),
        }
        self.coracao = folha.recortar((1091, 91, 23, 25))
        self.coracao_vazio = self.coracao.copy()
        self.coracao_vazio.fill((65, 65, 80, 255), special_flags=pygame.BLEND_RGBA_MULT)
        self.variantes = {}

    def alien_variante(self, tamanho=56, brilho=(0, 0, 0)):
        chave = (tamanho, brilho)
        if chave not in self.variantes:
            sequencias = {}
            for estado, direcoes in self.alien.items():
                sequencias[estado] = {}
                for direcao, quadros in direcoes.items():
                    novos = []
                    for quadro in quadros:
                        imagem = pygame.transform.scale(quadro, (tamanho, tamanho))
                        imagem.fill((*brilho, 0), special_flags=pygame.BLEND_RGBA_ADD)
                        novos.append(imagem)
                    sequencias[estado][direcao] = tuple(novos)
            self.variantes[chave] = sequencias
        return self.variantes[chave]


class Animacao:
    """Controla o tempo de uma entidade; os quadros compartilhados são imutáveis."""

    def __init__(self, sequencias, estado="parado", direcao="baixo"):
        self.sequencias = sequencias
        self.estado = None
        self.direcao = None
        self.selecionar(estado, direcao)

    def selecionar(self, estado, direcao, repetir=True, intervalo=120):
        if (estado, direcao) == (self.estado, self.direcao):
            return
        self.estado = estado
        self.direcao = direcao
        self.quadros = self.sequencias[estado][direcao]
        self.repetir = repetir
        self.intervalo = intervalo
        self.indice = 0
        self.tempo = 0
        self.finalizada = False

    @property
    def imagem(self):
        return self.quadros[self.indice]

    def atualizar(self, dt):
        self.tempo += dt
        while self.tempo >= self.intervalo and not self.finalizada:
            self.tempo -= self.intervalo
            if self.indice < len(self.quadros) - 1:
                self.indice += 1
            elif self.repetir:
                self.indice = 0
            else:
                self.finalizada = True
