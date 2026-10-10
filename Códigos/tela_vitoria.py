import pygame
from tela_derrota import TelaDerrota


class TelaVitoria(TelaDerrota):
    TITULO = "VITÓRIA"
    SUBTITULO = "A invasão terminou. Você salvou o reino!"
    COR_TITULO = (228, 207, 113)

    def _desenhar_invasao(self, tela):
        pygame.draw.circle(tela, (212, 192, 129), (400, 205), 43)
        pygame.draw.circle(tela, (73, 68, 66), (400, 205), 57, 1)
        for x, topo in ((222, 207), (292, 230), (472, 230), (542, 207)):
            pygame.draw.rect(tela, (57, 68, 76), (x, topo, 38, 290 - topo))
            for dx in (0, 14, 28):
                pygame.draw.rect(tela, (57, 68, 76), (x + dx, topo - 9, 10, 12))
            pygame.draw.rect(tela, (210, 181, 97), (x + 15, topo + 19, 8, 14))
        pygame.draw.rect(tela, (42, 52, 59), (240, 265, 320, 25))
        pygame.draw.line(tela, (154, 174, 156), (168, 290), (632, 290), 2)
