"""Música e efeitos originais sintetizados localmente, sem arquivos externos."""

from array import array
import math
import random
import pygame


class Audio:
    def __init__(self, ativo=True):
        self.disponivel = ativo and pygame.mixer.get_init() is not None
        self.mudo = False
        self.contexto = None
        self.musicas = {}
        self.efeitos = {}
        if self.disponivel:
            self.taxa, formato, self.canais = pygame.mixer.get_init()
            self.disponivel = formato == -16
        if self.disponivel:
            pygame.mixer.set_num_channels(12)
            pygame.mixer.set_reserved(1)
            self.canal = pygame.mixer.Channel(0)
            for nome, freq, duracao in (("flecha", 740, .10), ("espada", 190, .13),
                                       ("impacto", 95, .12), ("coleta", 880, .22),
                                       ("retorno", 520, .13), ("sala", 660, .40),
                                       ("dano", 70, .25), ("vitoria", 990, .6)):
                self.efeitos[nome] = self._efeito(freq, duracao)

    def _som(self, amostras):
        pcm = array("h")
        for valor in amostras:
            amostra = max(-32767, min(32767, int(valor * 32767)))
            pcm.extend([amostra] * self.canais)
        return pygame.mixer.Sound(buffer=pcm.tobytes())

    def _efeito(self, frequencia, duracao):
        quantidade = int(self.taxa * duracao)
        return self._som(.20 * (1 - i / quantidade) ** 2
                         * math.sin(2 * math.pi * frequencia * (i / self.taxa)
                                    * (1 + .3 * i / quantidade)) for i in range(quantidade))

    def _musica(self, contexto):
        bpm = {"calma": 92, "combate": 132, "chefe": 152}[contexto]
        batida = 60 / bpm
        duracao = batida * 16
        notas = (220, 261.63, 329.63, 293.66, 196, 246.94, 293.66, 261.63)
        rng = random.Random(17)
        amostras = []
        for i in range(int(self.taxa * duracao)):
            t = i / self.taxa
            indice = int(t / (batida / 2))
            fase = t % (batida / 2)
            frequencia = notas[indice % len(notas)]
            envelope = min(1, fase * 60) * math.exp(-fase * 8)
            melodia = math.sin(2 * math.pi * frequencia * t) * envelope * .085
            grave = math.sin(2 * math.pi * notas[(indice // 4) % 8] / 4 * t) * .045
            bateria = 0
            if contexto != "calma":
                pulso = t % batida
                bateria = math.sin(2 * math.pi * 60 * pulso) * math.exp(-pulso * 28) * .13
                bateria += rng.uniform(-1, 1) * math.exp(-fase * 90) * .025
            amostras.append(melodia + grave + bateria)
        return self._som(amostras)

    def ambiente(self, contexto):
        if not self.disponivel or contexto == self.contexto:
            return
        if contexto not in self.musicas:
            self.musicas[contexto] = self._musica(contexto)
        self.contexto = contexto
        self.canal.play(self.musicas[contexto], loops=-1, fade_ms=350)
        self.canal.set_volume(0 if self.mudo else .6)

    def tocar(self, nome):
        if self.disponivel and not self.mudo:
            self.efeitos[nome].play()

    def alternar(self):
        self.mudo = not self.mudo
        if self.disponivel:
            self.canal.set_volume(0 if self.mudo else .6)
            if self.mudo:
                for indice in range(1, pygame.mixer.get_num_channels()):
                    pygame.mixer.Channel(indice).stop()
