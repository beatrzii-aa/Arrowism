import math

import pygame

from configuracoes import LARGURA, ALTURA, TOTAL_SALAS
from menu import Botao, roxo, roxo_hover, vermelho_saturado, vermelho_hover


class TelaDerrota:
    """Exibe o resultado da tentativa e oferece as próximas ações ao jogador."""

    TITULO = "DERROTA"
    SUBTITULO = "O mundo caiu nas mãos dos alienígenas."
    COR_TITULO = (230, 90, 100)

    def __init__(self, pontos, tamanho=(LARGURA, ALTURA), salas=0):
        self.pontos = pontos
        self.salas = salas
        largura, altura = tamanho
        self.deslocamento = ((largura - 800) // 2, (altura - 600) // 2)
        self.cenario = pygame.Surface((800, 600), pygame.SRCALPHA)
        x_botoes = largura // 2 - 160
        y_base = self.deslocamento[1]
        self.inicio = pygame.time.get_ticks()
        self.fonte_titulo = pygame.font.SysFont("arial", 60, bold=True)
        self.fonte_texto = pygame.font.SysFont("arial", 22)
        self.fonte_atalhos = pygame.font.SysFont("arial", 18)
        self.botao_reiniciar = Botao("Tentar novamente", x_botoes, y_base + 354,
                                     320, 56, roxo, roxo_hover)
        self.botao_menu = Botao("Menu inicial", x_botoes, y_base + 422,
                                320, 56, (40, 45, 60), (60, 65, 85))
        self.botao_sair = Botao("Sair", x_botoes, y_base + 490,
                                320, 56, vermelho_saturado, vermelho_hover)
        self.botoes = (
            (self.botao_reiniciar, "jogar"),
            (self.botao_menu, "menu"),
            (self.botao_sair, "sair"),
        )
        self.deslocamento_ovni = 0

    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                return "jogar"
            if evento.key == pygame.K_ESCAPE:
                return "menu"

        for botao, acao in self.botoes:
            if botao.foi_clicado(evento):
                return acao
        return None

    def atualizar(self):
        tempo = (pygame.time.get_ticks() - self.inicio) / 1000
        self.deslocamento_ovni = round(math.sin(tempo * 2) * 5)

    def desenhar(self, tela):
        tela.fill((14, 16, 24))
        self.cenario.fill((0, 0, 0, 0))
        self._desenhar_invasao(self.cenario)
        tela.blit(self.cenario, self.deslocamento)
        self._desenhar_texto(tela, self.TITULO, self.fonte_titulo, self.COR_TITULO, 68)
        self._desenhar_texto(tela, self.SUBTITULO,
                             self.fonte_texto, (185, 184, 200), 120)
        self._desenhar_texto(tela, f"Pontuação: {self.pontos}  ·  Salas concluídas: {self.salas}/{TOTAL_SALAS}",
                             self.fonte_texto, (230, 200, 60), 320)

        for botao, _ in self.botoes:
            botao.desenhar(tela)

        self._desenhar_texto(tela, "Enter: tentar novamente  |  Esc: menu inicial",
                             self.fonte_atalhos, (150, 154, 175), 578)

    def _desenhar_texto(self, tela, texto, fonte, cor, y):
        imagem = fonte.render(texto, True, cor)
        centro = (tela.get_width() // 2, y + self.deslocamento[1])
        tela.blit(imagem, imagem.get_rect(center=centro))

    def _desenhar_invasao(self, tela):
        """Desenha ruínas medievais e um OVNI sem depender de imagens externas."""
        for x, y in ((190, 168), (280, 188), (525, 160), (610, 204), (155, 238), (570, 245)):
            pygame.draw.circle(tela, (110, 115, 145), (x, y), 2)

        # Torres e muralhas sob o domínio alienígena.
        cor_ruinas = (38, 39, 53)
        pygame.draw.rect(tela, cor_ruinas, (205, 246, 390, 44))
        for x, topo in ((205, 208), (268, 231), (495, 224), (557, 198)):
            pygame.draw.rect(tela, cor_ruinas, (x, topo, 38, 290 - topo))
            for dx in (0, 14, 28):
                pygame.draw.rect(tela, cor_ruinas, (x + dx, topo - 9, 10, 12))
            pygame.draw.rect(tela, (105, 58, 68), (x + 14, topo + 17, 9, 14))

        y = 192 + self.deslocamento_ovni
        feixe = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(feixe, (104, 235, 181, 35),
                            [(378, y + 10), (422, y + 10), (474, 289), (326, 289)])
        tela.blit(feixe, (0, 0))
        pygame.draw.ellipse(tela, (77, 137, 127), (373, y - 26, 54, 37))
        pygame.draw.ellipse(tela, (140, 237, 194), (382, y - 21, 36, 23))
        pygame.draw.ellipse(tela, (91, 83, 126), (340, y - 7, 120, 29))
        pygame.draw.ellipse(tela, (153, 143, 192), (340, y - 7, 120, 29), 2)
        for x in (362, 387, 413, 438):
            pygame.draw.circle(tela, (150, 246, 190), (x, y + 10), 3)
        pygame.draw.line(tela, (67, 64, 83), (168, 290), (632, 290), 2)
